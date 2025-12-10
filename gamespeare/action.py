"""Module for classes related to actions."""
from abc import ABC


class Action(ABC):
    """Base class for player actions."""


class QuitAction(Action):
    """Action representing player's choice to quit."""

    def __str__(self):
        return "Quit"


class NoAction(Action):
    """Action representing inaction that won't count as a turn."""

    def __str__(self):
        return "No action"


class UseAction(Action):
    """Action representing player's attempt at using item."""

    def __init__(self, item: str, target: str):
        self.item = item
        self.target = target

    def __str__(self):
        return f"Use {self.item} on {self.target}"


class TakeAction(Action):
    """Action representing player's attempt at taking item."""

    def __init__(self, item: str):
        self.item = item

    def __str__(self):
        return f"Take {self.item}"


class MoveAction(Action):
    """Action representing player's attempt at moving locations."""

    def __init__(self, destination: str):
        self.destination = destination

    def __str__(self):
        return f"Go {self.destination}"


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
