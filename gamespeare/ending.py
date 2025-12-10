"""Module with the classes for representing endings of a game."""

from abc import ABC, abstractmethod
from random import random
from typing import Any, Iterable

from gamespeare.state import State


class Ending(ABC):
    """Class for representing a way to end a game.

    Attributes
    ----------
    reason: str
        The reason to give when the ending is triggered.

    Parameters
    ----------
    reason: str
        The reason to give when the ending is triggered.
    """

    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason

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
    location: str or None
        The required location, or `None` for no location required.
    items: set of str
        Names of the required items to possess.

    Parameters
    ----------
    reason: str
        The reason to give when the ending is triggered.
    location: str or None
        The required location, empty string or `None` for no location required.
    items: iterable of str or None
        Names of the required items to possess, empty or `None` if no items are required.
    """

    def __init__(
        self,
        reason: str,
        location: str | None = None,
        items: Iterable[str] | None = None,
    ):
        super().__init__(reason)
        self.location = location
        if items:
            self.items = set(items)
        else:
            self.items = set()

    def __repr__(self):
        attributes_repr = (
            f"reason={self.reason}," f"location={self.location}," f"items={self.items})"
        )
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
    return GoalBasedEnding(
        reason=str(data.get("reason")).strip(),
        location=str(data.get("location", "")).strip(),
        items=[str(item).strip() for item in data.get("items", [])],
    )


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
    return TimeBasedEnding(
        reason=str(data.get("reason")), turn_limit=int(data.get("turn_limit"))
    )


class RandomEnding(Ending):
    """A random ending triggering with a specified probability.

    Parameters
    ----------
    reason: str
        The reason given for the triggered ending.
        Inherited from `Ending`.
    probability: float
        The probability of the ending being triggered, in the range [0.0, 1.0].
    """

    def __init__(self, reason: str, probability: float):
        super().__init__(reason)
        self.probability = probability

    def __repr__(self):
        attributes_repr = f"reason={self.reason}," f"probability={self.probability}"
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
    """
    return RandomEnding(
        reason=str(data.get("reason")), probability=float(data.get("probability"))
    )
