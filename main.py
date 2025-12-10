"""Module for initialising a `TextAdventureGame`.

Main entry point of the VG assignment program.
"""

import argparse
import sys

import gamespeare
from gamespeare.game import TextAdventureGame
from gamespeare.playbook import PlaybookError

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gamespeare - A Text Adventure Game Engine",
    )
    parser.add_argument("filename", help="path of game to play")
    args = parser.parse_args()

    game_file = args.filename
    try:
        playbook = gamespeare.playbook.from_file(game_file)
    except PlaybookError as e:
        print(f"Unable to load {game_file}: {e}", file=sys.stderr)
    else:
        TextAdventureGame(playbook).play()
