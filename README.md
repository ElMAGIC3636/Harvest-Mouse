# Harvest Mouse

A small AI-agents study game with a pygame UI. Guide a mouse to the cheese
either yourself or by watching one of three agents solve the maze.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The lobby lets you pick the grid size (4–9), the wall density (0–35%), and
the mode:

- **Play yourself** — arrow keys or WASD. You have a step budget based on
  grid size.
- **Simple reflex** — a purely reactive agent. Only sees adjacent cells;
  wanders randomly if the cheese isn't right next to it. Visited cells are
  lightly shaded so you can watch the random walk.
- **BFS agent** — plans a shortest path with breadth-first search. The
  planned path is highlighted on the board before the mouse starts walking.
- **A\* agent** — same planning, but with a Manhattan-distance heuristic.
  Compare the "nodes explored" stat against BFS to see the heuristic's
  payoff.

Every maze is verified solvable before it's handed to you — if a generated
grid has the cheese walled off, it's regenerated automatically.

## Files

- `search.py` — BFS and A\* implementations
- `agent.py`  — `SimpleReflexAgent`, `BFSAgent`, `AStarAgent`
- `game.py`   — `GridWorld` environment
- `ui.py`     — pygame lobby and game screen
- `main.py`   — entry point
