"""Module for testing of `TextAdventureGame`"""

import unittest

from gamespeare.game import TextAdventureGame
from gamespeare.playbook import from_file


class TestTextAdventureGame(unittest.TestCase):
    """Tests for `TextAdventureGame`"""

    def test_init(self) -> None:
        """Tests TextAdventureGame()"""
        playbook = from_file("../testdata/valid.json")
        game = TextAdventureGame(playbook)
        self.assertEqual(game.playbook, playbook)
        self.assertEqual(game.ending, "")


if __name__ == "__main__":
    unittest.main()
