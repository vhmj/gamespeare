"""Module for testing of `Playbook`."""

import unittest

from gamespeare.item import Item, LockableContainerItem
from gamespeare.location import Location
from gamespeare.playbook import Playbook, PlaybookError, from_file


class TestPlaybook(unittest.TestCase):
    """Tests Playbook."""

    def setUp(self) -> None:
        self.playbook = from_file("testdata/valid.json")

        self.chest = self.playbook.world.get_item("CHEST")
        self.skull = self.playbook.world.get_item("SKULL")
        self.key = self.playbook.world.get_item("KEY")
        self.ant = self.playbook.world.get_item("ANT")
        self.elephant = self.playbook.world.get_item("ELEPHANT")

        self.room = self.playbook.world.get_location("ROOM")
        self.hall = self.playbook.world.get_location("HALL")

    def test_get_available_items(self) -> None:
        """Tests get_available_items()"""
        items = self.playbook.get_available_items()
        expected_items = [self.chest, self.key, self.ant, self.elephant]
        self.assertCountEqual(items, expected_items)

    def test_add_item_to_inventory_valid(self) -> None:
        """Tests add_item_to_inventory() with valid items"""
        self.assertTrue(self.ant.takeable)
        self.assertIn(self.ant, self.playbook.state.location.contents)
        self.assertNotIn(self.ant, self.playbook.state.inventory.contents)
        self.playbook.add_item_to_inventory(self.ant)
        self.assertNotIn(self.ant, self.playbook.state.location.contents)
        self.assertIn(self.ant, self.playbook.state.inventory.contents)

        self.assertFalse(self.elephant.takeable)
        self.playbook.add_item_to_inventory(self.elephant)
        self.assertIn(self.elephant, self.playbook.state.location.contents)
        self.assertNotIn(self.elephant, self.playbook.state.inventory.contents)

    def test_add_item_to_inventory_invalid(self) -> None:
        """Tests add_item_to_inventory() with invalid items"""
        missing = Item(name="MISSING", description="Missing", takeable=True)
        with self.assertRaises(ValueError):
            self.playbook.add_item_to_inventory(missing)

    def test_add_item_to_location_valid(self) -> None:
        """Tests add_item_to_location() with valid items"""
        self.assertFalse(self.room.contains_item(self.key))
        self.assertTrue(self.playbook.state.inventory.contains_item(self.key))
        self.playbook.add_item_to_location(self.room, self.key)
        self.assertTrue(self.room.contains_item(self.key))
        self.assertFalse(self.playbook.state.inventory.contains_item(self.key))

        self.assertIsInstance(self.chest, LockableContainerItem)
        if hasattr(self.chest, "contains_item"):  # To keep mypy happy
            self.assertTrue(self.chest.contains_item(self.skull))
        self.assertFalse(self.room.contains_item(self.skull))
        self.playbook.add_item_to_location(self.room, self.skull)
        if hasattr(self.chest, "contains_item"):  # To keep mypy happy
            self.assertFalse(self.chest.contains_item(self.skull))
        self.assertTrue(self.room.contains_item(self.skull))

    def test_add_item_to_location_invalid(self) -> None:
        """Tests add_item_to_location() with invalid items"""
        missing_location = Location(name="MISSING", description="Missing")
        with self.assertRaises(ValueError):
            self.playbook.add_item_to_location(missing_location, self.skull)

        missing_item = Item(name="MISSING", description="Missing", takeable=True)
        with self.assertRaises(ValueError):
            self.playbook.add_item_to_location(self.room, missing_item)

    def test_remove_item_valid(self) -> None:
        """Tests remove_item() with valid items"""
        self.assertTrue(self.playbook.world.contains_item(self.skull))
        self.assertIsInstance(self.chest, LockableContainerItem)
        if hasattr(self.chest, "contains_item"):  # To keep mypy happy
            self.assertTrue(self.chest.contains_item(self.skull))
        self.playbook.remove_item(self.skull)
        self.assertTrue(self.playbook.world.contains_item(self.skull))
        if hasattr(self.chest, "contains_item"):  # To keep mypy happy
            self.assertFalse(self.chest.contains_item(self.skull))

        self.assertTrue(self.playbook.world.contains_item(self.key))
        self.assertTrue(self.playbook.state.inventory.contains_item(self.key))
        self.playbook.remove_item(self.key)
        self.assertTrue(self.playbook.world.contains_item(self.key))
        self.assertFalse(self.playbook.state.inventory.contains_item(self.key))

        self.assertTrue(self.playbook.world.contains_item(self.chest))
        self.assertTrue(self.room.contains_item(self.chest))
        self.playbook.remove_item(self.chest)
        self.assertTrue(self.playbook.world.contains_item(self.chest))
        self.assertFalse(self.room.contains_item(self.chest))

    def test_remove_item_invalid(self) -> None:
        """Tests remove_item() with invalid items"""
        missing_item = Item(name="MISSING", description="Missing", takeable=True)

        with self.assertRaises(ValueError):
            self.playbook.remove_item(missing_item)

    def test_from_file_valid(self) -> None:
        """Tests from_file() with valid playbook file"""
        self.assertIsInstance(self.playbook, Playbook)

        # World
        expected_items = [self.skull, self.key, self.chest, self.elephant, self.ant]
        self.assertCountEqual(self.playbook.world.get_item_list(), expected_items)
        expected_locations = [self.room, self.hall]
        self.assertCountEqual(
            self.playbook.world.get_location_list(), expected_locations
        )

        # Story
        self.assertEqual(self.playbook.story.prologue, "prologue")
        self.assertEqual(self.playbook.story.epilogue, "epilogue")
        self.assertEqual(len(self.playbook.story.endings), 3)

        # State
        self.assertEqual(self.playbook.state.turn_no, 123)
        self.assertEqual(self.playbook.state.location, self.room)
        self.assertCountEqual(self.playbook.state.inventory.contents, [self.key])

    def test_from_file_invalid(self) -> None:
        """Tests from_file() with invalid playbook file"""
        with self.assertRaises(PlaybookError):
            from_file("../testdata/nonexisting")

        with self.assertRaises(PlaybookError):
            from_file("../testdata/not.json")

        with self.assertRaises(PlaybookError):
            from_file("../testdata/empty.json")

        with self.assertRaises(PlaybookError):
            from_file("../testdata/no_world.json")

        with self.assertRaises(PlaybookError):
            from_file("../testdata/no_story.json")

        with self.assertRaises(PlaybookError):
            from_file("../testdata/no_state.json")


if __name__ == "__main__":
    unittest.main()
