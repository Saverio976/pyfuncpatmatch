from typing import Any, Callable, Dict, Tuple
from pyfuncpatmatch.pm_ext import PMExtensionCheck, __, _eq
from functools import update_wrapper
import inspect


def _transform_all_to_kwargs(
    parameters, convert: bool, pm_args: Tuple[Any], pm_kwargs: Dict[str, Any]
) -> Dict[str, PMExtensionCheck]:
    all_kwargs = {}
    for pm_arg, param_keyword in zip(pm_args, parameters.keys()):
        if not convert or isinstance(pm_arg, PMExtensionCheck):
            all_kwargs[param_keyword] = pm_arg
        else:
            all_kwargs[param_keyword] = _eq(pm_arg)
    for param_keyword, pm_arg in pm_kwargs.items():
        if not convert or isinstance(pm_arg, PMExtensionCheck):
            all_kwargs[param_keyword] = pm_arg
        else:
            all_kwargs[param_keyword] = _eq(pm_arg)
    for param_keyword in parameters.keys():
        if param_keyword not in all_kwargs:
            all_kwargs[param_keyword] = __()
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

    def __call__(self, *args, **kwargs):
        all_kwargs_arg = _transform_all_to_kwargs(
            parameters=self.func_wrapped_parameters,
            convert=False,
            pm_args=args,
            pm_kwargs=kwargs,
        )
        for check_key, check_value in self.pm_pattern_by_parameter.items():
            if not check_value.check_comply(all_kwargs_arg[check_key]):
                return self.func_wrapped(*args, **kwargs)

        return self.alternative_function(*args, **kwargs)


def pm(alternative_function, *args, **kwargs):
    def inner_decorator(func_wrapped):
        return PM(
            func_wrapped=func_wrapped,
            alternative_function=alternative_function,
            pm_args=args,
            pm_kwargs=kwargs,
        )

    return inner_decorator
