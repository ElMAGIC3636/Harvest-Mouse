"""Harvest Mouse — entry point.

Launches the pygame lobby. From the lobby you can play yourself
with the keyboard, or watch a simple-reflex, BFS, or A* agent solve
the maze.
"""
import sys


def main():
    try:
        import pygame  # noqa: F401
    except ImportError:
        print("pygame is required. Install it with:")
        print("    pip install pygame")
        sys.exit(1)

    from ui import run
    run()


if __name__ == "__main__":
    main()
