from sys import exit
from pyfuncpatmatch import patfunc, PatListExtract

@patfunc([0], {}, lambda _: 0)
@patfunc([1], {}, lambda _: 1)
def fib_rec(n: int) -> int:
    return fib_rec(n - 1) + fib_rec(n - 2)

print("fib_rec 1")
if fib_rec(0) != 0:
    exit(1)
print("fib_rec 2")
if fib_rec(1) != 1:
    exit(1)
print("fib_rec 3")
if fib_rec(6) != 8:
    exit(1)


@patfunc([""], {}, lambda _: "Empty Name")
@patfunc([PatListExtract()], {}, lambda x,_: x)
def print_initial(_: str):
    ...

print("print_initial 1")
if print_initial("") != "Empty Name":
    exit(1)
print("print_initial 2")
if print_initial("a") != "a":
    exit(1)
print("print_initial 3")
if print_initial("SupperName") != "S":
    exit(1)


def for_admin(xp, is_admin=True):
    return "Admin has 2000xp"

def for_newbie(xp, is_admin=False):
    return "You are new"

@patfunc([], {"is_admin": True}, for_admin)
@patfunc([1], {"is_admin": False}, for_newbie)
def print_for(xp, is_admin=False):
    return f"Someone has xp: {xp}"

print("print_for 1")
if print_for(2, True) != "Admin has 2000xp":
    exit(1)
print("print_for 2")
if print_for(1, False) != "You are new":
    exit(1)
print("print_for 3")
if print_for(20, False) != "Someone has xp: 20":
    exit(1)
