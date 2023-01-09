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

- with list extract
```python
from pyfuncpatmatch import patfunc, PatListExtract

@patfunc([PatListExtract()], {}, lambda x,y: print(x))
def print_initial(name: str):
    ...
```
in action
```python
>>> print_initial("SuperName")
S
>>> print_initial("a")
a
```
**but with empty value** (you could have not this error, but, still)
```python
>>> print_initial("")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File ".../pyfuncpatmatch/pyfuncpatmatch.py", line 64, in __call__
    kv, av, status = self._exe_extract_paterns(list(args), kwds)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../pyfuncpatmatch/pyfuncpatmatch.py", line 140, in _exe_extract_
paterns
    fst = value[0]
          ~~~~~^^^
IndexError: string index out of range
```
**so you need to put a pattern matching with an empty value** (like this:)
```python
from pyfuncpatmatch import patfunc, PatListExtract

@patfunc([""], {}, lambda x: print("Empty Name"))
@patfunc([PatListExtract()], {}, lambda x,y: print(x))
def print_initial(name: str):
    ...
```
and it will be like this:
```python
>>> print_initial("")
Empty Name
>>> print_initial("a")
a
>>> print_initial("SupperName")
S
```
