from sys import exit
from pyfuncpatmatch import patfunc, PatListExtract

@patfunc([""], {}, lambda _: "Empty Name")
@patfunc([PatListExtract(fst_match="s")], {}, lambda x,_: x)
def print_initial(_: str):
    return 'No'

print("print_initial 1")
if print_initial("") != "Empty Name":
    exit(1)
print("print_initial 2")
if print_initial("a") != "No":
    exit(1)
print("print_initial 3")
if print_initial("supper") != "s":
    exit(1)


@patfunc([""], {}, lambda _: "Empty Name")
@patfunc([PatListExtract(rest_match="s")], {}, lambda x,_: x)
def print_init(_: str):
    return 'No'

print("print_ini 1")
if print_init("") != "Empty Name":
    exit(1)
print("print_ini 2")
if print_init("a") != "No":
    exit(1)
print("print_ini 3")
if print_init("as") != "a":
    exit(1)
