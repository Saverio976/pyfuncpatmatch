# pyfuncpatmatch

Pattern matching (like haskell) for python fonctions

## Install

```bash
pip install pyfuncpatmatch
```

## Usage

### Exemples

_For a full list of exemples and tests done, see:_ [main](./pyfuncpatmatch/__main__.py)

#### eq

```python
from pyfuncpatmatch import pm, _eq

@pm(lambda _: 0, _eq(0))
@pm(lambda _: 1, _eq(1))
def fib_rec(n: int):
    return fib_rec(n - 1) + fib_rec(n - 2)
```

#### gte, lte

```python
from pyfuncpatmatch import pm, _gte, _lte

@pm(lambda x: f"You are not a teen ({x})", _gte(18))
@pm(lambda x: f"You are not a teen ({x})", _lte(11))
def is_teen(x):
    return f"You are a teen ({x})"
```

#### and, lambda

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

#### empty, all, extract

```python
from pyfuncpatmatch import pm, pm_raise, _empty, __, _extract

# pm_raise is a function that raise the exception being passed
# -> lambda can't raise the expression directly
@pm(lambda _: pm_raise(ValueError("empty iterable")), _empty())
@pm(lambda splited: splited[0], _extract(__(), __()))
def head(x):
    raise SyntaxError(f"{x} is not iterable")

@pm(lambda splited: splited[1], _extract(__(), __()))
def tail(x):
    raise ValueError(f"{x} is not iterable")
```

#### Keyword Matching

Arguments and Keyword Arguments are passed to the callback the same way they
would have be passed to the initial function.

But when the callback is a lambda, it automatically transform keywords arguments
as arguments (because passing keyword arguments to lambda raise an exception).

This ensure that you can keep calling the initial function with arguments and
keywords arguments.

```python
from pyfuncpatmatch import pm, __, _or, _eq

@pm(lambda x, z: (x,z), x=__(), z=_or(_eq(2), _eq(5)))
@pm(lambda x, z: (x,z), __(), z=_eq(10))
def select(x, y, z):
    return (x, y, z)

# >>> select(1, 2, z=3)
# (1, 2, 3)
# >>> select(0, 1, 2)
# (0, 2)
# >>> select(1, 3, 10)
# (1, 10)
```
