"""Module for representing game objects."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable


class GameObjectError(Exception):
    """Exception raised when game object is invalid.

    Attributes
    ----------
        message: str
            Explanation of the error.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass
class GameObject(ABC):
    """An object in the game.

    Attributes
    ----------
    name: str
        Unique name of the game object.
    description: str
        Description of the game object.
    """

    name: str
    description: str

    @abstractmethod
    def validate(self, valid_objects: Iterable[GameObject]):
        """Validates the integrity of the object in relation to valid objects.

        Raises
        ------
        GameDataError
            Raised if the object contains obvious errors.
        """


@dataclass
class GameObjectContainer:
    """A container for game objects.

    Attributes
    ----------
    contents: list of GameObject
        The game objects in the container.
    """

    contents: list[GameObject] = field(default_factory=list[GameObject])

    def contains(self, game_object: str | GameObject) -> bool:
        """Checks if a game object is part of the container's contents.

        Parameters
        ----------
        game_object: str or GameObject
            The object to check if it is part of the contents, eiter a
            `GameObject` or its name.

        Returns
        -------
        bool
            `True` if the item is part of the contents, `False` otherwise.
        """
        for candidate in self.contents:
            if game_object in (candidate, candidate.name):
                return True
        return False

    def add(self, game_object: GameObject, strict: bool = False) -> None:
        """Adds a game object to the container.

        Parameters
        ----------
        game_object: GameObject
            The game object to add.
        strict: bool
            Error will be raised for already present game objects if set to
            `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the object is already present.
        """
        if self.contains(game_object):
            if strict:
                raise ValueError(f"Duplicate game object: {game_object}")
        else:
            self.contents.append(game_object)

        self.contents.sort(key=lambda x: x.name)

    def remove(self, game_object: str | GameObject, strict: bool = False) -> None:
        """Removes a game object from the container.

        Parameters
        ----------
        game_object: GameObject or str
            The item to remove, eiter `GameObject` or its name.
        strict: bool
            Error will be raised for not present game objects if set to `True`.

        Raises
        ------
        ValueError
            Raised if `strict` and the game object is not present.
        """
        try:
            self.contents.remove(self.get(game_object))
        except ValueError as e:
            if strict:
                raise ValueError(f"Non-existing game object: {game_object}") from e

    def get(self, game_object: str | GameObject) -> GameObject:
        """Gets a game object from the container.

        Parameters
        ----------
        game_object: GameObject or str
            The game object to get, eiter `GameObject` or its name.

        Returns
        -------
        GameObject
            The requested game object.

        Raises
        ------
        ValueError
            Raised if the specified game object is not present.
        """
        for candidate in self.contents:
            if game_object in (candidate, candidate.name):
                return candidate

        raise ValueError(f"Non-existing game object: {game_object}")

    def get_list(self) -> list[GameObject]:
        """Gets a list of contained game objects.

        Returns
        -------
        list of GameObject
            New list of game objects.
        """
        return list(self.contents)

    def get_dict(self) -> dict[str, GameObject]:
        """Gets a dictionary of contained game objects.

        Returns
        -------
        list of GameObject
            New dict of game objects with the names as keys and game objects as
            values.
        """
        return {game_object.name: game_object for game_object in self.contents}
