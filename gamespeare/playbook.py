"""Module with the classes for representing adventure game data."""

import json
from json import JSONDecodeError
from typing import Any

from gamespeare.ending import (
    Ending,
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
from gamespeare.state import State
from gamespeare.story import Story
from gamespeare.utils import GameDataError
from gamespeare.world import World


class Playbook:
    """Class for representing adventure game data.

    Attributes
    ----------
    world: World
        The game world.
    story: Story
        The game story elements.
    state: State
        The game state.

    Parameters
    ----------
    world: World
        The game world.
    story: Story
        The game story elements.
    state: State
        The game state.

    Raises
    --------
    PlaybookError
        Error raised if the `Playbook` contains obvious errors.
    """

    def __init__(self, world: World, story: Story, state: State) -> None:
        world.validate()
        self.world = world

        story.validate(world)
        self.story = story

        state.validate(world)
        self.state = state

    def get_item_by_name(self, name: str) -> Item:
        """Returns the item with the name `name`.

        Returns
        -------
        Item
            The item with the name `name`.

        Raises
        ------
        ValueError
            Error raised if supplied name is not an item in this `Playbook`.
        """
        if name in self.world.items:
            return self.world.items[name]
        raise ValueError(f"Unknown item: {name}")

    def get_location_by_name(self, name: str) -> Location:
        """Returns the location with the name `name`.

        Returns
        -------
        Location
            The location with the name `name`.

        Raises
        ------
        ValueError
            Error raised if supplied name is not a location in this `Playbook`.
        """
        return self.world.locations[name]

    def get_current_location(self) -> Location:
        """Returns the current location.

        Returns
        -------
        Location
            The current location.
        """
        return self.world.locations[self.state.location]

    def get_available_items(self) -> dict[str, Item]:
        """Returns currently available items.

        This is the combination of player inventory and location contents.

        Returns
        -------
        dict of str:Item
            Currently available items, with the name as key.
        """
        item_names = (
            self.state.inventory | self.get_location_by_name(self.state.location).items
        )
        return {item_name: self.get_item_by_name(item_name) for item_name in item_names}

    def add_item_to_inventory(self, item_name: str) -> None:
        """Adds an item to the player's inventory.

        Parameters
        ----------
        item_name: str
            The name of the item to add.

        Raises
        ------
        ValueError
            Error raised if supplied name is not an item in this `Playbook`.
        """
        if not item_name in self.world.items:
            raise ValueError(f"Unknown item {item_name}")

        self.remove_item(item_name)
        self.state.inventory.add(item_name)

    def add_item_to_location(self, location_name: str, item_name: str) -> None:
        """Adds an item to a location.

        Parameters
        ----------
        location_name: str
            The name of the location to add an item to.
        item_name: str
            The name of the item to add.

        Raises
        ------
        ValueError
            Error raised if a supplied name is not present in this `Playbook`.
        """
        if not item_name in self.world.items:
            raise ValueError(f"Unknown item {item_name}")

        self.remove_item(item_name)
        self.get_location_by_name(location_name).items.add(item_name)

    def remove_item(self, item_name: str) -> None:
        """Removes an item from all locations and the inventory.

        Parameters
        ----------
        item_name: str
            The name of the item to add.

        Raises
        ------
        ValueError
            Error raised if supplied name is not an item in this `Playbook`.
        """
        if not item_name in self.world.items:
            raise ValueError(f"Unknown item {item_name}")

        if item_name in self.state.inventory:
            self.state.inventory.remove(item_name)

        for location in self.world.locations.values():
            if item_name in location.items:
                location.items.remove(item_name)

        for container_item in [
            item
            for item in self.world.items
            if (isinstance(item, LockableContainerItem) and item_name in item.contents)
        ]:
            container_item.contents.remove(item_name)


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
        raise GameDataError("Invalid playbook format.") from e
    except FileNotFoundError as e:
        raise GameDataError("Playbook file not found.") from e
    except OSError as e:
        raise GameDataError("Unable to playbook file.") from e

    return from_data(json_data)


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
    world = _create_world(data.get("world"))
    story = _create_story(data.get("story"))
    state = _create_state(data.get("state"))

    return Playbook(world, story, state)


def _create_world(data: Any) -> World:
    items = _create_items(data.get("items"))
    locations = _create_locations(data.get("locations"))

    return World(items, locations)


def _create_items(data: Any) -> dict[str, Item]:
    items = {}

    for entry in data:
        item_class = entry.get("class")
        if item_class == "ITEM":
            item = create_item(entry)
        elif item_class == "CONTAINER":
            item = create_lockable_container_item(entry)
        else:
            raise GameDataError(f"Unsupported Item class: {item_class}")
        items[item.name] = item

    return items


def _create_locations(data: Any) -> dict[str, Location]:
    locations = {}

    for entry in data:
        location_class = entry.get("class")
        if location_class == "LOCATION":
            location = create_location(entry)
        else:
            raise GameDataError(f"Unsupported ending class: {location_class}")

        locations[location.name] = location

    return locations


def _create_story(data: Any) -> Story:
    prologue = _create_string(data.get("prologue"))
    epilogue = _create_string(data.get("epilogue"))
    endings = _create_endings(data.get("endings"))

    return Story(prologue, epilogue, endings)


def _create_string(data: Any) -> str:
    if not data:
        return ""
    return str(data).strip()


def _create_endings(data: Any) -> set[Ending]:
    endings: set[Ending] = set()

    for entry in data:
        ending_class = entry.get("class")
        if ending_class == "RANDOM":
            endings.add(create_random_ending(entry))
        elif ending_class == "TURNS":
            endings.add(create_time_based_ending(entry))
        elif ending_class == "GOAL":
            endings.add(create_goal_based_ending(entry))
        else:
            raise GameDataError(f"Unsupported Ending class: {ending_class}")

    return endings


def _create_state(data: Any) -> State:
    turn_no = int(data.get("turn_no", 1))
    location = _create_string(data.get("location"))
    inventory = _create_inventory(data.get("inventory"))

    return State(turn_no=turn_no, location=location, inventory=inventory)


def _create_inventory(data: Any) -> set[str]:
    return {_create_string(item_name) for item_name in data}
