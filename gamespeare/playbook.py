"""Module with the classes for representing adventure game data."""

import json
from json import JSONDecodeError
from typing import Any, Iterable

from gamespeare.ending import Ending, GoalBasedEnding, RandomEnding, TimeBasedEnding
from gamespeare.gameobject import GameObject
from gamespeare.item import (
    Item,
    ItemContainer,
)
from gamespeare.location import Location
from gamespeare.state import State, create_state
from gamespeare.story import Story, create_story
from gamespeare.utils import GameDataError, validate_keyword, validate_string
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
        self.world = world
        self.story = story
        self.state = state
        self.validate()

    def validate(self) -> None:
        """Validates the integrity of a `Playbook`.

        Raises
        ------
        GameDataError
            Raised if the playbook contains obvious errors.
        """
        self._validate_world()
        self._validate_story()
        self._validate_state()

    def _validate_world(self):
        for game_object in self.world.contents:
            self._validate_game_object(game_object)

        n_entries = len(self.world.contents)
        n_names = len(self.world.get_dict().keys())
        if not n_entries == n_names:
            raise GameDataError(f"{n_entries} and {n_names} mismatch")

    def _validate_game_object(self, game_object: GameObject):
        validate_keyword(game_object.name, "Name")
        validate_string(game_object.description, "Description")

        game_object.validate(self.world.contents)

        if isinstance(game_object, ItemContainer):
            self._validate_item_container(game_object)
        if isinstance(game_object, Location):
            self._validate_location(game_object)

    def _validate_item_container(self, item_container: ItemContainer):
        for item in item_container.get_item_list():
            if not self.world.contains_item(item):
                raise GameDataError(f"Alien item: {item}")

    def _validate_location(self, location: Location):
        for direction, destination in location.destinations.items():
            validate_keyword(direction, "Direction")

            if not self.world.contains_location(location):
                raise GameDataError(f"Alien destination location: {location}")

    def _validate_story(self) -> None:
        validate_string(self.story.prologue, "Prologue")
        validate_string(self.story.epilogue, "Epilogue")
        self._validate_endings(self.story.endings)

    def _validate_endings(self, endings: Iterable[Ending]) -> None:
        if not endings:
            raise GameDataError("No endings")

        for ending in endings:
            validate_string(ending.reason, "Ending")

            if isinstance(ending, GoalBasedEnding):
                self._validate_goal_based_ending(ending)
            elif isinstance(ending, TimeBasedEnding):
                self._validate_time_based_ending(ending)
            elif isinstance(ending, RandomEnding):
                self._validate_random_ending(ending)
            else:
                raise GameDataError(f"Unsupported ending: {ending}")

    def _validate_goal_based_ending(self, ending: GoalBasedEnding) -> None:
        if ending.location and not self.world.contains_location(ending.location):
            raise GameDataError(f'Ending location "{ending.location}" does not exist.')

        for item in ending.items.get_item_list():
            if not self.world.contains_item(item):
                raise GameDataError(f"Alien ending item: {item.name}")

    def _validate_time_based_ending(self, ending: TimeBasedEnding) -> None:
        if ending.turn_limit < 1:
            raise GameDataError(f"Ending turn limit {ending.turn_limit} too low.")

    def _validate_random_ending(self, ending: RandomEnding) -> None:
        if ending.probability > 1.0 or ending.probability < 0.0:
            message = f"Ending probability {ending.probability} not in [0.0, 1.1]."
            raise GameDataError(message)

    def _validate_state(self) -> None:
        self._validate_round_no()
        self._validate_current_location()
        self._validate_inventory()

    def _validate_round_no(self) -> None:
        if self.state.turn_no < 1:
            raise GameDataError(f"Invalid turn number: {self.state.turn_no}")

    def _validate_current_location(self) -> None:
        if not self.world.contains_location(self.state.location):
            raise GameDataError(f"Invalid State Location: {self.state.location}")

    def _validate_inventory(self) -> None:
        for entry in self.state.inventory.contents:
            if not isinstance(entry, Item):
                message = f"Non-item in inventory: {entry}"
                raise GameDataError(message)

            if not self.world.contains_item(entry):
                message = f"Alien inventory item: {entry.name}"
                raise GameDataError(message)

    def get_available_items(self) -> list[Item]:
        """Returns currently available items.

        This is the combination of player inventory and location contents.

        Returns
        -------
        list of Item
            Currently available items.
        """
        available_items = ItemContainer()
        for item in (
            self.state.inventory.get_item_list() + self.state.location.get_item_list()
        ):
            available_items.add_item(item, strict=False)
        return available_items.get_item_list()

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
        if not self.world.contains_item(item):
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
        if not self.world.contains_item(item):
            raise ValueError(f"Alien item {item}")

        if not self.world.contains_location(location):
            raise ValueError(f"Alien location {location}")

        self.remove_item(item)
        location.add_item(item)

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
        if not self.world.contains_item(item):
            raise ValueError(f"Alien item {item}")

        self.state.inventory.remove_item(item, strict=False)

        for game_object in self.world.contents:
            if isinstance(game_object, ItemContainer):
                game_object.remove_item(item, strict=False)


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
