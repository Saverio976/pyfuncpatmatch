from functools import update_wrapper
import inspect

class PMExtension:
    def __init__(self) -> None:
        pass

def _transform_all_to_kwargs(parameters, pm_args, pm_kwargs):
    all_kwargs = {}
    for pm_arg, param_keyword in zip(pm_args, parameters.keys()):
        all_kwargs[param_keyword] = pm_arg
    for param_keyword, pm_arg in pm_kwargs.items():
        all_kwargs[param_keyword] = pm_arg
    return all_kwargs

class PM:
    def __init__(self, func_wrapped, alternative_function, pm_args, pm_kwargs) -> None:
        update_wrapper(self, func_wrapped)
        self.func_wrapped = func_wrapped
        self.func_wrapped_parameters = inspect.signature(func_wrapped).parameters
        self.alternative_function = alternative_function
        self.pm_pattern_by_parameter = _transform_all_to_kwargs(parameters=self.func_wrapped_parameters, pm_args=pm_args, pm_kwargs=pm_kwargs)

    def __call__(self, *args, **kwargs):
        all_kwargs_arg = _transform_all_to_kwargs(parameters=self.func_wrapped_parameters, pm_args=args, pm_kwargs=kwargs)
        # TODO: check patterns
        # TODO: if instance(PMExtension) -> check with custom check

def pm(alternative_function, *args, **kwargs):
    def inner_decorator(func_wrapped):
        return PM(func_wrapped=func_wrapped, alternative_function=alternative_function, pm_args=args, pm_kwargs=kwargs)

    return inner_decorator
