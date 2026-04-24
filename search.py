"""Search algorithms used by the goal-based agents."""
from collections import deque


def manhattan_distance(pos1, pos2):
    """Manhattan distance between two (x, y) tuples."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_neighbors(grid, pos):
    """Return valid neighbouring positions (non-wall, in bounds)."""
    size = len(grid)
    x, y = pos
    neighbors = []
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size and grid[nx][ny] != '#':
            neighbors.append((nx, ny))
    return neighbors


def bfs_search(grid, start, goal):
    """Breadth-first search. Returns (path_or_None, nodes_explored)."""
    if start == goal:
        return [start], 0

    queue = deque([(start, [start])])
    visited = {start}
    nodes_explored = 0

    while queue:
        current, path = queue.popleft()
        nodes_explored += 1

        for neighbor in get_neighbors(grid, current):
            if neighbor == goal:
                return path + [neighbor], nodes_explored
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None, nodes_explored


def astar_search(grid, start, goal):
    """A* with Manhattan heuristic. Returns (path_or_None, nodes_explored)."""
    if start == goal:
        return [start], 0

    # open_set entries: (f_score, counter, position, path)
    open_set = [(manhattan_distance(start, goal), 0, start, [start])]
    closed_set = set()
    g_scores = {start: 0}
    nodes_explored = 0
    counter = 1

    while open_set:
        open_set.sort()
        _, _, current, path = open_set.pop(0)
        nodes_explored += 1

        if current in closed_set:
            continue
        if current == goal:
            return path, nodes_explored

        closed_set.add(current)

        for neighbor in get_neighbors(grid, current):
            if neighbor in closed_set:
                continue
            tentative_g = g_scores[current] + 1
            if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                g_scores[neighbor] = tentative_g
                f_score = tentative_g + manhattan_distance(neighbor, goal)
                open_set.append((f_score, counter, neighbor, path + [neighbor]))
                counter += 1

    return None, nodes_explored
