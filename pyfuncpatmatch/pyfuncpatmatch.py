import inspect
from collections import OrderedDict
from functools import update_wrapper
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


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
        var_name_fst: Optional[str] = None,
        var_name_rest: Optional[str] = None,
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
        call_k_wargs = self._match_args_to_kwargs_match(call_args, call_kwargs)
        new_k_wargs = OrderedDict()
        for key, value in call_k_wargs.items():
            if key not in self.extract_patterns.keys():
                new_k_wargs[key] = value
                continue
            extract = self.extract_patterns.pop(key)
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
        av, kv = self._kwargs_match_to_func_param(new_k_wargs)
        return (kv, av, "ok")


def patfunc(
    l_args: LArgsPatternMatch = PatMatchAll(),
    k_args: Union[KArgsPatternMatch, PatMatchAll] = PatMatchAll(),
    func_instead: Optional[Callable] = None,
):
    if isinstance(l_args, list):
        l_args = tuple(l_args)
    if isinstance(k_args, PatMatchAll):
        k_args = {}

    def inner_decorator(true_func: Callable):
        return _PatDecoratorClass(func_instead, true_func, l_args, k_args)

    return inner_decorator
