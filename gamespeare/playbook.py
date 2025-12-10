"""Module with the classes for representing adventure game data."""

import json
from json import JSONDecodeError
from typing import Any

from gamespeare.ending import (
    Ending,
    GoalBasedEnding,
    create_goal_based_ending,
    create_random_ending,
    create_time_based_ending,
)
from gamespeare.item import (
    Item,
    LockableContainerItem,
    create_item,
    create_lockable_container_item,
)
from gamespeare.location import Location, create_location


class PlaybookError(Exception):
    """Exception raised when game data is invalid.

    Attributes
    ----------
        message: str
            Explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class Playbook:
    """Class for representing adventure game data.

    Attributes
    ----------
    locations: dict of str:Location
        Available locations in the game.
    items: dict of str:Item
        Available items in the game.
    endings: list of Ending
        Possible endings to the game.
    start: str
        Name of the starting location.
    location: Location
        The current location.
    inventory: list of str
        The name of the items in the player's possession.
    prologue: str
        Prologue text to get the game started.
    epilogue: str
        Epilogue text to finish the game.

    Parameters
    ----------
    locations: dict of str:Location
        Available locations in the game.
    items: dict of str:Item or None
        Available items in the game.
    endings: list of Ending
        Possible endings to the game.
    start: str
        The name of the starting location.
    inventory: list of str or None
        The name of the items in the player's possession.
    prologue: str
        Prologue text to get the game started.
    epilogue: str
        Epilogue text to finish the game.

    Raises
    --------
    PlaybookError:
        If the playbook contains obvious errors.
    """

    def __init__(
        self,
        start: str,
        prologue: str,
        epilogue: str,
        locations: dict[str, Location],
        endings: list[Ending],
        items: dict[str, Item] | None = None,
        inventory: list[str] | None = None,
    ) -> None:
        self.locations = locations
        self.start = start

        if items:
            self.items = items
        else:
            self.items = {}

        self.endings = list(endings)

        if inventory:
            self.inventory = list(inventory)
        else:
            self.inventory = []

        self.prologue = prologue
        self.epilogue = epilogue

        self._validate_initialized_game()
        self.location = self.locations[start]

    def get_item_by_name(self, name: str) -> Item:
        return self.items[name]

    def get_location_by_name(self, name: str) -> Location:
        return self.locations[name]

    def get_available_items(self) -> dict[str, Item]:
        item_names = self.inventory + self.location.items
        return {item_name: self.get_item_by_name(item_name) for item_name in item_names}

    def add_item_to_inventory(self, item_name: str) -> None:
        if not item_name in self.items:
            raise ValueError(f"Unknown item {item_name}")

        self.remove_item(item_name)
        self.inventory.append(item_name)

    def add_item_to_location(self, location: Location, item_name: str) -> None:
        if not item_name in self.items:
            raise ValueError(f"Unknown item {item_name}")

        self.remove_item(item_name)
        location.items.append(item_name)

    def remove_item(self, item_name: str) -> None:
        if item_name in self.inventory:
            self.inventory.remove(item_name)

        for location in self.locations.values():
            if item_name in location.items:
                location.items.remove(item_name)

        for item in self.items:
            if isinstance(item, LockableContainerItem):
                if item_name in item.contents:
                    item.contents.remove(item_name)

    def _validate_initialized_game(self) -> None:
        """Validates the integrity of an initialized `Playbook`.

        Raises
        ------
        PlaybookError
            If the playbook contains obvious errors.
        """
        self._validate_start_conditions()
        self._validate_items()
        self._validate_locations()
        self._validate_end_conditions()

    def _validate_items(self) -> None:
        for item in self.items.values():
            self._validate_item(item)

    def _validate_item(self, item: Item) -> None:
        if isinstance(item, LockableContainerItem):
            if item.key and not item.key in self.items:
                raise PlaybookError(f"Key {item.key} is undefined.")

            for contained_item_name in item.contents:
                contained_item = self.items.get(contained_item_name)
                if not contained_item:
                    raise PlaybookError(
                        f"Contained item {contained_item_name} is undefined."
                    )
                self._validate_item(contained_item)

    def _validate_locations(self) -> None:
        if not self.locations:
            raise PlaybookError("Missing locations!")

        for location in self.locations.values():
            for item_name in location.items:
                if item_name not in self.items:
                    raise PlaybookError(f"Item {item_name} is undefined.")

            for destination_name in location.destinations.values():
                if destination_name not in self.locations:
                    raise PlaybookError(f"Location {destination_name} is undefined.")

    def _validate_start_conditions(self) -> None:
        if not self.prologue:
            raise PlaybookError("Missing prologue!")

        if not self.start in self.locations:
            raise PlaybookError("Missing valid initial location!")

        for item_name in self.inventory:
            if not item_name in self.items:
                raise PlaybookError(f"Inventory item {item_name} is undefined.")

    def _validate_end_conditions(self) -> None:
        if not self.epilogue:
            raise PlaybookError("Missing epilogue!")

        if not self.endings:
            raise PlaybookError("No endings specified!")

        for ending in self.endings:
            if isinstance(ending, GoalBasedEnding):
                for item_name in ending.items:
                    if not item_name in self.items:
                        raise PlaybookError(f"Key {item_name} is undefined.")


def from_file(playbook_file: str):
    """Creates a playbook based on data from a file.

    Parameters
    ----------
    playbook_file: str
        Path to the JSON file to initialize a playbook with.

    Returns
    -------
    Playbook:
        An initialized playbook.

    Raises
    --------
    PlaybookError
        If the playbook file cannot be properly loaded.
    """
    try:
        with open(playbook_file, mode="r", encoding="utf-8") as input_file:
            json_data = json.load(input_file)
    except JSONDecodeError as e:
        raise PlaybookError("Invalid playbook format.") from e
    except FileNotFoundError as e:
        raise PlaybookError("Playbook file not found.") from e
    except OSError as e:
        raise PlaybookError("Unable to playbook file.") from e

    return from_data(json_data)


def _create_string(data: Any) -> str:
    return str(data).strip()


def _create_items(data: Any) -> dict[str, Item]:
    items = {}

    for entry in data:
        item_class = entry.get("class")
        if item_class == "ITEM":
            item = create_item(entry)
        elif item_class == "CONTAINER":
            item = create_lockable_container_item(entry)
        else:
            raise ValueError(f"Unsupported ending class: {item_class}")
        items[item.name] = item

    return items


def _create_locations(data: Any) -> dict[str, Location]:
    locations = {}

    for entry in data:
        location_class = entry.get("class")
        if location_class == "LOCATION":
            location = create_location(entry)
        else:
            raise ValueError(f"Unsupported ending class: {location_class}")

        locations[location.name] = location
    return locations


def _create_endings(data: Any) -> list[Ending]:
    endings: list[Ending] = []

    for entry in data:
        ending_class = entry.get("class")
        if ending_class == "RANDOM":
            endings.append(create_random_ending(entry))
        elif ending_class == "TURNS":
            endings.append(create_time_based_ending(entry))
        elif ending_class == "GOAL":
            endings.append(create_goal_based_ending(entry))
        else:
            raise ValueError(f"Unsupported ending class: {ending_class}")

    return endings


def _create_inventory(data: Any) -> list[str]:
    return [str(item) for item in data]


def from_data(data: Any):
    """Creates a playbook based on data compatible with the JSON playbook format.

    Parameters
    ----------
    data: Any
        Data to initialize a playbook with.

    Returns
    -------
    Playbook:
        An initialized playbook.

    Raises
    --------
    PlaybookError
        If the playbook cannot be properly created.
    """
    return Playbook(
        start=_create_string(data.get("start")),
        prologue=_create_string(data.get("prologue")),
        epilogue=_create_string(data.get("epilogue")),
        inventory=_create_inventory(data.get("inventory")),
        items=_create_items(data.get("items")),
        locations=_create_locations(data.get("locations")),
        endings=_create_endings(data.get("endings")),
    )
