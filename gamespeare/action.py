"""Module for classes and functions related to actions."""

from abc import ABC
from dataclasses import dataclass

from gamespeare.item import Item
from gamespeare.location import Location


class ActionError(Exception):
    """Exception raised when an action is invalid.

    Attributes
    ----------
    message: str
        Explanation of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


@dataclass
class Action(ABC):
    """Base class for player actions."""


@dataclass
class QuitAction(Action):
    """Action representing player's choice to quit."""

    def __str__(self) -> str:
        return "Quit"


@dataclass
class NoAction(Action):
    """Action representing inaction that won't count as a turn."""

    def __str__(self) -> str:
        return "No action"


@dataclass
class UseAction(Action):
    """Action representing player's attempt at using item.

    Attributes
    ----------
    item: Item
        The item to use.
    target: Item
        The target item.
    """

    item: Item
    target: Item

    def __str__(self) -> str:
        return f"Use {self.item} on {self.target}"


@dataclass
class TakeAction(Action):
    """Action representing player's attempt at taking item.

    Attributes
    ----------
    item: Item
        The item to take.
    """

    item: Item

    def __str__(self) -> str:
        return f"Take {self.item.name}"


@dataclass
class MoveAction(Action):
    """Action representing player's attempt at moving locations.

    Attributes
    ----------
    destination: Location
        The location to move to.
    """

    destination: Location

    def __str__(self) -> str:
        return f"Go to {self.destination.name}"
