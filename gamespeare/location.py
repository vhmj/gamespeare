"""Module for representing locations."""

from dataclasses import dataclass, field
from typing import Any, Iterable

from gamespeare.item import Item, ItemContainer


@dataclass
class Location:
    """Class representing a location in a game.

    Attributes
    ----------
    name: str
        Unique name of the location.
    description: str
        Description of the location.
    destinations: dict of str: Location
        Possible destinations to go from this location, with the key being the direction and the
        value the destination location.
    items: ItemContainer
        Items present in the location.
    """

    name: str
    description: str
    destinations: dict[str, Location] = field(default_factory=dict)
    items: ItemContainer = field(default_factory=ItemContainer)


def create_location(
    data: Any,
    locations: Iterable[Location] | None = None,
    items: ItemContainer | Iterable[Item] | None = None,
) -> Location:
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
    items: ItemContainer or iterable of Item or None
        Valid items.
    locations: iterable of Location
        Valid locations.
    data: Any
        dict-like object with keys 'name' and 'description' with string values, and
        optionally 'items', with a list of string values, and 'destinations', a dict
        with string keys and values.

    Raises
    ------
    ValueError
        Raised if `data` lacks required values or has incorrect values.
    """
    if not items:
        valid_items = []
    elif isinstance(items, ItemContainer):
        valid_items = items.items
    else:
        valid_items = list(items)
    item_dict = {item.name: item for item in valid_items}

    location_dict = {location.name: location for location in locations or []}

    try:
        name = str(data["name"]).strip()
        description = str(data["description"]).strip()
        contents = [item_dict[str(item).strip()] for item in data.get("items", [])]
        destinations = {
            str(k).strip(): location_dict[str(v).strip()]
            for (k, v) in data.get("destinations", {}).items()
        }
    except KeyError as e:
        raise ValueError("Missing key") from e
    except TypeError as e:
        raise ValueError("Invalid type") from e

    return Location(name, description, destinations, ItemContainer(contents))


def create_locations(
    data: Any, items: ItemContainer | Iterable[Item] | None
) -> list[Location]:
    """Creates locations from an iterable of dict-like data.

    The key `class` is required, and the supported values are:

    * `LOCATION` - See `create_location()` for additional requirements.

    Parameters
    ----------
    data: Any
        An iterable of dict-like objects with the key `class` and additional
        item data.
    items: ItemContainer or iterable of Item or None
        Valid items.

    Returns
    -------
    list of Location
        A list of locations initialized from `data`.


    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    locations = {}
    unfilled_destinations = {}

    for entry in data:
        location_class = entry.get("class")
        if location_class == "LOCATION":
            destinations = entry.pop("destinations", {})

            location = create_location(entry, items=items)
            if location.name in locations:
                raise ValueError(f"Duplicate location name: {location.name}")
            locations[location.name] = location

            if destinations:
                unfilled_destinations[location.name] = destinations
        else:
            raise ValueError(f"Unsupported ending class: {location_class}")

    for location_name, location_destinations in unfilled_destinations.items():
        location = locations[location_name]
        try:
            for raw_direction, raw_destination_name in location_destinations.items():

                direction = str(raw_direction).strip()
                destination_name = str(raw_destination_name).strip()

                if destination_name not in locations:
                    raise ValueError(f"Unknown destination: {destination_name}")

                location.destinations[direction] = locations[destination_name]
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid destination entry") from e

    return list(locations.values())


def get_location_by_name(locations: Iterable[Location] | None, name: str) -> Location:
    """Gets the item with a specific name.

    Parameters
    ----------
    locations: Iterable of Location
        Locations to search
    name: str
        Name of the location to get.

    Returns
    -------
    Location
        The first location encountered named `name`.

    Raises
    ------
    ValueError
        Raised if no locations named `name` were present.
    """
    for location in locations or []:
        if location.name == name:
            return location

    raise ValueError(f"Location does not exist: {name}")
