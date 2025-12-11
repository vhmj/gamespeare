"""Module with the classes for representing endings of a game."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from random import random
from typing import Any

from gamespeare.state import State


@dataclass
class Ending(ABC):
    """Class for representing a way to end a game.

    Attributes
    ----------
    reason: str
        The reason to give when the ending is triggered.
    """

    reason: str

    @abstractmethod
    def evaluate(self, state: State) -> bool:
        """Evaluates the supplied state of the game to determine if it should end.

        Parameters
        ----------
        state: State
            The game state to evaluate against.

        Returns
        -------
        bool:
            `True` if the condition matches the ending, `False` otherwise.
        """


@dataclass
class GoalBasedEnding(Ending):
    """Class for representing a goal-based way to end a game.

    The location (if given) must match the current location, and all items
    (if given) must be in the player's inventory for the ending to apply.
    If neither is given, the ending will always match.

    Attributes
    ----------
    reason: str
        The reason to give when the ending is triggered.
        Inherited from `Ending`.
    location: str
        The required location, or empty for no location required.
    items: set of str
        Names of the required items to possess.
    """

    location: str = ""
    items: set[str] = field(default_factory=set[str])

    def evaluate(self, state: State) -> bool:
        """Evaluates the supplied state of the game to determine if it should end.

        Parameters
        ----------
        state: State
            The game state to evaluate against.

        Returns
        -------
        bool:
            `True` if the condition matches the ending, `False` otherwise.
        """
        if self.location and not self.location == state.location:
            return False

        if not self.items.issubset(state.inventory):
            return False

        return True


def create_goal_based_ending(data: Any) -> GoalBasedEnding:
    """Creates a random ending triggering with a specified probability.

    Parameters
    ----------
    data: Any
        dict-like object with key-value pair 'reason'/compatible with str.
        Optionally also key-value pair 'location'/compatible with str, and/or
        'items'/compatible with iterable of str.
    """
    reason = _get_string(data, "reason")
    location = _get_string(data, "location", empty_ok=True)
    items = {str(item).strip() for item in data.get("items", [])}

    return GoalBasedEnding(reason=reason, location=location, items=items)


class TimeBasedEnding(Ending):
    """Class for representing a time-based way to end a game.

    Attributes
    ----------
    reason: str
        The reason to give when the ending is triggered.
        Inherited from `Ending`.
    turn_limit: int
        The number of turns allowed before triggering the ending.

    Parameters
    ----------
    reason: str
        The reason to give when the ending is triggered.
    turn_limit: int
        The number of turns allowed before triggering the ending, larger than 1.
    """

    def __init__(self, reason: str, turn_limit: int):
        super().__init__(reason)
        self.turn_limit = turn_limit

    def __repr__(self):
        attributes_repr = f"reason={self.reason}," f"turn_limit={self.turn_limit}"
        return f"{type(self).__name__}({attributes_repr})"

    def evaluate(self, state: State) -> bool:
        """Evaluates the supplied state of the game to determine if it should end.

        Parameters
        ----------
        state: State
            The game state to evaluate against.

        Returns
        -------
        bool:
            `True` if the condition matches the ending, `False` otherwise.
        """
        return state.turn_no >= self.turn_limit


def create_time_based_ending(data: Any) -> TimeBasedEnding:
    """Creates a time based ending triggering a specified amount of turns.

    Parameters
    ----------
    data: Any
        dict-like object with key-value pair 'turn_limit'/compatible with int
        (larger than 1), and 'reason'/compatible with str.
    """
    reason = _get_string(data, "reason")
    turn_limit = _get_int(data, "turn_limit")
    return TimeBasedEnding(reason=reason, turn_limit=turn_limit)


@dataclass
class RandomEnding(Ending):
    """A random ending triggering with a specified probability.

    Attributes
    ----------
    reason: str
        The reason given for the triggered ending.
        Inherited from `Ending`.
    probability: float
        The probability of the ending being triggered, in the range [0.0, 1.0].
    """

    probability: float

    def evaluate(self, state: State) -> bool:
        """Evaluates the supplied state of the game to determine if it should end.

        Parameters
        ----------
        state: State
            The game state to evaluate against.

        Returns
        -------
        bool:
            `True` with the specified probability, `False` otherwise.
        """
        return random() >= 1.0 - self.probability


def create_random_ending(data: Any) -> RandomEnding:
    """Creates a random ending triggering with a specified probability.

    Parameters
    ----------
    data: Any
        dict-like object with key-value pair 'probability'/compatible with float
        in the range [0.0, 1.0], and 'reason'/compatible with str.

    Raises
    ------
    ValueError
        Raised if there is a problem with `data`.
    """
    reason = _get_string(data, "reason")
    probability = _get_float(data, "probability")

    return RandomEnding(reason=reason, probability=probability)


def _get_string(data: Any, key: str, empty_ok: bool = False) -> str:
    string = data.get(key)
    if not string:
        if empty_ok:
            return ""
        raise ValueError(f"Missing {key}")

    clean_string = str(string).strip()
    if not clean_string:
        raise ValueError(f"Empty {key}")

    return clean_string


def _get_float(data: Any, key: str) -> float:
    try:
        return float(data.get(key))
    except TypeError as e:
        raise ValueError(f"Invalid type for {key}") from e


def _get_int(data: Any, key: str) -> int:
    try:
        return int(data.get(key))
    except TypeError as e:
        raise ValueError(f"Invalid type for {key}") from e
