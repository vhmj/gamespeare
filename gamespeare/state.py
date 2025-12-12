"""Module for state related classes and functions."""

from dataclasses import dataclass, field
from typing import Any

from gamespeare.item import ItemContainer, get_item_by_name
from gamespeare.location import Location
from gamespeare.utils import GameDataError
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

    def validate(self, world: World) -> None:
        """Validates the integrity of a `State`.

        Parameters
        ----------
        world: World
            The `World` to relate to.

        Raises
        ------
        GameDataError
            Raised if the state contains obvious errors.
        """
        self._validate_round_no()
        self._validate_location(world)
        self._validate_inventory(world)

    def _validate_round_no(self) -> None:
        """Validates the integrity of the round number.

        Raises
        ------
        GameDataError
            Raised if the round number contain obvious errors.
        """
        if self.turn_no < 1:
            raise GameDataError(f"Invalid turn number ({self.turn_no})!")

    def _validate_location(self, world: World) -> None:
        """Validates the integrity of the current location.

        Parameters
        ----------
        world: World
            The `World` to relate to.

        Raises
        ------
        GameDataError
            Raised if the current location contains obvious errors.
        """
        if not self.location in world.locations:
            raise GameDataError(f'Invalid State Location "{self.location}"!')

    def _validate_inventory(self, world: World) -> None:
        """Validates the integrity of the inventory.

        Parameters
        ----------
        world: World
            The `World` to relate to.

        Raises
        ------
        GameDataError
            Raised if the inventory contains obvious errors.
        """
        for item in self.inventory.items:
            if not world.items.contains_item(item):
                raise GameDataError(
                    f'State Inventory Item "{item.name}" does not exist.'
                )


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

    try:
        location_name = str(data["location"]).strip()
    except TypeError as e:
        raise ValueError("Invalid state location type") from e

    for location in world.locations:
        if location.name == location_name:
            return location

    raise ValueError(f"Alien state location: {location_name}")


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
        for item_name in [
            str(item_name).strip() for item_name in data.get("inventory", [])
        ]:
            item = get_item_by_name(name=item_name, items=world.items)
            if not item:
                raise ValueError(f"Alien inventory item: {item_name}")
            inventory.add_item(item)
    except TypeError as e:
        raise ValueError("Invalid inventory data") from e

    return inventory
