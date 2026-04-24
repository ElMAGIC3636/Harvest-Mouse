"""The GridWorld environment for the Harvest Mouse game."""
import copy
import random


class GridWorld:
    """A small grid world with a mouse, some cheese, and walls."""

    EMPTY = '.'
    WALL = '#'
    MOUSE = 'M'
    CHEESE = 'C'

    def __init__(self, size=5, obstacle_density=0.2):
        self.size = size
        self.obstacle_density = obstacle_density
        self.grid = []
        self.mouse_pos = None
        self.cheese_pos = None
        self.steps_taken = 0
        self.max_steps = size * size * 2

        self._generate_grid()
        self.initial_state = copy.deepcopy(self.grid)
        self.initial_mouse = self.mouse_pos
        self.initial_cheese = self.cheese_pos

    # -- generation -----------------------------------------------------
    def _generate_grid(self):
        self.grid = [[self.EMPTY for _ in range(self.size)]
                     for _ in range(self.size)]

        num_obstacles = int(self.size * self.size * self.obstacle_density)
        attempts = 0
        placed = 0
        while placed < num_obstacles and attempts < num_obstacles * 20:
            attempts += 1
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.grid[x][y] == self.EMPTY:
                self.grid[x][y] = self.WALL
                placed += 1

        empty_cells = self.get_empty_cells()
        if len(empty_cells) < 2:
            self.obstacle_density = 0.1
            return self._generate_grid()

        self.mouse_pos = random.choice(empty_cells)
        empty_cells.remove(self.mouse_pos)
        self.cheese_pos = random.choice(empty_cells)

        self.grid[self.mouse_pos[0]][self.mouse_pos[1]] = self.MOUSE
        self.grid[self.cheese_pos[0]][self.cheese_pos[1]] = self.CHEESE

    def get_empty_cells(self):
        empty = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == self.EMPTY:
                    empty.append((i, j))
        return empty

    # -- queries --------------------------------------------------------
    def get_valid_moves(self, position):
        moves = []
        x, y = position
        if x > 0 and self.grid[x - 1][y] != self.WALL:
            moves.append((-1, 0, 'up'))
        if x < self.size - 1 and self.grid[x + 1][y] != self.WALL:
            moves.append((1, 0, 'down'))
        if y > 0 and self.grid[x][y - 1] != self.WALL:
            moves.append((0, -1, 'left'))
        if y < self.size - 1 and self.grid[x][y + 1] != self.WALL:
            moves.append((0, 1, 'right'))
        return moves

    def get_adjacent_cells(self, position):
        x, y = position
        directions = {
            'up': (x - 1, y) if x > 0 else None,
            'down': (x + 1, y) if x < self.size - 1 else None,
            'left': (x, y - 1) if y > 0 else None,
            'right': (x, y + 1) if y < self.size - 1 else None,
        }
        adjacent = {}
        for name, pos in directions.items():
            if pos is None:
                adjacent[name] = self.WALL
            else:
                adjacent[name] = self.grid[pos[0]][pos[1]]
        return adjacent

    def is_cheese_reached(self):
        return self.mouse_pos == self.cheese_pos

    # -- mutation -------------------------------------------------------
    def move_mouse(self, direction):
        x, y = self.mouse_pos
        nx, ny = x, y
        if direction == 'up' and x > 0:
            nx = x - 1
        elif direction == 'down' and x < self.size - 1:
            nx = x + 1
        elif direction == 'left' and y > 0:
            ny = y - 1
        elif direction == 'right' and y < self.size - 1:
            ny = y + 1
        else:
            return False

        if self.grid[nx][ny] == self.WALL:
            return False

        self.grid[x][y] = self.EMPTY
        self.mouse_pos = (nx, ny)
        self.grid[nx][ny] = self.MOUSE
        self.steps_taken += 1
        return True

    def reset(self):
        self.grid = copy.deepcopy(self.initial_state)
        self.mouse_pos = self.initial_mouse
        self.cheese_pos = self.initial_cheese
        self.steps_taken = 0

    # -- utilities ------------------------------------------------------
    def get_state(self):
        return {
            'grid': copy.deepcopy(self.grid),
            'mouse_pos': self.mouse_pos,
            'cheese_pos': self.cheese_pos,
            'steps': self.steps_taken,
        }

    def display(self):
        """Simple terminal display (still works for CLI debugging)."""
        border = "─" * (self.size * 4 + 1)
        print("\n" + border)
        for i in range(self.size):
            row = "│"
            for j in range(self.size):
                cell = self.grid[i][j]
                if cell == self.MOUSE:
                    row += " M │"
                elif cell == self.CHEESE:
                    row += " C │"
                elif cell == self.WALL:
                    row += " █ │"
                else:
                    row += " · │"
            print(row)
            print(border)
        print(f"Steps: {self.steps_taken}")
