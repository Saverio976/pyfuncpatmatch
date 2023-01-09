import inspect
from collections import OrderedDict
from functools import update_wrapper
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class PatMatchAll:
    """PatMatchAll.
    If you want to match all

    Useful for l_args:
    ```python
    @patfunc([1, PatMatchAll(), 2], ...
    def abc(a, b, c):
        ...
    ```
    """

    def __init__(self) -> None:
        pass


class PatEqMatch:
    """PatEqMatch.

    ```python
    @patfunc([PatEqMatch(1)], ...)
    def abc(a):
        ...
    ```
    will be the same as
    ```python
    @patfunc([1], ...)
    def abc(a):
        ...
    ```
    """

    def __init__(self, value: Any) -> None:
        self.value = value


class PatEqMatchList(PatEqMatch):
    """PatEqMatchList.

    same as PatEqMatch but with list value (usefull for PatListExtract)
    """

    def __init__(self, value: List[Any]) -> None:
        self.value = value


class PatListExtract:
    """PatListExtract.

    Realy cool feature

    Example:
    ```python
    @patfunc([""], {}, lambda x: print("Empty Name"))
    @patfunc([PatListExtract()], {}, lambda x,y: print(x))
    def print_initial(name: str):
        ...
    ```
    will react like this:
    ```python
    >>> print_initial("")
    Empty Name
    >>> print_initial("a")
    a
    >>> print_initial("SupperName")
    S
    ```
    Dont miss the first patfunc, else your code will raise an error for empty string
    This apply for list too
    """

    def __init__(
        self,
        var_name_fst: Optional[str] = None,
        var_name_rest: Optional[str] = None,
        fst_eq_match: Union[PatEqMatch, PatMatchAll, Any] = PatMatchAll(),
        rest_eq_match: Union[PatEqMatchList, PatMatchAll, Any] = PatMatchAll(),
    ) -> None:
        """__init__.

        Parameters
        ----------
        var_name_fst : Optional[str]
            name to give (kwargs) to the first elem, if None, it is passed as args, in place of the true arg order
        var_name_rest : Optional[str]
            name to give (kwargs) to the rest of the elem, if None, it is passed as args, after var_name_fst
        fst_eq_match : Union[PatEqMatch, PatMatchAll, Any]
            pattern match for the first elem
        rest_eq_match : Union[PatEqMatchList, PatMatchAll, Any]
            pattern match for the rest of the elem

        Returns
        -------
        None

        """
        self.var_name_fst = var_name_fst
        self.var_name_rest = var_name_rest
        self.fst_eq_match = fst_eq_match
        self.rest_eq_match = rest_eq_match


PatternMatch = Union[Any, PatListExtract, PatEqMatch, PatMatchAll]
LArgsPatternMatch = Union[List[PatternMatch], Tuple[PatternMatch], PatMatchAll]
LArgsPatternEqMatch = Union[List[PatEqMatch], Tuple[PatEqMatch]]
LArgsPatternExtractMatch = Union[List[PatListExtract], Tuple[PatListExtract]]
KArgsPatternMatch = Dict[str, PatternMatch]


