"""Module for world related classes and functions."""

from dataclasses import dataclass
from typing import Any

from gamespeare.item import ItemContainer, create_items
from gamespeare.location import LocationContainer, create_locations


@dataclass
class World(LocationContainer, ItemContainer):
    """Class for storing the contents of the game world.

    Attributes
    ----------
    contents: list of GameObject
        The contained game objects.
        Inherited from `GameObjectContainer`.
    """

    def validate(self) -> None:
        """Validates the integrity of a `World`.

        Raises
        ------
        GameDataError
            Raised if the world contains obvious errors.
        """
        for game_object in self.contents:
            game_object.validate(self.contents)


def create_world(data: Any) -> World:
    """Creates a `World` from dict-like data.

    Parameters
    ----------
    data: Any
        A dict-like object with the key `items` with a list of items
        (see `item.create_items()`) as value, and the key `locations` with a
        list of locations (see `location.create_locations()`) as value.

    Returns
    -------
    World
        A `World` initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    if not data:
        raise ValueError("Missing world data")

    items = create_items(data.get("items"))
    locations = create_locations(data.get("locations"), items=items)

    return World(list(locations + items))
