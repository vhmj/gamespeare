"""Module for testing of `Playbook`."""

import unittest

from gamespeare.item import Item, LockableContainerItem
from gamespeare.location import Location
from gamespeare.playbook import Playbook, from_file
from gamespeare.utils import GameDataError


class TestPlaybook(unittest.TestCase):
    """Tests Playbook."""

    def setUp(self):
        self.playbook = from_file("../testdata/valid.json")

    def test_playbook_get_item_by_name_valid(self):
        """Tests get_item_by_name() with valid names"""
        regular_item = self.playbook.get_item_by_name("SKULL")
        self.assertIsInstance(regular_item, Item)
        self.assertEqual(regular_item.name, "SKULL")

        container_item = self.playbook.get_item_by_name("CHEST")
        self.assertIsInstance(container_item, LockableContainerItem)
        self.assertEqual(container_item.name, "CHEST")

    def test_playbook_get_item_by_name_invalid(self):
        """Tests get_item_by_name() with invalid names"""
        with self.assertRaises(ValueError):
            self.playbook.get_item_by_name("MISSING")

    def test_playbook_get_location_by_name_valid(self):
        """Tests get_location_by_name() with valid names"""
        location = self.playbook.get_location_by_name("HALL")
        self.assertIsInstance(location, Location)
        self.assertEqual(location.name, "HALL")

    def test_playbook_get_location_by_name_invalid(self):
        """Tests get_location_by_name() with invalid names"""
        with self.assertRaises(ValueError):
            self.playbook.get_location_by_name("MISSING")

    def test_get_current_location(self):
        """Tests get_current_location()"""
        location = self.playbook.get_current_location()
        self.assertIsInstance(location, Location)
        self.assertEqual(location.name, "ROOM")

    def test_get_available_items(self):
        """Tests get_available_items()"""
        items = self.playbook.get_available_items()
        expected_items = ["CHEST", "KEY", "ANT", "ELEPHANT"]
        self.assertCountEqual(items, expected_items)

    def test_add_item_to_inventory_valid(self):
        """Tests add_item_to_inventory() with valid items"""
        self.playbook.add_item_to_inventory("ANT")
        self.assertNotIn("ANT", self.playbook.get_current_location().items)
        self.assertIn("ANT", self.playbook.state.inventory)

        self.playbook.add_item_to_inventory("ELEPHANT")
        self.assertIn("ELEPHANT", self.playbook.get_current_location().items)
        self.assertNotIn("ELEPHANT", self.playbook.state.inventory)

    def test_add_item_to_inventory_invalid(self):
        """Tests add_item_to_inventory() with invalid items"""
        with self.assertRaises(ValueError):
            self.playbook.add_item_to_inventory("MISSING")

    def test_add_item_to_location_valid(self):
        """Tests add_item_to_location() with valid items"""
        self.playbook.add_item_to_location("ROOM", "KEY")
        self.assertIn("KEY", self.playbook.get_location_by_name("ROOM").items)
        self.assertNotIn("KEY", self.playbook.state.inventory)

        self.playbook.add_item_to_location("ROOM", "SKULL")
        self.assertIn("SKULL", self.playbook.get_location_by_name("ROOM").items)
        self.assertNotIn("SKULL", self.playbook.get_item_by_name("CHEST").contents)

    def test_add_item_to_location_invalid(self):
        """Tests add_item_to_location() with invalid items"""
        with self.assertRaises(ValueError):
            self.playbook.add_item_to_location("MISSING", "SKULL")

        with self.assertRaises(ValueError):
            self.playbook.add_item_to_location("ROOM", "MISSING")

    def test_remove_item_valid(self):
        """Tests remove_item() with valid items"""
        self.assertIn("SKULL", self.playbook.get_item_by_name("CHEST").contents)
        self.playbook.remove_item("SKULL")
        self.assertNotIn("SKULL", self.playbook.get_item_by_name("CHEST").contents)
        self.assertIn("SKULL", self.playbook.world.items)

        self.assertIn("KEY", self.playbook.state.inventory)
        self.playbook.remove_item("KEY")
        self.assertNotIn("KEY", self.playbook.state.inventory)
        self.assertIn("KEY", self.playbook.world.items)

        self.assertIn("CHEST", self.playbook.get_location_by_name("ROOM").items)
        self.playbook.remove_item("CHEST")
        self.assertNotIn("CHEST", self.playbook.get_location_by_name("ROOM").items)
        self.assertIn("CHEST", self.playbook.world.items)

    def test_remove_item_invalid(self):
        """Tests remove_item() with invalid items"""
        with self.assertRaises(ValueError):
            self.playbook.remove_item("MISSING")

    def test_from_file_valid(self):
        """Tests from_file() with valid playbook file"""
        self.assertIsInstance(self.playbook, Playbook)

        # World
        items = ["SKULL", "KEY", "CHEST", "ELEPHANT", "ANT"]
        self.assertCountEqual(self.playbook.world.items.keys(), items)
        locations = ["ROOM", "HALL"]
        self.assertCountEqual(self.playbook.world.locations.keys(), locations)

        # Story
        self.assertEqual(self.playbook.story.prologue, "prologue")
        self.assertEqual(self.playbook.story.epilogue, "epilogue")
        self.assertEqual(len(self.playbook.story.endings), 3)

        # State
        self.assertEqual(self.playbook.state.turn_no, 123)
        self.assertEqual(self.playbook.state.location, "ROOM")
        self.assertCountEqual(self.playbook.state.inventory, ["KEY"])

    def test_from_file_invalid(self):
        """Tests from_file() with invalid playbook file"""
        with self.assertRaises(GameDataError):
            from_file("../testdata/nonexisting")

        with self.assertRaises(GameDataError):
            from_file("../testdata/not.json")

        with self.assertRaises(GameDataError):
            from_file("../testdata/empty.json")

        with self.assertRaises(GameDataError):
            from_file("../testdata/no_world.json")

        with self.assertRaises(GameDataError):
            from_file("../testdata/no_story.json")

        with self.assertRaises(GameDataError):
            from_file("../testdata/no_state.json")


if __name__ == "__main__":
    unittest.main()
