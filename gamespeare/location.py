"""Module for representing locations."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Location:
    """Class representing a location in a game.

    Attributes
    ----------
    name: str
        Unique name for the location.
    description: str
        Description of the location.
    destinations: dict of str: str
        Possible destinations to go from this location, with the key being the direction and the
        value the name of the destination.
    items: set of str
        Items present in the location.
    """

    name: str
    description: str
    destinations: dict[str, str] = field(default_factory=dict[str, str])
    items: set[str] = field(default_factory=set[str])


def create_location(data: Any) -> Location:
    """Creates a `Location` from a dict-like object.

    The input could for example look like this:

    {
      "name": "ROOM",
      "description": "A room in the castle",
      "items": [
        "CHEST", "SKULL", "KEY"
      ],
      "destinations": {
        "NORTH": "HALL"
        "WEST": "CLOSET"
      }
    }

    Parameters
    ----------
    data: Any
        dict-like object with keys 'name' and 'description' with string values, and
        optionally 'items', with a list of string values, and 'destinations', a dict
        with string keys and values.
    """
    name = str(data.get("name")).strip()
    description = str(data.get("description")).strip()
    items = {str(item).strip() for item in data.get("items", [])}
    destinations = {
        str(k).strip(): str(v).strip()
        for (k, v) in data.get("destinations", {}).items()
    }

    return Location(name, description, destinations, items)
