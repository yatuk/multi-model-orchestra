The `roombook` package in the current directory is our meeting room booking tool (try
`python -m roombook --help`). Please make the change and fix the bug in this ticket.

**Keep cancelled bookings.** Today cancelling a booking deletes it, so when someone asks the front
desk where their meeting went there is nothing to show, and the monthly usage report cannot tell a
room that was booked and dropped from a room nobody wanted. From now on a cancelled booking stays:
marked as cancelled, with when it was cancelled, who did it (the person running the command, as for
every other command) and an optional reason, given as `cancel <id> --reason "..."`. `show <id>`
must say that a booking is cancelled, by whom, and the reason when there is one. The day listing
should show cancelled bookings too, marked `[cancelled]`, so the desk sees what happened.
Cancelling a booking that is already cancelled is an error that says it is already cancelled.
Apart from that, a cancelled booking must behave as if it were gone: the room is free again for
anyone to book, shows as free, and nothing else counts it. The monthly usage report gets a column
`cancelled` with the number of cancelled bookings per room; a booking that was cancelled late, that
is less than the building's notice period before it started (the period the cancel command already
warns about), still counts in the report's bookings and hours as if it had taken place, because by
then nobody else could use the room. Backups must keep cancellations, and the databases and backup
files we already have must keep working.

**Double bookings after the spreadsheet import.** Since facilities started importing their
spreadsheet, people get double booked: someone books a room over a meeting that came in through the
import, and roombook does not object. Find out why and fix it, and make sure the meetings that were
imported before your fix are protected too.

Rules:
1. Read the code before you change it. Everything this ticket does not change must keep working
   exactly as it does now, including the output other teams' scripts read.
2. Keep every public name in `roombook/__init__.py`. Standard library only.
3. Change only files inside `roombook/`. Do not edit, delete or add test files.
4. Run `python -m unittest test_roombook`. Some of its tests check the new behaviour and fail now;
   all of them must pass when you are done. Held-out tests check much more than these.

Do not commit. Finish with one line: DONE or FAILED and the reason.
