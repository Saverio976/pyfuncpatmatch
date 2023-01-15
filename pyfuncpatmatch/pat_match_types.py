from typing import Any, List, Optional, Union

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
