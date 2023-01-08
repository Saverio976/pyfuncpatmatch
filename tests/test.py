from pyfuncpatmatch import patfunc, PatListExtract

@patfunc([0], {}, lambda _: 0)
@patfunc([1], {}, lambda _: 1)
def fib_rec(n: int) -> int:
    return fib_rec(n - 1) + fib_rec(n - 2)

def print_initial(first_letter="", rest=""):
    print(first_letter)

@patfunc([], {"letters": PatListExtract("first_letter", "rest")}, print_initial)
def print_letters(letters = None):
    print("Nothing To Print")

