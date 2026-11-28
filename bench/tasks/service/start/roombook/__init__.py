"""roombook: meeting room bookings for one building, kept in a sqlite file.

Run it as `python -m roombook --help`. The layers, from the bottom:

  util/      parsing and formatting of times, ids and tables
  model/     Room, Booking, Series (plain data)
  store/     sqlite: schema and upgrades, rooms, bookings, JSON backups
  parse/     the facilities spreadsheet, room files, listing ranges
  rules/     what a booking must satisfy
  sched/     free time, weekly series
  service.py what the commands do
  report/    listings, usage, the finance export
  cli/       the command line
"""
from .cli.main import main
from .model import Booking, Room, Series
from .service import BookingService
from .settings import load as load_settings
from .store import open_db

__version__ = "2.3.1"
