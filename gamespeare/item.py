"""Module for representing items."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Item:
    """Class representing an item.

    Attributes
    ----------
    name: str
        Unique name of the item.
    description: str
        Description of the item.
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
    """

    name: str
    description: str
    takeable: bool


def create_item(data: Any) -> Item:
    """Creates an `Item` from a dict-like object.

    The input could for example look like this:

    {
      "name": "SKULL",
      "description": "Yorick's skull"
      "takeable": False
    }

    Parameters
    ----------
    data: Any
        dict-like object with keys 'name' and 'description' with string values,
        and optionally the key 'takeable' with bool value.
    """
    name = str(data.get("name")).strip()
    description = str(data.get("description")).strip()
    takeable = bool(data.get("takeable", True))

    return Item(name=name, description=description, takeable=takeable)


@dataclass
class LockableContainerItem(Item):
    """Class representing an item that can contain other items and be locked.

    Attributes
    ----------
    name: str
        Unique name of the item.
        Inherited from `Item`.
    description: str
        Description of the item.
        Inherited from `Item`.
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
        Inherited from `Item`.
    key: str
        Name of the item representing the key, or `None` for no key required.
    contents: set of str
        Set of the names of the items in this container.
    """

    key: str
    contents: set[str]


def create_lockable_container_item(data: Any) -> LockableContainerItem:
    """Creates an `LockableContainerItem` from a dict-like object.

    The input could for example look like this:

    {
      "name": "CHEST",
      "description": "A sturdy chest",
      "key": "KEY"
      "contents": [
        "GIFT"
      ]
    }

    Parameters
    ----------
    data: Any
        dict-like object with keys 'name' and 'description' with string values, and optionally
        the key 'key' with string value, and/or the key 'content' with a list of string values,
        and/or the key 'takeable' with bool value.
    """
    name = str(data.get("name")).strip()
    description = str(data.get("description")).strip()
    takeable = bool(data.get("takeable", False))
    key = str(data.get("key", "")).strip()
    contents = {str(item).strip() for item in data.get("contents", [])}

    return LockableContainerItem(
        name=name,
        description=description,
        takeable=takeable,
        key=key,
        contents=contents,
    )
