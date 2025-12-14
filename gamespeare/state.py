"""Module for state related classes and functions."""

from dataclasses import dataclass, field
from typing import Any

from gamespeare.item import ItemContainer
from gamespeare.location import Location
from gamespeare.world import World


@dataclass
class State:
    """Class for storing a player's current state.

    Attributes:
        turn_no: int
            The current round number.
        location: Location
            The current location.
        inventory: ItemContainer
            The items in the player's possession.
    """

    turn_no: int
    location: Location
    inventory: ItemContainer = field(default_factory=ItemContainer)

    def update_turn(self, delta: int = 1) -> None:
        """Updates the current turn number.

        Parameters
        ----------
        delta: int
            Number of turns to add/remove.
        """
        self.turn_no = max(1, self.turn_no + delta)


def create_state(data: Any, world: World) -> State:
    """Creates a `State` from dict-like data.

    Parameters
    ----------
    data: Any
        A dict-like object with the key `turn_no` with a positive `int` value,
        the key and `location` with non-empty `str` value representing a location
        name, and optionally the key `inventory` with a list of non-empty `str`
        values representing item names.
    world: World
        The `World` to relate to.

    Returns
    -------
    State
        A `State` initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    if not data:
        raise ValueError("Missing state data")

    turn_no = _create_turn_no(data)
    location = _create_location(data, world)
    inventory = _create_inventory(data, world)

    return State(turn_no=turn_no, location=location, inventory=inventory)


def _create_turn_no(data: Any, default: int = 1) -> int:
    """Extracts turn number value from a dict-like object.

    Parameters
    ----------
    data: Any
        The dict-like object, optionally with the key `turn_no` with an int
        compatible value.
    default: int
        Turn number to use if turn_no is missing.

    Returns
    -------
    int
        The turn number.

    Raises
    ------
    ValueError
        Raised if the turn number could not be determined.
    """
    try:
        return int(data.get("turn_no", default))
    except TypeError as e:
        raise ValueError("Invalid type for turn_no") from e


def _create_location(data: Any, world: World) -> Location:
    """Creates the location from a dict-like object.

    Parameters
    ----------
    data: Any
        An iterable object with non-empty `str` values representing item names.
    world: World
        The `World` to relate to.

    Returns
    -------
    Location
        A location initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    if not "location" in data:
        raise ValueError("Missing state location")

    return world.get_location(data["location"])


def _create_inventory(data: Any, world: World) -> ItemContainer:
    """Creates the inventory from iterable data.

    Parameters
    ----------
    data: Any
        An iterable object with non-empty `str` values representing item names.
    world: World
        The `World` to relate to.

    Returns
    -------
    ItemContainer
        An inventory initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    inventory = ItemContainer()

    try:
        for item_name in data.get("inventory", []):
            item = world.get_item(item_name)
            if not item:
                raise ValueError(f"Alien inventory item: {item_name}")
            inventory.add_item(item)
    except TypeError as e:
        raise ValueError("Invalid inventory data") from e

    return inventory
