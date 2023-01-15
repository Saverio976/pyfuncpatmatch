from typing import Callable, Optional, Union

from pyfuncpatmatch.pat_decorator_class import PatDecoratorClass
from pyfuncpatmatch.pat_match_types import PatMatchAll
from pyfuncpatmatch.types import KArgsPatternMatch, LArgsPatternMatch


def patfunc(
    l_args: LArgsPatternMatch = PatMatchAll(),
    k_args: Union[KArgsPatternMatch, PatMatchAll] = PatMatchAll(),
    func_instead: Optional[Callable] = None,
):
    """patfunc.

    Parameters
    ----------
    l_args : LArgsPatternMatch
        list of pattern match / list extract to match for args
    k_args : Union[KArgsPatternMatch, PatMatchAll]
        dict of [keyword argument] = pattern match / list extract
    func_instead : Optional[Callable]
        function to call instead of the decorated function if patterns before are true

    Examples
    --------
    ```python
    @patfunc([0], {}, lambda _: 0)
    @patfunc([1], {}, lambda _: 1)
    def fib_rec(n: int):
        return fib_rec(n - 1) + fib_rec(n - 2)
    ```
    will call the first lambda that return 0 if the first argument of fib_rec (n) is equal to 0
    will call the first lambda that return 1 if the first argument of fib_rec (n) is equal to 1
    else, it will call the decorated function
    this is an equivalent (in a much beautiful way) to that:
    ```python
    def fib_rec(n: int):
        if n == 0:
            return 0
        if n == 1:
            return 1
        return fib_rec(n - 1) + fib_rec(n - 2)
    ```
    """
    if isinstance(l_args, list):
        l_args = tuple(l_args)
    if isinstance(k_args, PatMatchAll):
        k_args = {}

    def inner_decorator(true_func: Callable):
        return PatDecoratorClass(func_instead, true_func, l_args, k_args)

    return inner_decorator
