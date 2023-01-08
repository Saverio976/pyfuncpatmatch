# pyfuncpatmatch

Pattern matching (like haskell) for python fonctions

## Install

```bash
pip install pyfuncpatmatch
```

## Usage

- basic recursive fibonacci
```python
from pyfuncpatmatch import patfunc

@patfunc([0], {}, lambda _: 0)
@patfunc([1], {}, lambda _: 1)
def fib_rec(n: int):
    return fib_rec(n - 1) + fib_rec(n - 2)
```

- less basic
```python
from pyfuncpatmatch import patfunc

def for_admin(xp, is_admin=True):
    print("Admin has 2000xp")

def for_newbie(xp, is_admin=False):
    print("You are new")

@patfunc([], {"is_admin": True}, for_admin)
@patfunc([1], {"is_admin": False}, for_newbie)
def print_for(xp, is_admin=False):
    print("Someone has xp:", xp)
```

in action:
```python
>>> print_for(1, True)
Admin has 2000xp
>>> print_for(1, False)
You are new
>>> print_for(20, False)
Someone has xp: 20
```
