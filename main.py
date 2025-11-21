"""Module for initialising a `TextAdventureGame`.

Main entry point of the VG assignment program.
"""

import argparse
import sys

from gamespeare.game import TextAdventureGame, GameDataError

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gamespeare - A Text Adventure Game Engine",
    )
    parser.add_argument("filename", help="path of game to play")
    args = parser.parse_args()

    game_file = args.filename
    try:
        game = TextAdventureGame(game_file)
    except GameDataError as e:
        print(f"Unable to load {game_file}: {e}", file=sys.stderr)
    else:
        game.play()
