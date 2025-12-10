"""Module for world related classes and functions."""

from dataclasses import dataclass

from gamespeare.item import Item, LockableContainerItem
from gamespeare.location import Location
from gamespeare.utils import (
    GameDataError,
    get_missing_entries,
    validate_keyword,
    validate_string,
)


@dataclass
class World:
    """Class for storing the contents of the game world.

    Attributes:
        items: dict of str:Item
            All existing items, with the item name as key.
        locations: dict of str:Location
            All existing locations, with the location name as key.
    """

    items: dict[str, Item]
    locations: dict[str, Location]

    def validate(self) -> None:
        """Validates the integrity of a `World`.

        Raises
        ------
        PlaybookError
            Raised if the world contains obvious errors.
        """
        self._validate_items()
        self._validate_locations()

    def _validate_items(self) -> None:
        """Validates items.

        Raises
        ------
        PlaybookError
            Raised if the items in the world contains obvious errors.
        """
        for item_name, item in self.items.items():
            validate_keyword(item_name, "Item name")
            if not item_name == item.name:
                reason = (
                    f'Name mismatch for Item name: "{item_name}" vs. "{item.name}".'
                )
                raise GameDataError(reason)

            if isinstance(item, LockableContainerItem):
                if item.key and not item.key in self.items:
                    reason = f'Key "{item.key}\” for Item "{item_name}" does not exist.'
                    raise GameDataError(reason)

                for contained_item_name in item.contents:
                    if not contained_item_name in self.items:
                        reason = (
                            f'Contained Item "{contained_item_name}" '
                            f'for Item "{item_name}" does not exist.'
                        )
                        raise GameDataError(reason)

    def _validate_locations(self) -> None:
        """Validates locations.

        Raises
        ------
        PlaybookError
            Raised if the locations in the world contains obvious errors.
        """
        if not self.locations:
            raise GameDataError("Missing locations!")

        for location_name, location in self.locations.items():
            validate_keyword(location_name, "Location name")
            if not location_name == location.name:
                raise GameDataError(
                    f'Name mismatch for Item name: "{location_name}" vs. "{location.name}".'
                )

            validate_string(location.description, "Location description")

            for missing_item_name in get_missing_entries(location.items, self.items):
                raise GameDataError(
                    f'Location item "{missing_item_name}" for "{location_name}" does not exist.'
                )

            for direction, destination_name in location.destinations.items():
                validate_keyword(direction, "Location destination direction")
                if destination_name not in self.locations:
                    reason = (
                        f'Location destination "{destination_name}" '
                        f'for "{location_name}" does not exist.'
                    )
                    raise GameDataError(reason)
