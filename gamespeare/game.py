"""Module with the classes for representing an adventure game."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from gamespeare.action import (
    Action,
    ActionError,
    MoveAction,
    NoAction,
    QuitAction,
    TakeAction,
    UseAction,
)
from gamespeare.item import Item, LockableContainerItem
from gamespeare.playbook import Playbook


class AdventureGame(ABC):
    """Class for representing an adventure game.

    Attributes
    ----------
    playbook : Playbook
        Game data.
    ending: str
        The reason the game ended, or empty if the game has not ended.

    Parameters
    ----------
    playbook : Playbook
        Game data to use.
    """

    def __init__(self, playbook: Playbook) -> None:
        if not playbook:
            raise ValueError("Missing playbook")
        self.playbook = playbook
        self.ending = ""

    def play(self) -> None:
        """Plays an adventure game."""
        self.prologue()

        while not self.ending:
            action = self.select_action()
            consequences = self.execute_action(action)
            self.present_consequences(consequences)

        self.epilogue()

    @abstractmethod
    def prologue(self) -> None:
        """Introduces the game to the player."""

    @abstractmethod
    def select_action(self) -> Action:
        """Lets the player select an action for the turn.

        Provides the player with relevant information about the current situation and a way to
        pick an action to perform.

        Returns
        -------
        Action
            The `Action` selected by the player.
        """

    @abstractmethod
    def present_consequences(self, consequences: Sequence[str]) -> None:
        """Presents the observable consequences of an action.

        Parameters
        ----------
        consequences: Sequence[str]
            Consequences of the action taken.
        """

    @abstractmethod
    def epilogue(self) -> None:
        """Concludes the game."""

    def execute_action(self, action: Action) -> Sequence[str]:
        """Executes an action, i.e. plays the turn.

        Parameters
        ----------
        action: Action
            The `Action` to perform.

        Returns
        -------
        Sequence[str]:
            The consequences of executing the requested action.

        Raises
        ------
        ActionError:
            If the `Action` is not supported.
        """
        if isinstance(action, NoAction):
            return ()

        if isinstance(action, QuitAction):
            self.ending = "Player gave up!"
            return ("Quitting.",)

        self.playbook.state.update_turn(1)
        consequences = []

        if isinstance(action, UseAction):
            consequences.extend(self._execute_use_action(action))
        elif isinstance(action, MoveAction):
            consequences.extend(self._execute_move_action(action))
        elif isinstance(action, TakeAction):
            consequences.extend(self._execute_take_action(action))
        else:
            raise ActionError(f"Unsupported Action: {action}")

        ending = self.playbook.story.get_ending(self.playbook.state)
        if ending:
            self.ending = ending.reason
            consequences.append(self.ending)

        return consequences

    def _execute_use_action(self, action: UseAction) -> list[str]:
        if not action.item:
            return ["There is no item to use."]

        if not self.playbook.state.inventory.contains_item(action.item):
            return [f"You don't have {action.item.name}."]

        if not action.target:
            return [f"Use {action.item.name} on what?"]

        available_items = self.playbook.get_available_items()
        if not action.target in available_items:
            return [f"Target {action.item.name} not available."]

        if isinstance(action.target, LockableContainerItem):
            return self._execute_use_on_lockable_container(
                container=action.target, key=action.item
            )

        return [f"Can't use {action.item.name} on {action.target.name}."]

    def _execute_use_on_lockable_container(
        self, container: LockableContainerItem, key: Item
    ) -> list[str]:
        result = []

        if not container.key or container.key == key:
            result.append(f"{container.name} unlocked!")
            for item in list(container.get_item_list()):
                self.playbook.add_item_to_location(self.playbook.state.location, item)
                result.append(f"{item.name} discovered!")
        else:
            result.append(f"{key.name} didn't work on {container.name}.")

        return result

    def _execute_move_action(self, action: MoveAction) -> list[str]:
        for direction, destination in self.playbook.state.location.destinations.items():
            if action.destination == destination:
                self.playbook.state.location = action.destination
                return [f"Moved {direction} to {destination.name}"]

        raise ActionError(
            f"Alien destination {action.destination.name} for {self.playbook.state.location.name}."
        )

    def _execute_take_action(self, action: TakeAction) -> list[str]:
        if self.playbook.state.inventory.contains_item(action.item):
            return [f"You already have {action.item.name}"]

        if not self.playbook.state.location.contains_item(action.item):
            return [f"Can't take {action.item.name}, it's not here!"]

        if not action.item.takeable:
            return [f"Can't take {action.item.name}!"]

        self.playbook.add_item_to_inventory(action.item)
        return [f"You now have {action.item.name}"]


class TextAdventureGame(AdventureGame):
    """Class for representing a text adventure game.

    Attributes
    ----------
    playbook : Playbook
        Game data.
        Inherited from `AdventureGame`.
    ending: Ending
        The reason the game ended, or `None` if the game has not ended.
        Inherited from `AdventureGame`.
    """

    def prologue(self) -> None:
        """Introduces the game to the player."""
        print(self.playbook.story.prologue)
        print()

    def select_action(self) -> Action:
        """Lets the player select an action for the turn.

        Provides the player with relevant information about the current situation and a way to
        pick an action to perform.

        Returns
        -------
        Action
            The `Action` selected by the player.
        """
        self._print_location_description()

        while True:
            print("What do you want to do? (HELP for help)")
            command = input("> ").strip()
            upper_command = command.upper()

            if upper_command == "HELP":
                self._print_help()
            else:
                try:
                    if upper_command == "QUIT":
                        return QuitAction()
                    if upper_command.startswith("USE "):
                        return self._parse_use_action(command[4:])
                    if upper_command.startswith("TAKE "):
                        return self._parse_take_action(command[5:])
                    if upper_command.startswith("GO "):
                        return self._parse_go_action(command[3:])
                    raise ActionError(f"No idea what {command} means!")
                except ActionError as e:
                    print(f"Error! {e}")

    def _print_help(self) -> None:
        help_text = f"""
