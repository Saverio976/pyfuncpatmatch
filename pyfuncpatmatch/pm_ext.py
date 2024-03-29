from typing import (
    Any,
    Callable,
    Iterable,
    Sequence,
    Tuple,
    Dict,
    Optional,
    Union,
)


class PMExtension:
    def __init__(self) -> None:
        pass

    def get_value(
        self, keyword: Optional[str], value: Any
    ) -> Tuple[Tuple[Any], Dict[str, Any]]:
        if keyword:
            return (tuple(), {keyword: value})
        return ((value,), {})


class PMExtensionCheck(PMExtension):
    def __init__(self) -> None:
        super().__init__()

    def check_comply(self, value: Any) -> bool:
        raise NotImplementedError()


class __(PMExtensionCheck):
    def __init__(self) -> None:
        super().__init__()

    def check_comply(self, value: Any) -> bool:
        return True


class _gt(PMExtensionCheck):
    def __init__(self, comparatif: Any) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return value > self._comparatif


class _gte(PMExtensionCheck):
    def __init__(self, comparatif: Any) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return value >= self._comparatif


class _lt(PMExtensionCheck):
    def __init__(self, comparatif: Any) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return value < self._comparatif


class _lte(PMExtensionCheck):
    def __init__(self, comparatif: Any) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return value <= self._comparatif


class _eq(PMExtensionCheck):
    def __init__(self, comparatif: Any) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return value == self._comparatif


class _truthy(PMExtensionCheck):
    def __init__(self) -> None:
        super().__init__()

    def check_comply(self, value: Any) -> bool:
        if value:
            return True
        return False


def _get_pm_ext_check(val: Any) -> PMExtensionCheck:
    if isinstance(val, PMExtensionCheck):
        return val
    return _eq(val)


class _or(PMExtensionCheck):
    def __init__(
        self, comparatif1: PMExtensionCheck, comparatif2: PMExtensionCheck
    ) -> None:
        super().__init__()
        self._comparatif1 = _get_pm_ext_check(comparatif1)
        self._comparatif2 = _get_pm_ext_check(comparatif2)

    def check_comply(self, value: Any) -> bool:
        return self._comparatif1.check_comply(
            value=value
        ) or self._comparatif2.check_comply(value=value)


class _and(PMExtensionCheck):
    def __init__(
        self, comparatif1: PMExtensionCheck, comparatif2: PMExtensionCheck
    ) -> None:
        super().__init__()
        self._comparatif1 = _get_pm_ext_check(comparatif1)
        self._comparatif2 = _get_pm_ext_check(comparatif2)

    def check_comply(self, value: Any) -> bool:
        return self._comparatif1.check_comply(
            value=value
        ) and self._comparatif2.check_comply(value=value)


class _empty(PMExtensionCheck):
    def __init__(self) -> None:
        super().__init__()

    def check_comply(self, value: Union[Iterable, Sequence]) -> bool:
        if isinstance(value, Sequence):
            return len(value) == 0
        if isinstance(value, Iterable):
            iterr = iter(value)
            try:
                next(iterr)
            except StopIteration:
                return True
            return False
        return False


class _not(PMExtensionCheck):
    def __init__(self, comparatif: PMExtensionCheck) -> None:
        super().__init__()
        self._comparatif = _get_pm_ext_check(comparatif)

    def check_comply(self, value: Any) -> bool:
        return not self._comparatif.check_comply(value=value)


class _lambda(PMExtensionCheck):
    def __init__(self, comparatif: Callable[[Any], bool]) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return self._comparatif(value)


class _extract(PMExtensionCheck):
    def __init__(
        self,
        comparatif_head: PMExtensionCheck,
        comparatif_tail: PMExtensionCheck,
    ) -> None:
        super().__init__()
        self._comparatif_head = _get_pm_ext_check(comparatif_head)
        self._comparatif_tail = _get_pm_ext_check(comparatif_tail)
        self._calculated = False
        self._head = None
        self._tail = None

    def _set_values(self, value: Any):
        if not self._calculated:
            if isinstance(value, Sequence):
                try:
                    self._head = value[0]
                except IndexError:
                    return
                self._tail = value[1:]
            else:
                iterr = iter(value)
                try:
                    self._head = next(iterr)
                except StopIteration:
                    return
                self._tail = type(value)(iterr)
            self._calculated = True

    def check_comply(self, value: Any) -> bool:
        if isinstance(value, (Iterable, Sequence)):
            self._set_values(value=value)
            if not self._calculated:
                return False
            return self._comparatif_head.check_comply(
                self._head
            ) and self._comparatif_tail.check_comply(self._tail)
        else:
            return False

    def get_value(
        self, keyword: Optional[str], value: Any
    ) -> Tuple[Tuple[Any], Dict[str, Any]]:
        self._set_values(value=value)
        self._calculated = False
        if keyword:
            return (tuple(), {keyword: (self._head, self._tail)})
        return (((self._head, self._tail),), {})
