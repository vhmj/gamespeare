"""Module for common utility functions."""

from typing import Any, Iterable


class GameDataError(Exception):
    """Exception raised when playbook data is invalid.

    Attributes
    ----------
        message: str
            Explanation of the error.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def get_missing_entries(first: Iterable[str], second: Iterable[str]) -> set[str]:
    """Gets entries that exists in the first sequence but not in the second.

    Parameters
    ----------
    first: iterable of str
        Sequence of values to check.
    second: iterable of str
        Sequence of values to compare against.

    Returns
    -------
    set of str
        Entries that exists in the first sequence but not in the second.
    """
    return set(first) - set(second)


def validate_keyword(keyword: str, title: str) -> None:
    """Validates a keyword to make sure it is suitable for playbook data.

    The keyword must not contain leading or trailing whitespace and must be all
    uppercase.

    Parameters
    ----------
    keyword: str
        The keyword .
    title: str
        Title to include in raised error.

    Raises
    ------
    GameDataError
        Raised if the keyword is invalid.
    """
    validate_string(keyword, title)
    if not keyword.isupper():
        raise GameDataError(f'Non-uppercase {title} "{keyword}".')


def validate_string(string: str, title: str) -> None:
    """Validates a string to make sure it is suitable for playbook data.

    The string must not contain leading or trailing whitespace and must not be
    empty.

    Parameters
    ----------
    string: str
        The string.
    title: str
        Title to include in raised error.

    Raises
    ------
    GameDataError
        Raised if the keyword is invalid.
    """
    stripped = string.strip()
    if not stripped:
        raise GameDataError(f'Empty {title} "{string}".')
    if not stripped == string:
        raise GameDataError(f'Extra whitespace in {title} "{string}".')


def get_string(data: Any, key: str, empty_ok: bool = False) -> str:
    """Extracts a value from a dict-like object and returns it as a string.

    Parameters
    ----------
    data: Any
        The dict-like object.
    key: str
        The key
    empty_ok: bool
        If `True`, an empty string will be returned if the key is missing, or
        if the value is an empty string.

    Returns
    -------
    str
        String stripped from surrounding whitespace.

    Raises
    ------
    ValueError
        Raised if the key was missing or the value without content unless
        `empty_ok` is set.
    """
    string = data.get(key)
    if not string:
        if empty_ok:
            return ""
        raise ValueError(f"Missing {key}")

    clean_string = str(string).strip()
    if not clean_string:
        raise ValueError(f"Empty {key}")

    return clean_string


def get_float(data: Any, key: str) -> float:
    """Extracts a value from a dict-like object and returns it as a float.

    Parameters
    ----------
    data: Any
        The dict-like object.
    key: str
        The key

    Returns
    -------
    float
        The converted value.

    Raises
    ------
    ValueError
        Raised if the value could not be converted.
    """
    try:
        return float(data.get(key))
    except TypeError as e:
        raise ValueError(f"Invalid type for {key}") from e


def get_int(data: Any, key: str) -> int:
    """Extracts a value from a dict-like object and returns it as an integer.

    Parameters
    ----------
    data: Any
        The dict-like object.
    key: str
        The key

    Returns
    -------
    int
        The converted value.

    Raises
    ------
    ValueError
        Raised if the value could not be converted.
    """
    try:
        return int(data.get(key))
    except TypeError as e:
        raise ValueError(f"Invalid type for {key}") from e


def get_bool(data: Any, key: str, default: bool) -> bool:
    """Extracts a value from a dict-like object and returns it as a boolean.

    Parameters
    ----------
    data: Any
        The dict-like object.
    key: str
        The key
    default: bool
        Value to return if the key is not present.

    Returns
    -------
    bool
        `True` is the value is case-insensitive "True",
        `False` is the value is case-insensitive "False".

    Raises
    ------
    ValueError
        Raised if the value could not be converted.
    """
    if not key in data:
        return default
    string = get_string(data, key).upper()
    if string == "FALSE":
        return False
    if string == "TRUE":
        return True

    raise ValueError(f"Invalid type for {key}")
