"""Module for world related classes and functions."""

from dataclasses import dataclass, field
from typing import Any

from gamespeare.item import ItemContainer, LockableContainerItem, create_items
from gamespeare.location import Location, create_locations
from gamespeare.utils import (
    GameDataError,
    validate_keyword,
    validate_string,
)


@dataclass
class World:
    """Class for storing the contents of the game world.

    Attributes:
        items: ItemContainer
            All existing items.
        locations: list of Location
            All existing locations.
    """

    locations: list[Location]
    items: ItemContainer = field(default_factory=ItemContainer)

    def validate(self) -> None:
        """Validates the integrity of a `World`.

        Raises
        ------
        GameDataError
            Raised if the world contains obvious errors.
        """
        self._validate_items()
        self._validate_locations()

    def _validate_items(self) -> None:
        """Validates items.

        Raises
        ------
        GameDataError
            Raised if the items in the world contains obvious errors.
        """
        for item in self.items.items:
            validate_keyword(item.name, "Item name")
            validate_string(item.description, "Item description")

            if isinstance(item, LockableContainerItem):
                if item.key and not self.items.contains_item(item.key):
                    reason = f'Key "{item.key}\” for Item "{item.name}" does not exist.'
                    raise GameDataError(reason)

                for contained_item in item.items:
                    if not self.items.contains_item(contained_item):
                        reason = (
                            f'Contained Item "{contained_item.name}" '
                            f'for Item "{item.name}" does not exist.'
                        )
                        raise GameDataError(reason)

    def _validate_locations(self) -> None:
        """Validates locations.

        Raises
        ------
        GameDataError
            Raised if the locations in the world contains obvious errors.
        """
        if not self.locations:
            raise GameDataError("Missing locations!")

        for location in self.locations:
            validate_keyword(location.name, "Location name")
            validate_string(location.description, "Location description")

            for item in location.items.items:
                if not self.items.contains_item(item):
                    raise GameDataError(
                        f'Location item "{item.name}" for "{location.name}" does not exist.'
                    )

            for direction, destination in location.destinations.items():
                validate_keyword(direction, "Location destination direction")
                if destination not in self.locations:
                    reason = (
                        f'Location destination "{destination.name}" '
                        f'for "{location.name}" does not exist.'
                    )
                    raise GameDataError(reason)


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

    return World(locations=locations, items=items)
