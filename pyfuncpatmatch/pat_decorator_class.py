import inspect
from collections import OrderedDict
from functools import update_wrapper
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pyfuncpatmatch.pat_match_types import (PatEqMatch, PatGtEqMatch,
                                            PatGtMatch, PatListExtract,
                                            PatLtEqMatch, PatLtMatch,
                                            PatMatchAll)
from pyfuncpatmatch.types import (KArgsPatternMatch, LArgsPatternMatch,
                                  PatternMatch)


class PatDecoratorClass:
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

    def _kwargs_match_to_func_param(
        self, k_wargs: OrderedDict[str, Dict[str, Union[Any, bool]]]
    ) -> Tuple[list, dict]:
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
    ) -> Tuple[
        Dict[
            str,
            Union[
                PatEqMatch,
                PatMatchAll,
                PatGtMatch,
                PatGtEqMatch,
                PatLtMatch,
                PatLtEqMatch,
            ],
        ],
        Dict[str, PatListExtract],
    ]:
        exact_patterns: Dict[
            str,
            Union[
                PatEqMatch,
                PatMatchAll,
                PatGtMatch,
                PatGtEqMatch,
                PatLtMatch,
                PatLtEqMatch,
            ],
        ] = {}
        extract_pattern: Dict[str, PatListExtract] = {}
        for key_arg, item_arg in k_args.items():
            if isinstance(item_arg["value"], PatListExtract):
                extract_pattern[key_arg] = item_arg["value"]
            elif isinstance(
                item_arg["value"],
                (
                    PatEqMatch,
                    PatMatchAll,
                    PatGtMatch,
                    PatGtEqMatch,
                    PatLtMatch,
                    PatLtEqMatch,
                ),
            ):
                exact_patterns[key_arg] = item_arg["value"]
            else:
                exact_patterns[key_arg] = PatEqMatch(value=item_arg["value"])
        return (exact_patterns, extract_pattern)

    def _check_patmatch(self, pat: PatternMatch, value: Any) -> bool:
        if isinstance(pat, PatMatchAll):
            return True
        if isinstance(pat, PatEqMatch) and value != pat.value:
            return False
        if isinstance(pat, PatGtMatch) and value <= pat.value:
            return False
        if isinstance(pat, PatGtEqMatch) and value < pat.value:
            return False
        if isinstance(pat, PatLtMatch) and value >= pat.value:
            return False
        if isinstance(pat, PatGtEqMatch) and value > pat.value:
            return False
        return True

    def _is_exact_paterns(self, call_args: list, call_kwargs: dict) -> bool:
        call_k_wargs = self._match_args_to_kwargs_match(call_args, call_kwargs)
        for key, exact in self.exact_patterns.items():
            if self._check_patmatch(exact, call_k_wargs[key]["value"]) is False:
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
            if isinstance(value, (PatListExtract, PatEqMatch, PatMatchAll, bool)):
                return ({}, [], "ko")
            try:
                fst = value[0]
                rest = value[1:]
            except Exception:
                return ({}, [], "ko")
            if self._check_patmatch(extract.fst_match, fst) is False:
                return ({}, [], "ko")
            if self._check_patmatch(extract.rest_match, rest) is False:
                return ({}, [], "ko")
            if extract.var_name_fst is None:
                new_k_wargs[f"{key}__________fst"] = {"value": fst, "is_kwargs": False}
            else:
                new_k_wargs[extract.var_name_fst] = {"value": fst, "is_kwargs": True}
            if extract.var_name_rest is None:
                new_k_wargs[f"{key}__________rest"] = {
                    "value": rest,
                    "is_kwargs": False,
                }
            else:
                new_k_wargs[extract.var_name_rest] = {"value": rest, "is_kwargs": True}
        if len(copy_extract.keys()) != 0:
            return ({}, [], "ko")
        av, kv = self._kwargs_match_to_func_param(new_k_wargs)
        return (kv, av, "ok")
