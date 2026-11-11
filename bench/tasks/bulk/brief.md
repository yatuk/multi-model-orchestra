Label every line with exactly one of CRITICAL, ERROR, WARN, INFO.
Apply the first rule that matches, top to bottom:
1. CRITICAL if the line contains the whole word "panic" or "fatal" (any case).
   Whole word means "panic" matches, "panicked" does not.
2. ERROR if it contains the whole word "error" (any case), or an HTTP status from 500 to 599.
   "errors", "errorless" are not the whole word "error".
3. WARN if it contains the whole word "warn" or "warning" (any case),
   or an HTTP status from 400 to 499 other than 404.
4. INFO otherwise (including 404).
An HTTP status is a 3-digit number right after a request path, as in "GET /x 503 2ms".

Reply with CSV only: a header line `line,label`, then one row per line, in order.
No other text.

Lines (number TAB text):

1	GET /api/users 200 12ms
2	GET /api/users/42 404 3ms
3	POST /api/orders 500 220ms
4	worker-3 panic: nil map write
5	cache warm: errors=0 hits=1200
6	disk usage at 81 percent, warn threshold is 80
7	PUT /api/orders/7 409 18ms
8	auth: Error validating token for session 77
9	GET /health 200 1ms
10	db pool exhausted, fatal
11	GET /static/app.js 304 2ms
12	retrying upload (attempt 2 of 5)
13	POST /api/login 401 9ms
14	scheduler tick
15	GET /api/reports 503 3001ms
16	Warning: deprecated flag --legacy used
17	kernel: FATAL machine check
18	DELETE /api/users/9 204 7ms
19	parser: no errors found
20	GET /api/search 429 1ms
21	error budget remaining 97 percent
22	GET /favicon.ico 404 1ms
23	PATCH /api/items/3 422 15ms
24	backup finished in 812s
25	tls handshake warn: weak cipher offered
26	GET /api/export 502 60001ms
27	warmup: 0 warnings
28	runtime: goroutine panic recovered
29	POST /api/upload 413 40ms
30	GET / 200 5ms
31	ERROR could not reach payment gateway
32	metrics flushed
33	GET /api/items 500 9ms
34	config reloaded, warn: unknown key 'tz'
35	GET /missing 404 2ms
36	job 81 failed with error code 3
37	user 5 logged in
38	POST /api/pay 403 6ms
39	OOM killer invoked, fatal for pid 4411
40	GET /api/users 201 30ms
41	cron: errorless run complete
42	GET /admin 401 2ms
43	fan speed nominal
44	replication lag warn 4.2s
45	GET /api/stream 504 30000ms
46	Panic button pressed in UI test (simulated)
47	GET /docs 301 1ms
48	queue depth 0
49	POST /api/orders 400 11ms
50	certificate expires in 6 days (warn)
51	GET /api/v2/x 404 4ms
52	shutdown requested by operator
53	GET /api/slow 500 1200ms
54	index rebuilt with 0 errors
55	POST /api/retry 408 5000ms
56	ingest: error rate 0.01 percent
57	GET /ok 200 1ms
58	panicked at 'index out of bounds'
59	warn
60	GET /api/teapot 418 1ms
