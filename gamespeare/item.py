"""Module for representing items."""

from dataclasses import dataclass
from typing import Any

from gamespeare.utils import get_bool, get_string


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

    Raises
    ------
    ValueError
        Raised if `data` lacks required values.
    """
    name = get_string(data, "name")
    description = get_string(data, "description")
    takeable = get_bool(data, "takeable", True)

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

    Raises
    ------
    ValueError
        Raised if `data` lacks required values.
    """
    name = get_string(data, "name")
    description = get_string(data, "description")
    takeable = get_bool(data, "takeable", False)
    key = get_string(data, "key", empty_ok=True)
    contents = {str(item).strip() for item in data.get("contents", [])}

    return LockableContainerItem(
        name=name,
        description=description,
        takeable=takeable,
        key=key,
        contents=contents,
    )


def create_items(data: Any) -> dict[str, Item]:
    """Creates items from a list of dict-like data.

    The key `class` is required, and the supported values are:

    * `ITEM` - See `create_item()` for additional requirements.
    * `CONTAINER` - See `create_lockable_container_item()` for additional requirements.

    Parameters
    ----------
    data: Any
        A list of dict-like objects with the key `class` and additional item data.

    Returns
    -------
    dict of str:Item
        A dict of items initialized from `data`.

    Raises
    ------
    ValueError
        Raised if `data` was invalid.
    """
    items = {}

    for entry in data:
        item_class = entry.get("class")
        if item_class == "ITEM":
            item = create_item(entry)
        elif item_class == "CONTAINER":
            item = create_lockable_container_item(entry)
        else:
            raise ValueError(f"Unsupported Item class: {item_class}")
        items[item.name] = item

    return items
