from collections import OrderedDict
from typing import Any, Callable, Dict, Tuple
import types
from pyfuncpatmatch.pm_ext import PMExtensionCheck, _eq
from functools import update_wrapper
import inspect


def _transform_all_to_kwargs(
    parameters, convert: bool, pm_args: Tuple[Any], pm_kwargs: Dict[str, Any]
) -> OrderedDict[str, Tuple[bool, PMExtensionCheck]]:
    all_kwargs: OrderedDict[str, Tuple[bool, PMExtensionCheck]] = OrderedDict()
    for pm_arg, param_keyword in zip(pm_args, parameters.keys()):
        if not convert or isinstance(pm_arg, PMExtensionCheck):
            all_kwargs[param_keyword] = (True, pm_arg)
        else:
            all_kwargs[param_keyword] = (True, _eq(pm_arg))
    for param_keyword, pm_arg in pm_kwargs.items():
        if not convert or isinstance(pm_arg, PMExtensionCheck):
            all_kwargs[param_keyword] = (False, pm_arg)
        else:
            all_kwargs[param_keyword] = (False, _eq(pm_arg))
    return all_kwargs


class PM:
    def __init__(
        self,
        func_wrapped: Callable,
        alternative_function: Callable,
        pm_args: Tuple[Any],
        pm_kwargs: Dict[str, Any],
    ) -> None:
        update_wrapper(self, func_wrapped)
        self.func_wrapped = func_wrapped
        self.func_wrapped_parameters = inspect.signature(
            func_wrapped
        ).parameters
        self.alternative_function = alternative_function
        self.pm_pattern_by_parameter = _transform_all_to_kwargs(
            parameters=self.func_wrapped_parameters,
            convert=True,
            pm_args=pm_args,
            pm_kwargs=pm_kwargs,
        )
        self._alternative_function_is_lambda = (
            isinstance(alternative_function, types.LambdaType)
            and alternative_function.__name__ == "<lambda>"
        )

    def __call__(self, *args, **kwargs):
        all_kwargs_arg = _transform_all_to_kwargs(
            parameters=self.func_wrapped_parameters,
            convert=False,
            pm_args=args,
            pm_kwargs=kwargs,
        )
        for check_key, (
            _,
            check_value,
        ) in self.pm_pattern_by_parameter.items():
            if check_key not in all_kwargs_arg:
                continue
            if not check_value.check_comply(all_kwargs_arg[check_key][1]):
                return self.func_wrapped(*args, **kwargs)
        args_alternativ = []
        kwargs_alternativ = {}
        for key, (is_args, value) in all_kwargs_arg.items():
            if key not in self.pm_pattern_by_parameter:
                continue
            keyword = None if is_args else key
            args_tmp, kwargs_tmp = self.pm_pattern_by_parameter[key][
                1
            ].get_value(keyword, value)
            args_alternativ.extend(args_tmp)
            kwargs_alternativ.update(**kwargs_tmp)
        if self._alternative_function_is_lambda:
            for key in self.func_wrapped_parameters.keys():
                if key in kwargs_alternativ:
                    args_alternativ.append(kwargs_alternativ[key])
            kwargs_alternativ.clear()
        return self.alternative_function(*args_alternativ, **kwargs_alternativ)


def pm(alternative_function, *args, **kwargs):
    def inner_decorator(func_wrapped):
        return PM(
            func_wrapped=func_wrapped,
            alternative_function=alternative_function,
            pm_args=args,
            pm_kwargs=kwargs,
        )

    return inner_decorator