class _PatDecoratorClass:
    def __init__(
        self,
        func_instead: Optional[Callable],
        true_func: Callable,
        l_args: LArgsPatternMatch = [],
        k_args: KArgsPatternMatch = {},
    ) -> None:
        update_wrapper(self, true_func)
        self.true_func = true_func
        self.func_instead = func_instead
        self.parameters = inspect.signature(true_func).parameters
        self._kwargs_match = self._match_args_to_kwargs_match(l_args, k_args)
        exact_patterns, extract_patterns = self._parse_kwargs_match(self._kwargs_match)
        self.exact_patterns = exact_patterns
        self.extract_patterns = extract_patterns

    def __call__(self, *args, **kwds) -> Any:
        if self.func_instead is None:
            response = self.true_func(*args, **kwds)
        elif self._is_exact_paterns(list(args), kwds):
            kv, av, status = self._exe_extract_paterns(list(args), kwds)
            if status == "ko":
                response = self.true_func(*args, **kwds)
            elif status == "ok-no-extract":
                response = self.func_instead(*args, **kwds)
            else:
                response = self.func_instead(*av, **kv)
        else:
            response = self.true_func(*args, **kwds)
        return response

    def _match_args_to_kwargs_match(
        self,
        args: Union[LArgsPatternMatch, List[Any]],
        kwargs: Union[KArgsPatternMatch, Dict[str, Any]],
    ) -> OrderedDict[str, Dict[str, Union[Any, bool]]]:
        ret = OrderedDict()
        if not isinstance(args, PatMatchAll):
            for value, key in zip(args, self.parameters.keys()):
                ret[key] = {"value": value, "is_kwargs": False}
        for key, value in kwargs.items():
            ret[key] = {"value": value, "is_kwargs": True}
        return ret

    def _kwargs_match_to_func_param(self, k_wargs: OrderedDict[str, Dict[str, Union[Any, bool]]]) -> Tuple[list, dict]:
        args = []
        kwargs = {}
        for key, value in k_wargs.items():
            if value["is_kwargs"]:
                kwargs[key] = value["value"]
            else:
                args.append(value["value"])
        return (args, kwargs)

    def _parse_kwargs_match(
        self, k_args: Dict[str, Dict[str, Union[Any, bool]]]
    ) -> Tuple[Dict[str, Union[PatEqMatch, PatMatchAll]], Dict[str, PatListExtract]]:
        exact_patterns: Dict[str, Union[PatEqMatch, PatMatchAll]] = {}
        extract_pattern: Dict[str, PatListExtract] = {}
        for key_arg, item_arg in k_args.items():
            if isinstance(item_arg["value"], PatListExtract):
                extract_pattern[key_arg] = item_arg["value"]
            elif isinstance(item_arg["value"], PatEqMatch):
                exact_patterns[key_arg] = item_arg["value"]
            elif isinstance(item_arg["value"], PatMatchAll):
                exact_patterns[key_arg] = item_arg["value"]
            else:
                exact_patterns[key_arg] = PatEqMatch(value=item_arg["value"])
        return (exact_patterns, extract_pattern)

    def _is_exact_paterns(self, call_args: list, call_kwargs: dict) -> bool:
        call_k_wargs = self._match_args_to_kwargs_match(call_args, call_kwargs)
        for key, exact in self.exact_patterns.items():
            if isinstance(exact, PatMatchAll):
                continue
            if call_k_wargs[key]["value"] != exact.value:
                return False
        return True

    def _exe_extract_paterns(
        self, call_args: list, call_kwargs: dict
    ) -> Tuple[dict, list, str]:
        if len(self.extract_patterns) == 0:
            return ({}, [], "ok-no-extract")
        copy_extract = self.extract_patterns.copy()
        call_k_wargs = self._match_args_to_kwargs_match(call_args, call_kwargs)
        new_k_wargs = OrderedDict()
        for key, value in call_k_wargs.items():
            if key not in copy_extract.keys():
                new_k_wargs[key] = value
                continue
            extract = copy_extract.pop(key)
            value = value["value"]
            if isinstance(
                value, (PatListExtract, PatEqMatch, PatMatchAll, bool)
            ):
                return ({}, [], "ko")
            fst = value[0]
            rest = value[1:]
            if not isinstance(extract.fst_eq_match, PatMatchAll):
                if fst != extract.fst_eq_match.value:
                    return ({}, [], "ko")
            if not isinstance(extract.rest_eq_match, PatMatchAll):
                if rest != extract.rest_eq_match.value:
                    return ({}, [], "ko")
            if extract.var_name_fst is None:
                new_k_wargs[f"{key}__________fst"] = {"value": fst, "is_kwargs": False}
            else:
                new_k_wargs[extract.var_name_fst] = {"value": fst, "is_kwargs": True}
            if extract.var_name_rest is None:
                new_k_wargs[f"{key}__________rest"] = {"value": rest, "is_kwargs": False}
            else:
                new_k_wargs[extract.var_name_rest] = {"value": rest, "is_kwargs": True}
        if len(copy_extract.keys()) != 0:
            return ({}, [], "ko")
        av, kv = self._kwargs_match_to_func_param(new_k_wargs)
        return (kv, av, "ok")


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
        return _PatDecoratorClass(func_instead, true_func, l_args, k_args)

    return inner_decorator
