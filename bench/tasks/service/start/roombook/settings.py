"""Settings for roombook.

Values come from three places; a later one wins:

  1. DEFAULTS below
  2. an ini file: the --config option, else $ROOMBOOK_CONFIG, else ./roombook.ini when it exists
  3. environment variables named ROOMBOOK_<KEY>, e.g. ROOMBOOK_CLOSE_HOUR=19

Every setting is an int except db_path and outbox_dir. Roles of people (desk, admin) are read from the
[people] section of the ini file only; there is no environment form for them on purpose,
so a shell variable cannot make someone an admin.
"""
import configparser
import os

DEFAULTS = {
    "open_hour": 7,
    "close_hour": 20,
    "max_booking_minutes": 240,
    "advance_days": 90,
    "late_cancel_hours": 24,
    "slot_step_minutes": 15,
    "weekend_warning": 1,
    "weekly_quota_hours": 0,
    "db_path": "roombook.sqlite3",
    "outbox_dir": "",
}

# Which ini section holds which key. A key in the wrong section is ignored (with a note).
SECTIONS = {
    "hours": ("open_hour", "close_hour"),
    "policy": ("max_booking_minutes", "advance_days", "late_cancel_hours",
               "slot_step_minutes", "weekend_warning", "weekly_quota_hours"),
    "storage": ("db_path",),
    "notify": ("outbox_dir",),
}

ROLES = ("staff", "desk", "admin")
ENV_PREFIX = "ROOMBOOK_"


class Settings:
    """Resolved settings. Read values as attributes: settings.close_hour."""

    def __init__(self, values, roles, source=None, notes=None):
        self._values = dict(values)
        self.roles = dict(roles)
        self.source = source
        self.notes = list(notes or [])

    def __getattr__(self, name):
        try:
            return self.__dict__["_values"][name]
        except KeyError:
            raise AttributeError(name) from None

    def get(self, name, default=None):
        return self._values.get(name, default)

    def role_of(self, person):
        return self.roles.get(person, "staff")

    def can_manage(self, actor, owner):
        """True when actor may change a booking owned by owner."""
        return actor == owner or self.role_of(actor) in ("desk", "admin")

    def is_admin(self, person):
        return self.role_of(person) == "admin"

    def open_minutes_per_day(self):
        return (self.close_hour - self.open_hour) * 60

    def as_dict(self):
        return dict(self._values)


def _coerce(key, raw):
    if key in ("db_path", "outbox_dir"):
        return str(raw)
    try:
        return int(str(raw).strip())
    except ValueError:
        raise ValueError(f"setting {key} must be a whole number, got {raw!r}") from None


def _ini_path(explicit):
    if explicit:
        return explicit
    env = os.environ.get(ENV_PREFIX + "CONFIG")
    if env:
        return env
    if os.path.exists("roombook.ini"):
        return "roombook.ini"
    return None


def _read_people(parser):
    roles = {}
    if parser.has_section("people"):
        for role, names in parser.items("people"):
            if role not in ROLES:
                continue
            for name in names.split(","):
                name = name.strip()
                if name:
                    roles[name] = role
    return roles


def load(config_path=None, environ=None):
    """Build Settings from defaults, the ini file and the environment."""
    environ = os.environ if environ is None else environ
    values = dict(DEFAULTS)
    notes = []
    roles = {}
    path = _ini_path(config_path)
    if path:
        parser = configparser.ConfigParser()
        with open(path, encoding="utf-8") as f:
            parser.read_file(f)
        for section in parser.sections():
            if section == "people":
                continue
            allowed = SECTIONS.get(section)
            if allowed is None:
                notes.append(f"unknown section [{section}] ignored")
                continue
            for key, raw in parser.items(section):
                if key not in allowed:
                    notes.append(f"{key} does not belong in [{section}], ignored")
                    continue
                values[key] = _coerce(key, raw)
        roles = _read_people(parser)
    for key in DEFAULTS:
        raw = environ.get(ENV_PREFIX + key.upper())
        if raw is not None and raw != "":
            values[key] = _coerce(key, raw)
    if values["close_hour"] <= values["open_hour"]:
        raise ValueError("close_hour must be after open_hour")
    return Settings(values, roles, source=path, notes=notes)
