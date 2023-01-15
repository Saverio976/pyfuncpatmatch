from sys import exit
from pyfuncpatmatch import patfunc, PatListExtract
from pyfuncpatmatch.pat_match_types import PatEqMatch, PatGtMatch, PatLtMatch

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


@patfunc([PatLtMatch(3)], {}, lambda _: "LT")
@patfunc([PatEqMatch(3)], {}, lambda _: "EQ")
@patfunc([PatGtMatch(3)], {}, lambda _: "GT")
def gt_than_3(_: int) -> str:
    ...

print("gt_than_3 1")
if gt_than_3(0) != "LT":
    exit(1)
print("gt_than_3 2")
if gt_than_3(3) != "EQ":
    exit(1)
print("gt_than_3 3")
if gt_than_3(4) != "GT":
    exit(1)
