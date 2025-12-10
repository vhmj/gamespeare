"""Module for representing items."""

from typing import Any


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

    Parameters
    ----------
    name: str
        Unique name of the item.
    description: str
        Description of the item.
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
    """

    def __init__(self, name: str, description: str, takeable: bool = True):
        self.name = name
        self.description = description
        self.takeable = takeable

    def __str__(self):
        return f"{self.name}: {self.description}"

    def __repr__(self):
        attributes_repr = (
            f"name={self.name},"
            f"description={self.description},"
            f"takeable={self.takeable}"
        )
        return f"{type(self).__name__}({attributes_repr})"


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
    contents: list of str
        List of the names of the items in this container, or `None` for no items.

    Parameters
    ----------
    name: str
        Unique name of the item.
    description: str
        Description of the item.
    takeable: bool
        `True` if the item can be taken, `False` otherwise.
    key: str or None
        Name of the item representing the key, or `None` for no key required.
    contents: list of str or None
        List of the names of the items in this container, or `None` for no items.
    """

    def __init__(
        self,
        name: str,
        description: str,
        takeable: bool = False,
        key: str | None = None,
        contents: list[str] | None = None,
    ):
        super().__init__(name, description, takeable)
        self.key = key
        self.contents = contents or []

    def __repr__(self):
        attributes_repr = (
            f"name={self.name},"
            f"description={self.description},"
            f"takeable={self.takeable},"
            f"key={self.key},"
            f"contents={self.contents}"
        )
        return f"{type(self).__name__}({attributes_repr})"


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
    contents = [str(item).strip() for item in data.get("contents", [])]

    return LockableContainerItem(
        name=name,
        description=description,
        takeable=takeable,
        key=key,
        contents=contents,
    )
