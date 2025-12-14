"""Module with the classes for representing endings of a game."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from random import random
from typing import Any

from gamespeare.item import ItemContainer
from gamespeare.location import Location
from gamespeare.state import State
from gamespeare.utils import get_float, get_int, get_string
from gamespeare.world import World


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
    location: Location or None
        The required location, or `None` for no location required.
    items: ItemContainer
        Required items to possess.
    """

    location: Location | None = None
    items: ItemContainer = field(default_factory=ItemContainer)

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

        for item in self.items.get_item_list():
            if not state.inventory.contains_item(item):
                return False

        return True


def create_goal_based_ending(data: Any, world: World) -> GoalBasedEnding:
    """Creates a random ending triggering with a specified probability.

    Parameters
    ----------
    data: Any
        dict-like object with key-value pair 'reason'/compatible with str.
        Optionally also key-value pair 'location'/compatible with str, and/or
        'items'/compatible with iterable of str.
    world: World
        The `World` to relate to.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    reason = get_string(data, "reason")

    location_name = get_string(data, "location", empty_ok=True)
    if location_name:
        location = world.get_location(location_name)
    else:
        location = None

    items = ItemContainer()
    for entry in data.get("items", []):
        item_name = str(entry).strip()
        items.add_item(world.get_item(item_name))

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

    def __init__(self, reason: str, turn_limit: int) -> None:
        super().__init__(reason)
        self.turn_limit = turn_limit

    def __repr__(self) -> str:
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
    reason = get_string(data, "reason")
    turn_limit = get_int(data, "turn_limit")
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
    reason = get_string(data, "reason")
    probability = get_float(data, "probability")

    return RandomEnding(reason=reason, probability=probability)


def create_endings(data: Any, world: World) -> list[Ending]:
    """Creates endings from a list of dict-like data.

    The key `class` is required, and the supported values are:

    * `GOAL` - See `create_goal_based_ending()` for additional requirements.
    * `TURNS` - See `create_time_based_ending()` for additional requirements.
    * `RANDOM` - See `create_random_ending()` for additional requirements.

    Parameters
    ----------
    data: Any
        A dict-like object with the key `class` and additional ending data.
    world: World
        The `World` to relate to.

    Returns
    -------
    list[Ending]
        A list of `Ending` initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    endings: list[Ending] = []

    for entry in data:
        ending_class = entry.get("class")
        if ending_class == "RANDOM":
            endings.append(create_random_ending(entry))
        elif ending_class == "TURNS":
            endings.append(create_time_based_ending(entry))
        elif ending_class == "GOAL":
            endings.append(create_goal_based_ending(entry, world))
        else:
            raise ValueError(f"Unsupported Ending class: {ending_class}")

    return endings
