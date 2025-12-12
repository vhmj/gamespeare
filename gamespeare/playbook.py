"""Module with the classes for representing adventure game data."""

import json
from json import JSONDecodeError
from typing import Any

from gamespeare.item import (
    Item,
    ItemContainer,
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

    def get_available_items(self) -> list[Item]:
        """Returns currently available items.

        This is the combination of player inventory and location contents.

        Returns
        -------
        list of Item
            Currently available items.
        """
        available_items = ItemContainer()
        for item in self.state.inventory.items + self.state.location.items.items:
            available_items.add_item(item, strict=False)
        return available_items.items

    def add_item_to_inventory(self, item: Item) -> None:
        """Adds an item to the player's inventory if it is takeable.

        Parameters
        ----------
        item: Item
            The item to add.

        Raises
        ------
        ValueError
            Error raised if supplied name is not an item in this `Playbook`.
        """
        if not self.world.items.contains_item(item):
            raise ValueError(f"Alien item {item}")

        if item.takeable:
            self.remove_item(item)
            self.state.inventory.add_item(item)

    def add_item_to_location(self, location: Location, item: Item) -> None:
        """Adds an item to a location.

        Parameters
        ----------
        location: Location
            The location to add an item to.
        item: Item
            The item to add.

        Raises
        ------
        ValueError
            Error raised if item or location is not present in this `Playbook`.
        """
        if not self.world.items.contains_item(item):
            raise ValueError(f"Alien item {item}")

        if not location in self.world.locations:
            raise ValueError(f"Alien location {location}")

        self.remove_item(item)
        location.items.add_item(item)

    def remove_item(self, item: Item) -> None:
        """Removes an item from all locations and the inventory.

        Parameters
        ----------
        item: Item
            The name of the item to add.

        Raises
        ------
        ValueError
            Error raised if supplied item is not an item in this `Playbook`.
        """
        if not self.world.items.contains_item(item):
            raise ValueError(f"Alien item {item}")

        self.state.inventory.remove_item(item, strict=False)

        for location in self.world.locations:
            location.items.remove_item(item, strict=False)

        for world_item in self.world.items.items:
            if isinstance(world_item, LockableContainerItem):
                world_item.remove_item(item)


def from_file(playbook_file: str) -> Playbook:
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


def from_data(data: Any) -> Playbook:
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
        story = create_story(data.get("story"), world)
        state = create_state(data.get("state"), world)
    except ValueError as e:
        raise GameDataError("Invalid playbook data.") from e

    return Playbook(world, story, state)
