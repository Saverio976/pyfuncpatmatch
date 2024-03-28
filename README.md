# pyfuncpatmatch

Pattern matching (like haskell) for python fonctions

## Install

```bash
pip install pyfuncpatmatch
```

## Usage

```python
from pyfuncpatmatch import pm, _eq

@pm(lambda _: 0, _eq(0))
@pm(lambda _: 1, _eq(1))
def fib_rec(n: int):
    return fib_rec(n - 1) + fib_rec(n - 2)
```

```python
from pyfuncpatmatch import pm, _gte, _lte

@pm(lambda x: f"You are not a teen ({x})", _gte(18))
@pm(lambda x: f"You are not a teen ({x})", _lte(11))
def is_teen(x):
    return f"You are a teen ({x})"
```

```python
from pyfuncpatmatch import pm, _and, _lambda

@pm(
    lambda _: "FizzBuzz",
    _and(_lambda(lambda x: x % 3 == 0), _lambda(lambda x: x % 5 == 0)),
)
@pm(lambda _: "Fizz", _lambda(lambda x: x % 3 == 0))
@pm(lambda _: "Buzz", _lambda(lambda x: x % 5 == 0))
def fizzbuzz(x):
    return f"{x}"
```
