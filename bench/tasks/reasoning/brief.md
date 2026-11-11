Answer three questions. Work them out carefully; do not run any code.

Q1. What does this Python program print?

```python
def f(n):
    c = 0
    for i in range(n):
        for j in range(i, n, 3):
            c += 1
    return c
print(f(10))
```

Q2. What does this Python program print?

```python
def add(x, acc=[]):
    acc.append(x)
    return len(acc)

r = [add(1), add(2), add(3, []), add(4)]
print(sum(r))
```

Q3. How many integers from 1 to 1000 inclusive are divisible by 3 or by 5, but not by 15?

Reply with exactly one line of JSON and nothing else, for example:
{"q1": 0, "q2": 0, "q3": 0}
