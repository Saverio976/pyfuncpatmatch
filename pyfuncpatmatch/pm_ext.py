from typing import Any, Callable


class PMExtension:
    def __init__(self) -> None:
        pass


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


class _or(PMExtensionCheck):
    def __init__(self, comparatif1: Any, comparatif2: Any) -> None:
        super().__init__()
        self._comparatif1 = comparatif1
        self._comparatif2 = comparatif2

    def check_comply(self, value: Any) -> bool:
        return self._comparatif1.check_comply(
            value=value
        ) or self._comparatif2.check_comply(value=value)


class _and(PMExtensionCheck):
    def __init__(self, comparatif1: Any, comparatif2: Any) -> None:
        super().__init__()
        self._comparatif1 = comparatif1
        self._comparatif2 = comparatif2

    def check_comply(self, value: Any) -> bool:
        return self._comparatif1.check_comply(
            value=value
        ) and self._comparatif2.check_comply(value=value)


class _lambda(PMExtensionCheck):
    def __init__(self, comparatif: Callable[[Any], bool]) -> None:
        super().__init__()
        self._comparatif = comparatif

    def check_comply(self, value: Any) -> bool:
        return self._comparatif(value)
