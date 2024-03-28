from pyfuncpatmatch import pm, __, _eq, _lt, _lte, _gt, _gte, _lambda, _and

if __name__ == "__main__":
    import sys

    nb_errors = 0

    def check_exact(check_name, actual, expected):
        global nb_errors
        if actual != expected:
            nb_errors += 1
            print(
                f"ERR: {check_name}: "
                f"[expected]`{expected}` | [actual]`{actual}`",
                file=sys.stderr,
            )
        else:
            print(f"ERR: {check_name}: OK", file=sys.stderr)

    def check_raise():
        global nb_errors
        if nb_errors != 0:
            print(f"ERR: {nb_errors}", file=sys.stderr)
            sys.exit(1)
        else:
            print("OK", file=sys.stderr)
            sys.exit(0)

    # ------------------------------------------------------------------------

    @pm(lambda _: 0, _eq(0))
    @pm(lambda _: 1, _eq(1))
    def fib_rec(n: int):
        return fib_rec(n - 1) + fib_rec(n - 2)

    check_exact("fib_rec(0)", fib_rec(0), 0)
    check_exact("fib_rec(1)", fib_rec(1), 1)
    check_exact("fib_rec(2)", fib_rec(2), 1)
    check_exact("fib_rec(6)", fib_rec(6), 8)

    # ------------------------------------------------------------------------

    @pm(lambda x: x, __())
    def wtf_not_called(_):
        return 0

    check_exact("wtf_not_called(1)", wtf_not_called(1), 1)
    check_exact("wtf_not_called('abc')", wtf_not_called("abc"), "abc")

    # ------------------------------------------------------------------------

    @pm(lambda x: f"You are not an adult ({x})", _lt(18))
    def is_adult(x):
        return f"You are an adult ({x})"

    check_exact("is_adult(18)", is_adult(18), "You are an adult (18)")
    check_exact("is_adult(17)", is_adult(17), "You are not an adult (17)")
    check_exact("is_adult(0)", is_adult(0), "You are not an adult (0)")

    # ------------------------------------------------------------------------

    @pm(lambda x: f"You are not a teen ({x})", _gte(18))
    @pm(lambda x: f"You are not a teen ({x})", _lte(11))
    def is_teen(x):
        return f"You are a teen ({x})"

    check_exact("is_teen(18)", is_teen(11), "You are not a teen (11)")
    check_exact("is_teen(17)", is_teen(18), "You are not a teen (18)")
    check_exact("is_teen(17)", is_teen(19), "You are not a teen (19)")
    check_exact("is_teen(10)", is_teen(10), "You are not a teen (10)")
    check_exact("is_teen(15)", is_teen(15), "You are a teen (15)")

    # ------------------------------------------------------------------------

    @pm(lambda x: f"You are not a child ({x})", _gt(11))
    def is_child(x):
        return f"You are a child ({x})"

    check_exact("is_child(10)", is_child(10), "You are a child (10)")
    check_exact("is_child(11)", is_child(11), "You are a child (11)")
    check_exact("is_child(12)", is_child(12), "You are not a child (12)")

    # ------------------------------------------------------------------------

    @pm(
        lambda _: "FizzBuzz",
        _and(_lambda(lambda x: x % 3 == 0), _lambda(lambda x: x % 5 == 0)),
    )
    @pm(lambda _: "Fizz", _lambda(lambda x: x % 3 == 0))
    @pm(lambda _: "Buzz", _lambda(lambda x: x % 5 == 0))
    def fizzbuzz(x):
        return f"{x}"

    check_exact("fizzbuzz(1)", fizzbuzz(1), "1")
    check_exact("fizzbuzz(2)", fizzbuzz(2), "2")
    check_exact("fizzbuzz(3)", fizzbuzz(3), "Fizz")
    check_exact("fizzbuzz(5)", fizzbuzz(5), "Buzz")
    check_exact("fizzbuzz(15)", fizzbuzz(15), "FizzBuzz")

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    check_raise()
