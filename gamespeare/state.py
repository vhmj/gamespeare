"""Module for state related classes and functions."""

from dataclasses import dataclass
from typing import Any

from gamespeare.utils import (
    GameDataError,
    get_int,
    get_missing_entries,
    get_string,
    validate_keyword,
)
from gamespeare.world import World


@dataclass
class State:
    """Class for storing a player's current state.

    Attributes:
        turn_no: int
            The current round number.
        location: str
            The name of the current location.
        inventory: set of str
            The names of the items in the player's possession.
    """

    turn_no: int
    location: str
    inventory: set[str]

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
        validate_keyword(self.location, "State Location")
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
        for missing_item_name in get_missing_entries(self.inventory, world.items):
            raise GameDataError(
                f'State Inventory Item "{missing_item_name}"  does not exist.'
            )


def create_state(data: Any) -> State:
    """Creates a `State` from dict-like data.

    Parameters
    ----------
    data: Any
        A dict-like object with the key `turn_no` with a positive `int` value,
        the key and `location` with non-empty `str` value representing a location
        name, and optionally the key `inventory` with a list of non-empty `str`
        values representing item names.

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

    turn_no = get_int(data, "turn_no")
    location = get_string(data, "location")
    inventory = _create_inventory(data.get("inventory"))

    return State(turn_no=turn_no, location=location, inventory=inventory)


def _create_inventory(data: Any) -> set[str]:
    """Creates an inventory list from iterable data.

    Parameters
    ----------
    data: Any
        An iterable object with non-empty `str` values representing item names.

    Returns
    -------
    Set of str
        An inventory initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    if not data:
        return set()

    try:
        return {str(item_name).strip() for item_name in data}
    except TypeError as e:
        raise ValueError("Invalid inventory data") from e
