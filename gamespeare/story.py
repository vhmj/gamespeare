"""Module for story related classes and functions."""

from dataclasses import dataclass
from typing import Any

from gamespeare.ending import (
    Ending,
    create_endings,
)
from gamespeare.state import State
from gamespeare.world import World


@dataclass
class Story:
    """Class for story elements of the game.

    prologue: str
        Prologue text to get the game started.
    epilogue: str
        Epilogue text to finish the game.
    endings: list of Ending
        Possible endings to the game.
    """

    prologue: str
    epilogue: str
    endings: list[Ending]

    def get_ending(self, state: State) -> Ending | None:
        """Checks ending for a specific state.

        Parameters
        ----------
        state: State
            The `State` to check ending for.

        Returns
        -------
        Ending or None
            An ending that matches the supplied state, or None if no ending applied.
        """
        for potential_ending in self.endings:
            if potential_ending.evaluate(state):
                return potential_ending
        return None


def create_story(data: Any, world: World) -> Story:
    """Creates a `Story` from dict-like data.

    Parameters
    ----------
    data: Any
        A dict-like object with the keys `prologue` and `epilogue` with `str`
        values, and the key `endings` with a list of endings
        (see `Ending.create_endings()`)
    world: World
        The `World` to relate to.

    Returns
    -------
    Story
        A `Story` initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    if not data:
        raise ValueError("Missing story data")

    try:
        prologue = data["prologue"]
        epilogue = data["epilogue"]
        endings = create_endings(data["endings"], world)
    except KeyError as e:
        raise ValueError("Missing key in data") from e

    return Story(prologue, epilogue, endings)
