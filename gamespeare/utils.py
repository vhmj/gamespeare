"""Module for common utility functions."""

from typing import Iterable


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
    PlaybookError
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
    PlaybookError
        Raised if the keyword is invalid.
    """
    stripped = string.strip()
    if not stripped:
        raise GameDataError(f'Empty {title} "{string}".')
    if not stripped == string:
        raise GameDataError(f'Extra whitespace in {title} "{string}".')
