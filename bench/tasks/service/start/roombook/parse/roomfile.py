"""Room definitions in an ini file, one section per room:

    [A]
    name = Atlas
    capacity = 8
    features = screen, phone
"""
import configparser

from ..errors import UsageError
from ..model.room import Room, features_from_text, norm_code


def parse_rooms(text):
    parser = configparser.ConfigParser()
    try:
        parser.read_string(text)
    except configparser.Error as e:
        raise UsageError(f"bad room file: {e}") from None
    rooms = []
    for section in parser.sections():
        s = parser[section]
        try:
            capacity = int(s.get("capacity", "4"))
        except ValueError:
            raise UsageError(f"room {section}: capacity must be a number") from None
        if capacity < 1:
            raise UsageError(f"room {section}: capacity must be at least 1")
        rooms.append(Room(code=norm_code(section), name=s.get("name", "").strip(), capacity=capacity,
                          features=features_from_text(s.get("features", ""))))
    return rooms


def read_rooms(path):
    with open(path, encoding="utf-8") as f:
        return parse_rooms(f.read())
