<!-- mmo provider=opencode model=opencode/mimo-v2.6-flash-free mode=rw status=ok exit=0 seconds=80 base=99f973a1a changed=1 -->
All rules now hold: each unit at most once (checked via index tracking), strict h→m→s ordering, every number must be followed by a unit (trailing digits rejected), empty string rejected, and any non-digit/non-unit character rejected — all raising `ValueError`. Visible tests pass (4/4 OK), and extra cases like `1m1h`, `1h1h`, `1h30`, `1s2m`, and `" 1h"` all raise `ValueError`.

DONE
