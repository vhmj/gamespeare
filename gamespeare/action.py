"""Module for classes and functions related to actions."""

from abc import ABC
from dataclasses import dataclass


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

    def __str__(self):
        return "Quit"


@dataclass
class NoAction(Action):
    """Action representing inaction that won't count as a turn."""

    def __str__(self):
        return "No action"


@dataclass
class UseAction(Action):
    """Action representing player's attempt at using item.

    Attributes
    ----------
    item: str
        Name of the item to use.
    target: str
        Name of the use target item.
    """

    item: str
    target: str

    def __str__(self):
        return f"Use {self.item} on {self.target}"


@dataclass
class TakeAction(Action):
    """Action representing player's attempt at taking item.

    Attributes
    ----------
    item: str
        Name of the item to take.
    """

    item: str

    def __str__(self):
        return f"Take {self.item}"


@dataclass
class MoveAction(Action):
    """Action representing player's attempt at moving locations.

    Attributes
    ----------
    destination: str
        Name of the destination to move to.
    """

    destination: str

    def __str__(self):
        return f"Go {self.destination}"
