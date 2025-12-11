"""Module with the classes for representing adventure game data."""

import json
from json import JSONDecodeError
from typing import Any

from gamespeare.item import (
    Item,
    LockableContainerItem,
)
from gamespeare.location import Location
from gamespeare.state import State, create_state
from gamespeare.story import Story, create_story
from gamespeare.utils import GameDataError
from gamespeare.world import World, create_world


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
    GameDataError
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
        if not name in self.world.locations:
            raise ValueError(f"Unknown location: {name}")
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
        """Adds an item to the player's inventory if it is takeable.

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

        if self.world.items[item_name].takeable:
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

        all_items = self.world.items.values()
        for container_item in [
            i for i in all_items if (isinstance(i, LockableContainerItem))
        ]:
            if item_name in container_item.contents:
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
    GameDataError
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
    GameDataError
        If the playbook cannot be properly created.
    """
    try:
        world = create_world(data.get("world"))
        story = create_story(data.get("story"))
        state = create_state(data.get("state"))
    except ValueError as e:
        raise GameDataError("Invalid playbook data.") from e

    return Playbook(world, story, state)
