"""Agent classes: reactive (simple reflex) and goal-based (BFS / A*)."""
import random

from search import bfs_search, astar_search


class SimpleReflexAgent:
    """Reacts only to the current percept (adjacent cells)."""

    def __init__(self, name="Simple Reflex"):
        self.name = name
        self.steps_taken = 0
        self.path = []

    def decide_action(self, adjacent_cells, cheese_pos, current_pos):
        self.steps_taken += 1

        # Rule 1: if cheese is adjacent, move onto it
        for direction, cell in adjacent_cells.items():
            if cell == 'C':
                return direction

        # Rule 2: otherwise pick a random non-wall neighbour
        valid_moves = [d for d, cell in adjacent_cells.items() if cell != '#']
        if valid_moves:
            return random.choice(valid_moves)

        # Rule 3: fully boxed in — pick any direction
        return random.choice(['up', 'down', 'left', 'right'])

    def reset(self):
        self.steps_taken = 0
        self.path = []


class BFSAgent:
    """Goal-based agent that plans a shortest path with BFS."""

    def __init__(self, name="BFS Agent"):
        self.name = name
        self.steps_taken = 0
        self.path = []
        self.nodes_explored = 0
        self.current_path_index = 0

    def plan_path(self, grid, start, goal):
        self.path, self.nodes_explored = bfs_search(grid, start, goal)
        self.current_path_index = 0
        return self.path is not None

    def get_next_move(self):
        if not self.path or self.current_path_index >= len(self.path) - 1:
            return None
        self.current_path_index += 1
        self.steps_taken += 1
        current = self.path[self.current_path_index - 1]
        next_pos = self.path[self.current_path_index]
        return _direction_between(current, next_pos)

    def reset(self):
        self.steps_taken = 0
        self.path = []
        self.current_path_index = 0
        self.nodes_explored = 0


class AStarAgent:
    """Goal-based agent that plans a shortest path with A*."""

    def __init__(self, name="A* Agent"):
        self.name = name
        self.steps_taken = 0
        self.path = []
        self.nodes_explored = 0
        self.current_path_index = 0

    def plan_path(self, grid, start, goal):
        self.path, self.nodes_explored = astar_search(grid, start, goal)
        self.current_path_index = 0
        return self.path is not None

    def get_next_move(self):
        if not self.path or self.current_path_index >= len(self.path) - 1:
            return None
        self.current_path_index += 1
        self.steps_taken += 1
        current = self.path[self.current_path_index - 1]
        next_pos = self.path[self.current_path_index]
        return _direction_between(current, next_pos)

    def reset(self):
        self.steps_taken = 0
        self.path = []
        self.current_path_index = 0
        self.nodes_explored = 0


def _direction_between(current, next_pos):
    if next_pos[0] < current[0]:
        return 'up'
    if next_pos[0] > current[0]:
        return 'down'
    if next_pos[1] < current[1]:
        return 'left'
    if next_pos[1] > current[1]:
        return 'right'
    return None
