from functools import update_wrapper
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import inspect

class PatMatchAll:
    def __init__(self) -> None:
        pass

class PatEqMatch:
    def __init__(self, value: Any) -> None:
        self.value = value

class PatEqMatchList(PatEqMatch):
    def __init__(self, value: List[Any]) -> None:
        self.value = value

class PatListExtract:
    def __init__(
        self,
        var_name_fst: str,
        var_name_rest: str,
        fst_eq_match: Union[PatEqMatch, PatMatchAll] = PatMatchAll(),
        rest_eq_match: Union[PatEqMatchList, PatMatchAll] = PatMatchAll(),
    ) -> None:
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
    def __init__(self, func_instead: Optional[Callable], true_func: Callable, l_args: LArgsPatternMatch = [], k_args: KArgsPatternMatch = {}) -> None:
        update_wrapper(self, true_func)
        self.true_func = true_func
        self.func_instead = func_instead
        self.parameters = inspect.signature(true_func).parameters
        self._kwargs = self._args_to_kwargs(l_args, k_args)
        exact_patterns, extract_patterns = self._parse_kwargs(self._kwargs)
        self.exact_patterns = exact_patterns
        self.extract_patterns = extract_patterns

    def __call__(self, *args, **kwds) -> Any:
        if self.func_instead is None:
            response = self.true_func(*args, **kwds)
        elif self._is_exact_paterns(list(args), kwds):
            kwargs = self._exe_extract_paterns(list(args), kwds)
            if isinstance(kwargs, str):
                if kwargs == "ok":
                    response = self.func_instead(*args, **kwds)
                else:
                    response = self.true_func(*args, **kwds)
            else:
                response = self.func_instead(**kwargs)
        else:
            response = self.true_func(*args, **kwds)
        return response

    def _args_to_kwargs(self, args: Union[LArgsPatternMatch, list], kwargs: Union[KArgsPatternMatch, dict]) -> Union[KArgsPatternMatch, dict]:
        ret = {}
        if not isinstance(args, PatMatchAll):
            for value, key in zip(args, self.parameters.keys()):
                ret[key] = value
        for key, value in kwargs.items():
            ret[key] = value
        return ret

    def _parse_kwargs(self, k_args: KArgsPatternMatch) -> Tuple[Dict[str, Union[PatEqMatch, PatMatchAll]], Dict[str, PatListExtract]]:
        exact_patterns: Dict[str, Union[PatEqMatch, PatMatchAll]] = {}
        extract_pattern: Dict[str, PatListExtract] = {}
        for key_arg, item_arg in k_args.items():
            if isinstance(item_arg, PatListExtract):
                extract_pattern[key_arg] = item_arg
            elif isinstance(item_arg, PatEqMatch):
                exact_patterns[key_arg] = item_arg
            elif isinstance(item_arg, PatMatchAll):
                exact_patterns[key_arg] = item_arg
            else:
                exact_patterns[key_arg] = PatEqMatch(value=item_arg)
        return (exact_patterns, extract_pattern)

    def _is_exact_paterns(self, call_args: list, call_kwargs: dict) -> bool:
        call_k_wargs = self._args_to_kwargs(call_args, call_kwargs)
        for key, exact in self.exact_patterns.items():
            if isinstance(exact, PatMatchAll):
                continue
            if call_k_wargs[key] != exact.value:
                return False
        return True

    def _exe_extract_paterns(self, call_args: list, call_kwargs: dict) -> Union[dict, str]:
        if len(self.extract_patterns) == 0:
            return "ok"
        call_k_wargs = self._args_to_kwargs(call_args, call_kwargs)
        for key, extract in self.extract_patterns.items():
            value = call_k_wargs.get(key)
            if value is None or isinstance(value, (PatListExtract, PatEqMatch, PatMatchAll)):
                return "not ok"
            fst = value[0]
            rest = value[1:]
            if not isinstance(extract.fst_eq_match, PatMatchAll):
                if fst != extract.fst_eq_match.value:
                    return "not ok"
            if not isinstance(extract.rest_eq_match, PatMatchAll):
                if rest != extract.rest_eq_match.value:
                    return "not ok"
            call_k_wargs.pop(key)
            call_k_wargs[extract.var_name_fst] = fst
            call_k_wargs[extract.var_name_rest] = rest
        return call_k_wargs


def patfunc(
    l_args: LArgsPatternMatch = PatMatchAll(),
    k_args: Union[KArgsPatternMatch, PatMatchAll] = PatMatchAll(),
    func_instead: Optional[Callable] = None
):
    if isinstance(l_args, list):
        l_args = tuple(l_args)
    if isinstance(k_args, PatMatchAll):
        k_args = {}
    def inner_decorator(true_func: Callable):
        return _PatDecoratorClass(func_instead, true_func, l_args, k_args)
    return inner_decorator