Valid Commands in the Turn of Our Lord {self.playbook.state.turn_no}:

GO [direction]
    Example: GO NORTH
USE [item] ON [other item]
    Example: USE KEY ON CHEST
TAKE [item]
    Example: TAKE SKULL
HELP
    Example: HELP
QUIT
    Example: QUIT
"""
        print(help_text)

    def _print_location_description(self) -> None:
        location = self.playbook.state.location

        print(f"Turn #{self.playbook.state.turn_no}: {location.name}")
        print()
        print(f"{location.description}")
        print()

        items = location.get_item_list()
        if items:
            print("You can see the following items here:")
            for item in items:
                print(item)
            print()

        if location.destinations:
            print("You can see the following exits:")
            for direction in location.destinations:
                print(direction)
            print()

        inventory = self.playbook.state.inventory.get_item_list()
        if inventory:
            print("You have the following items:")
            for item in inventory:
                print(item)
            print()

    def _parse_go_action(self, param: str) -> MoveAction:
        destination = param.upper()
        if not destination in self.playbook.state.location.destinations:
            raise ActionError(f"Invalid destination: {param}")
        return MoveAction(self.playbook.state.location.destinations[destination])

    def _parse_use_action(self, param: str) -> UseAction:
        upper_param = param.upper()

        item = self._extract_item(upper_param)
        target = self._extract_target(upper_param)

        if not item or not target:
            raise ActionError(f"Can't use {param}!")

        return UseAction(item, target)

    def _extract_item(self, param: str) -> Item | None:
        for item in self.playbook.get_available_items():
            if param.startswith(item.name):
                return item
        return None

    def _extract_target(self, param: str) -> Item | None:
        for item in self.playbook.get_available_items():
            if param.endswith(item.name):
                return item
        return None

    def _parse_take_action(self, param: str) -> TakeAction:
        item_name = param.upper()
        try:
            item = self.playbook.state.location.get_item(item_name)
        except ValueError as e:
            raise ActionError(f"Invalid item: {param}") from e
        return TakeAction(item)

    def present_consequences(self, consequences: Sequence[str]) -> None:
        """Presents observable consequences of an action.

        Parameters
        ----------
        consequences: Sequence[str]
            Consequences of the action taken.
        """
        for consequence in consequences:
            print(consequence)

    def epilogue(self) -> None:
        """Concludes the game."""
        print(self.playbook.story.epilogue)
