"""Pygame UI for Harvest Mouse: lobby + game screen.

Run with `python main.py` (or `python ui.py` directly).
"""
import sys
import pygame

from game import GridWorld
from search import bfs_search, astar_search


# ----------------------------------------------------------------------
# Colour palette (matches the claude.ai-inspired widget)
# ----------------------------------------------------------------------
BG               = (250, 249, 245)
SURFACE          = (255, 255, 255)
SURFACE_SOFT     = (241, 239, 232)
BORDER           = (220, 218, 210)
BORDER_STRONG    = (180, 178, 170)
TEXT_PRIMARY     = (30, 29, 26)
TEXT_SECONDARY   = (95, 94, 90)
TEXT_TERTIARY    = (136, 135, 128)

INFO_BG          = (230, 241, 251)
INFO_TEXT        = (12, 68, 124)
INFO_BORDER      = (55, 138, 221)

SUCCESS_BG       = (225, 245, 238)
SUCCESS_TEXT     = (15, 110, 86)

DANGER_BG        = (252, 235, 235)
DANGER_TEXT      = (163, 45, 45)

# Cell / path colours
WALL_COLOR       = (68, 68, 65)
WALL_BORDER      = (44, 44, 42)
FLOOR_COLOR      = (255, 255, 255)
PATH_COLOR       = (206, 203, 246)   # purple 100
VISITED_COLOR    = (238, 237, 254)   # purple 50
GOAL_RING        = (15, 110, 86)     # teal 600

# Mode icon colours (bg, fg)
ICON_PLAYER      = ((230, 241, 251), (12, 68, 124))
ICON_REFLEX      = ((250, 236, 231), (113, 43, 19))
ICON_BFS         = ((238, 237, 254), (60, 52, 137))
ICON_ASTAR       = ((225, 245, 238), (8, 80, 65))

# Mouse / cheese art
MOUSE_BODY       = (220, 218, 210)
MOUSE_EAR_OUTER  = (180, 178, 170)
MOUSE_EAR_INNER  = (237, 147, 177)
MOUSE_EYE        = (30, 29, 26)
MOUSE_NOSE       = (212, 83, 126)
CHEESE_FILL      = (239, 159, 39)
CHEESE_OUTLINE   = (186, 117, 23)

WINDOW_W, WINDOW_H = 980, 720
FPS = 60


# ----------------------------------------------------------------------
# Fonts
# ----------------------------------------------------------------------
def load_font(size, bold=False):
    stack = "Inter,SF Pro Display,SF Pro Text,Helvetica Neue,Segoe UI,Arial"
    return pygame.font.SysFont(stack, size, bold=bold)


class Fonts:
    def __init__(self):
        self.h1    = load_font(30, bold=True)
        self.h2    = load_font(20, bold=True)
        self.h3    = load_font(17, bold=True)
        self.body  = load_font(15)
        self.small = load_font(13)
        self.tiny  = load_font(11)
        self.stat  = load_font(26, bold=True)
        self.icon  = load_font(15, bold=True)
        self.mono  = pygame.font.SysFont("Menlo,Consolas,monospace", 12, bold=True)


# ----------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------
def draw_round_rect(surface, color, rect, radius=8, width=0):
    pygame.draw.rect(surface, color, rect, width, border_radius=radius)


def draw_text(surface, text, font, color, pos, align="topleft"):
    img = font.render(text, True, color)
    rect = img.get_rect(**{align: pos})
    surface.blit(img, rect)
    return rect


def draw_mouse(surface, rect):
    cx, cy = rect.centerx, rect.centery
    s = min(rect.width, rect.height)
    body_r = max(6, int(s * 0.30))
    ear_r  = max(3, int(s * 0.12))
    ex     = int(body_r * 0.55)
    ey     = cy - int(body_r * 0.75)
    # outer ears
    pygame.draw.circle(surface, MOUSE_EAR_OUTER, (cx - ex, ey), ear_r)
    pygame.draw.circle(surface, MOUSE_EAR_OUTER, (cx + ex, ey), ear_r)
    # body
    pygame.draw.circle(surface, MOUSE_BODY, (cx, cy), body_r)
    # inner ears
    if ear_r >= 5:
        pygame.draw.circle(surface, MOUSE_EAR_INNER, (cx - ex, ey), ear_r - 2)
        pygame.draw.circle(surface, MOUSE_EAR_INNER, (cx + ex, ey), ear_r - 2)
    # eyes
    eye_r = max(1, int(s * 0.035))
    pygame.draw.circle(surface, MOUSE_EYE, (cx - body_r // 3, cy), eye_r)
    pygame.draw.circle(surface, MOUSE_EYE, (cx + body_r // 3, cy), eye_r)
    # nose
    pygame.draw.circle(surface, MOUSE_NOSE, (cx, cy + body_r // 3), eye_r + 1)


def draw_cheese(surface, rect):
    cx, cy = rect.centerx, rect.centery
    s = min(rect.width, rect.height)
    k = int(s * 0.34)
    points = [(cx - k, cy + k), (cx + k, cy + k), (cx, cy - k)]
    pygame.draw.polygon(surface, CHEESE_FILL, points)
    pygame.draw.polygon(surface, CHEESE_OUTLINE, points, 2)
    # holes
    hole_r = max(1, int(s * 0.04))
    pygame.draw.circle(surface, CHEESE_OUTLINE, (cx - k // 3, cy + k // 3), hole_r)
    pygame.draw.circle(surface, CHEESE_OUTLINE, (cx + k // 4, cy + k // 6), hole_r)
    pygame.draw.circle(surface, CHEESE_OUTLINE, (cx, cy + k // 2 + 2), hole_r)


# ----------------------------------------------------------------------
# Widgets
# ----------------------------------------------------------------------
class Button:
    def __init__(self, rect, label, onclick, primary=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.onclick = onclick
        self.hover = False
        self.pressed = False
        self.primary = primary
        self.enabled = True

    def handle(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                self.onclick()

    def draw(self, surface, fonts):
        r = self.rect
        if not self.enabled:
            bg = SURFACE
            border = BORDER
            text = TEXT_TERTIARY
        elif self.primary:
            bg = INFO_BG if not self.hover else (215, 232, 247)
            border = INFO_BORDER
            text = INFO_TEXT
        else:
            bg = SURFACE_SOFT if self.hover else SURFACE
            border = BORDER_STRONG if self.hover else BORDER
            text = TEXT_PRIMARY

        draw_round_rect(surface, bg, r, radius=8)
        draw_round_rect(surface, border, r, radius=8, width=1)
        img = fonts.body.render(self.label, True, text)
        surface.blit(img, img.get_rect(center=r.center))


class Slider:
    def __init__(self, rect, min_val, max_val, value, step=1, on_change=None):
        self.rect = pygame.Rect(rect)
        self.min = min_val
        self.max = max_val
        self.value = value
        self.step = step
        self.dragging = False
        self.on_change = on_change

    def _value_to_x(self, v):
        t = (v - self.min) / max(1, (self.max - self.min))
        return int(self.rect.x + t * self.rect.width)

    def _x_to_value(self, x):
        t = (x - self.rect.x) / max(1, self.rect.width)
        t = max(0.0, min(1.0, t))
        raw = self.min + t * (self.max - self.min)
        return round(raw / self.step) * self.step

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            expanded = self.rect.inflate(0, 24)
            if expanded.collidepoint(event.pos):
                self.dragging = True
                self._set(self._x_to_value(event.pos[0]))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set(self._x_to_value(event.pos[0]))

    def _set(self, v):
        v = max(self.min, min(self.max, v))
        if v != self.value:
            self.value = v
            if self.on_change:
                self.on_change(v)

    def draw(self, surface):
        # track
        track = pygame.Rect(self.rect.x, self.rect.y + self.rect.height // 2 - 2,
                            self.rect.width, 4)
        draw_round_rect(surface, BORDER, track, radius=2)
        # filled portion
        fill_w = self._value_to_x(self.value) - self.rect.x
        fill = pygame.Rect(track.x, track.y, fill_w, track.height)
        draw_round_rect(surface, TEXT_SECONDARY, fill, radius=2)
        # thumb
        tx = self._value_to_x(self.value)
        ty = self.rect.y + self.rect.height // 2
        pygame.draw.circle(surface, SURFACE, (tx, ty), 9)
        pygame.draw.circle(surface, BORDER_STRONG, (tx, ty), 9, 1)


class ModeCard:
    def __init__(self, rect, mode_id, title, desc, icon_letter, icon_colors,
                 badge=None, featured=False, on_select=None):
        self.rect = pygame.Rect(rect)
        self.mode_id = mode_id
        self.title = title
        self.desc = desc
        self.icon_letter = icon_letter
        self.icon_bg, self.icon_fg = icon_colors
        self.badge = badge
        self.featured = featured
        self.hover = False
        self.pressed = False
        self.on_select = on_select

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was = self.pressed
            self.pressed = False
            if was and self.rect.collidepoint(event.pos):
                self.on_select(self.mode_id)

    def draw(self, surface, fonts):
        r = self.rect
        draw_round_rect(surface, SURFACE, r, radius=12)
        border_color = INFO_BORDER if self.featured else (
            BORDER_STRONG if self.hover else BORDER)
        width = 2 if self.featured else 1
        draw_round_rect(surface, border_color, r, radius=12, width=width)

        x, y = r.x + 20, r.y + 18

        # badge
        if self.badge:
            badge_text = fonts.small.render(self.badge, True, INFO_TEXT)
            pad_x, pad_y = 10, 4
            bw = badge_text.get_width() + pad_x * 2
            bh = badge_text.get_height() + pad_y * 2
            badge_rect = pygame.Rect(x, y, bw, bh)
            draw_round_rect(surface, INFO_BG, badge_rect, radius=8)
            surface.blit(badge_text, (x + pad_x, y + pad_y))
            y += bh + 10

        # icon
        icon_rect = pygame.Rect(x, y, 34, 34)
        draw_round_rect(surface, self.icon_bg, icon_rect, radius=8)
        letter = fonts.icon.render(self.icon_letter, True, self.icon_fg)
        surface.blit(letter, letter.get_rect(center=icon_rect.center))

        # title
        title_y = icon_rect.bottom + 12
        draw_text(surface, self.title, fonts.h3, TEXT_PRIMARY, (x, title_y))

        # description (2 lines max)
        desc_y = title_y + 24
        self._wrap_and_draw(surface, self.desc, fonts.small, TEXT_SECONDARY,
                            (x, desc_y), r.right - x - 20, max_lines=2)

    @staticmethod
    def _wrap_and_draw(surface, text, font, color, pos, max_w, max_lines=2):
        words = text.split()
        lines, line = [], ""
        for w in words:
            trial = (line + " " + w).strip()
            if font.size(trial)[0] <= max_w:
                line = trial
            else:
                lines.append(line)
                line = w
                if len(lines) == max_lines - 1:
                    # put the rest in the last line
                    remaining = " ".join([line] + words[words.index(w) + 1:])
                    while font.size(remaining + "…")[0] > max_w and len(remaining) > 0:
                        remaining = remaining[:-1]
                    lines.append(remaining + "…")
                    line = ""
                    break
        if line:
            lines.append(line)

        x, y = pos
        for i, ln in enumerate(lines[:max_lines]):
            img = font.render(ln, True, color)
            surface.blit(img, (x, y + i * (font.get_linesize())))


# ----------------------------------------------------------------------
# Env helpers
# ----------------------------------------------------------------------
def make_solvable_env(size, density, max_tries=40):
    """Generate a GridWorld where the mouse can reach the cheese."""
    last = None
    for _ in range(max_tries):
        env = GridWorld(size=size, obstacle_density=density)
        path, _ = bfs_search(env.grid, env.mouse_pos, env.cheese_pos)
        if path is not None:
            return env
        last = env
    # Fall back to low density if we got stuck
    return GridWorld(size=size, obstacle_density=min(density, 0.1))


# ----------------------------------------------------------------------
# Lobby screen
# ----------------------------------------------------------------------
class LobbyScreen:
    def __init__(self, app, size=6, density=0.22):
        self.app = app
        self.size = size
        self.density = density

        # sliders
        self.size_slider = Slider((180, 177, 180, 22), 4, 9, self.size,
                                  on_change=self._on_size)
        self.density_slider = Slider((560, 177, 180, 22), 0, 35,
                                     int(self.density * 100),
                                     on_change=self._on_density)

        # mode cards (2x2)
        card_w = 400
        card_h = 180
        gap = 24
        total_w = card_w * 2 + gap
        left = (WINDOW_W - total_w) // 2
        top = 250

        self.cards = [
            ModeCard((left, top, card_w, card_h), 'player',
                     "Play yourself",
                     "Use arrow keys or WASD to move. Find the cheese before you run out of steps.",
                     "P1", ICON_PLAYER, badge="You play", featured=True,
                     on_select=self._start),
            ModeCard((left + card_w + gap, top, card_w, card_h), 'simple',
                     "Simple reflex",
                     "Reacts only to adjacent cells. Wanders randomly until it stumbles onto cheese.",
                     "R", ICON_REFLEX, on_select=self._start),
            ModeCard((left, top + card_h + gap, card_w, card_h), 'bfs',
                     "BFS agent",
                     "Plans ahead with breadth-first search. Always finds the shortest path.",
                     "B", ICON_BFS, on_select=self._start),
            ModeCard((left + card_w + gap, top + card_h + gap, card_w, card_h), 'astar',
                     "A* agent",
                     "Uses a Manhattan-distance heuristic. Explores far fewer nodes than BFS.",
                     "A*", ICON_ASTAR, on_select=self._start),
        ]

    def _on_size(self, v):
        self.size = int(v)

    def _on_density(self, v):
        self.density = int(v) / 100.0

    def _start(self, mode_id):
        self.app.start_game(mode_id, self.size, self.density)

    def handle(self, event):
        self.size_slider.handle(event)
        self.density_slider.handle(event)
        for card in self.cards:
            card.handle(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(BG)
        fonts = self.app.fonts

        # title
        draw_text(surface, "Harvest mouse", fonts.h1, TEXT_PRIMARY, (60, 56))
        draw_text(surface,
                  "Help the mouse reach the cheese. Play yourself or watch an AI agent solve it.",
                  fonts.body, TEXT_SECONDARY, (60, 100))

        # settings strip
        strip = pygame.Rect(60, 160, WINDOW_W - 120, 56)
        draw_round_rect(surface, SURFACE, strip, radius=12)
        draw_round_rect(surface, BORDER, strip, radius=12, width=1)

        draw_text(surface, "Grid size", fonts.small, TEXT_SECONDARY, (80, 178))
        self.size_slider.draw(surface)
        draw_text(surface, f"{self.size}", fonts.h3, TEXT_PRIMARY, (370, 178))

        draw_text(surface, "Wall density", fonts.small, TEXT_SECONDARY, (450, 178))
        self.density_slider.draw(surface)
        draw_text(surface, f"{int(self.density * 100)}%", fonts.h3, TEXT_PRIMARY,
                  (750, 178))

        # mode cards
        for card in self.cards:
            card.draw(surface, fonts)

        # footer hint
        draw_text(surface,
                  "Tip: try a 9 × 9 grid at 30%+ density to see how much A* beats BFS.",
                  fonts.small, TEXT_TERTIARY, (60, WINDOW_H - 38))


# ----------------------------------------------------------------------
# Game screen
# ----------------------------------------------------------------------
class GameScreen:
    MODE_TITLES = {
        'player': "You are playing",
        'simple': "Simple reflex agent",
        'bfs':    "BFS agent",
        'astar':  "A* agent",
    }

    def __init__(self, app, mode, size, density):
        self.app = app
        self.mode = mode
        self.size = size
        self.density = density
        self.env = None
        self.status = 'idle'      # 'idle' | 'playing' | 'won' | 'lost'
        self.planned_path = None
        self.path_cells = set()
        self.visited_cells = set()
        self.nodes_explored = 0
        self.step_budget = 0
        self.agent_elapsed = 0
        self.agent_delay = 180    # ms per step
        self.buttons = []
        self._new_round()

    # -- round lifecycle ------------------------------------------------
    def _new_round(self):
        self.env = make_solvable_env(self.size, self.density)
        self.status = 'idle'
        self.planned_path = None
        self.path_cells = set()
        self.visited_cells = {self.env.mouse_pos}
        self.nodes_explored = 0
        self.step_budget = self.size * self.size * 3
        self.agent_elapsed = 0
        self.agent_delay = 110 if self.mode == 'simple' else 180

        if self.mode == 'bfs':
            path, nodes = bfs_search(self.env.grid,
                                     self.env.mouse_pos, self.env.cheese_pos)
            self.planned_path = path or []
            self.path_cells = set(tuple(p) for p in self.planned_path)
            self.nodes_explored = nodes
        elif self.mode == 'astar':
            path, nodes = astar_search(self.env.grid,
                                       self.env.mouse_pos, self.env.cheese_pos)
            self.planned_path = path or []
            self.path_cells = set(tuple(p) for p in self.planned_path)
            self.nodes_explored = nodes

        self._rebuild_buttons()

    def _rebuild_buttons(self):
        self.buttons = []
        bx = 60
        by = WINDOW_H - 74
        bw, bh = 130, 40

        self.buttons.append(Button((bx, by, bw, bh), "New maze", self._new_round))
        bx += bw + 10

        if self.mode != 'player':
            if self.status == 'playing':
                self.buttons.append(
                    Button((bx, by, bw, bh), "Pause", self._pause_agent))
                bx += bw + 10
            elif self.status in ('idle',):
                self.buttons.append(
                    Button((bx, by, bw, bh), "Start agent", self._run_agent,
                           primary=True))
                bx += bw + 10
                self.buttons.append(
                    Button((bx, by, bw, bh), "Step once", self._step_once))
                bx += bw + 10

        # back button (top-right)
        self.buttons.append(
            Button((WINDOW_W - 60 - 150, 40, 150, 40), "Back to lobby",
                   self._back))

    # -- actions --------------------------------------------------------
    def _back(self):
        self.app.go_to_lobby(self.size, self.density)

    def _run_agent(self):
        if self.status == 'won' or self.status == 'lost':
            return
        self.status = 'playing'
        self.agent_elapsed = 0
        self._rebuild_buttons()

    def _pause_agent(self):
        if self.status == 'playing':
            self.status = 'idle'
            self._rebuild_buttons()

    def _step_once(self):
        if self.status in ('won', 'lost'):
            return
        self._agent_step()
        self._rebuild_buttons()

    # -- movement -------------------------------------------------------
    def _try_move(self, direction):
        if self.status in ('won', 'lost'):
            return False
        moved = self.env.move_mouse(direction)
        if moved:
            self.visited_cells.add(self.env.mouse_pos)
            if self.env.is_cheese_reached():
                self.status = 'won'
                self._rebuild_buttons()
            elif self.mode == 'player' and self.env.steps_taken >= self.step_budget:
                self.status = 'lost'
                self._rebuild_buttons()
        return moved

    def _agent_step(self):
        if self.status in ('won', 'lost'):
            return

        if self.mode == 'simple':
            adj = self.env.get_adjacent_cells(self.env.mouse_pos)
            x, y = self.env.mouse_pos
            direction = None
            for d in ('up', 'down', 'left', 'right'):
                np = {
                    'up': (x - 1, y), 'down': (x + 1, y),
                    'left': (x, y - 1), 'right': (x, y + 1),
                }[d]
                if np == self.env.cheese_pos:
                    direction = d
                    break
            if direction is None:
                import random
                valid = [d for d, c in adj.items() if c != '#']
                if not valid:
                    self.status = 'lost'
                    self._rebuild_buttons()
                    return
                direction = random.choice(valid)
            self._try_move(direction)
            # generous safety cap so simple reflex doesn't loop forever
            if self.env.steps_taken >= self.size * self.size * 8 \
                    and self.status != 'won':
                self.status = 'lost'
                self._rebuild_buttons()

        else:  # bfs / astar
            if not self.planned_path:
                self.status = 'lost'
                self._rebuild_buttons()
                return
            idx = self.env.steps_taken + 1
            if idx >= len(self.planned_path):
                self.status = 'won' if self.env.is_cheese_reached() else 'lost'
                self._rebuild_buttons()
                return
            nx, ny = self.planned_path[idx]
            x, y = self.env.mouse_pos
            if nx < x:
                self._try_move('up')
            elif nx > x:
                self._try_move('down')
            elif ny < y:
                self._try_move('left')
            elif ny > y:
                self._try_move('right')

    # -- pygame loop ----------------------------------------------------
    def handle(self, event):
        for b in self.buttons:
            b.handle(event)

        if self.mode == 'player' and event.type == pygame.KEYDOWN:
            key = event.key
            direction = None
            if key in (pygame.K_UP, pygame.K_w):
                direction = 'up'
            elif key in (pygame.K_DOWN, pygame.K_s):
                direction = 'down'
            elif key in (pygame.K_LEFT, pygame.K_a):
                direction = 'left'
            elif key in (pygame.K_RIGHT, pygame.K_d):
                direction = 'right'
            if direction:
                self._try_move(direction)

    def update(self, dt):
        if self.status == 'playing' and self.mode != 'player':
            self.agent_elapsed += dt
            while self.agent_elapsed >= self.agent_delay \
                    and self.status == 'playing':
                self.agent_elapsed -= self.agent_delay
                self._agent_step()

    # -- drawing --------------------------------------------------------
    def draw(self, surface):
        surface.fill(BG)
        fonts = self.app.fonts

        # header
        draw_text(surface, self.MODE_TITLES[self.mode], fonts.h2,
                  TEXT_PRIMARY, (60, 48))
        draw_text(surface, self._subtitle(), fonts.small,
                  TEXT_SECONDARY, (60, 76))

        # stat cards
        self._draw_stats(surface, fonts)

        # board
        self._draw_board(surface)

        # status banner
        self._draw_banner(surface, fonts)

        # buttons + keyboard hint
        for b in self.buttons:
            b.draw(surface, fonts)
        if self.mode == 'player':
            self._draw_key_hint(surface, fonts)

    def _subtitle(self):
        if self.mode == 'player':
            return "Use arrow keys or WASD to move."
        if self.mode == 'simple':
            return "Acts only on what is immediately adjacent."
        path_len = max(0, len(self.planned_path) - 1) if self.planned_path else 0
        return (f"Planned shortest path: {path_len} steps, "
                f"{self.nodes_explored} nodes explored.")

    def _draw_stats(self, surface, fonts):
        if self.mode == 'player':
            stats = [
                ("Steps taken", str(self.env.steps_taken)),
                ("Steps remaining", str(max(0, self.step_budget - self.env.steps_taken))),
                ("Grid", f"{self.size} × {self.size}"),
            ]
        else:
            planned = "—"
            nodes = "—"
            if self.mode in ('bfs', 'astar'):
                planned = str(max(0, len(self.planned_path) - 1)
                              if self.planned_path else 0)
                nodes = str(self.nodes_explored)
            stats = [
                ("Steps taken", str(self.env.steps_taken)),
                ("Planned length", planned),
                ("Nodes explored", nodes),
            ]

        y = 110
        gap = 12
        count = len(stats)
        total_w = WINDOW_W - 120
        card_w = (total_w - gap * (count - 1)) // count
        for i, (label, value) in enumerate(stats):
            x = 60 + i * (card_w + gap)
            r = pygame.Rect(x, y, card_w, 64)
            draw_round_rect(surface, SURFACE_SOFT, r, radius=8)
            draw_text(surface, label, fonts.small, TEXT_SECONDARY,
                      (x + 14, y + 10))
            draw_text(surface, value, fonts.stat, TEXT_PRIMARY,
                      (x + 14, y + 28))

    def _draw_board(self, surface):
        # available area: y from 200 to WINDOW_H - 130
        top_y = 200
        bottom_y = WINDOW_H - 130
        avail_h = bottom_y - top_y
        avail_w = WINDOW_W - 120
        board_px = min(avail_h, avail_w, 460)

        cell = board_px // self.size
        pad = 6
        board_w = cell * self.size + pad * 2
        board_h = cell * self.size + pad * 2
        bx = (WINDOW_W - board_w) // 2
        by = top_y + (avail_h - board_h) // 2

        # board container
        board_rect = pygame.Rect(bx, by, board_w, board_h)
        draw_round_rect(surface, SURFACE_SOFT, board_rect, radius=10)
        draw_round_rect(surface, BORDER, board_rect, radius=10, width=1)

        # cells
        for i in range(self.size):
            for j in range(self.size):
                r = pygame.Rect(bx + pad + j * cell,
                                by + pad + i * cell,
                                cell - 3, cell - 3)
                is_wall = self.env.grid[i][j] == '#'
                is_mouse = (i, j) == self.env.mouse_pos
                is_cheese = (i, j) == self.env.cheese_pos

                if is_wall:
                    draw_round_rect(surface, WALL_COLOR, r, radius=5)
                    draw_round_rect(surface, WALL_BORDER, r, radius=5, width=1)
                    continue

                if self.mode in ('bfs', 'astar') \
                        and (i, j) in self.path_cells \
                        and not is_mouse and not is_cheese:
                    draw_round_rect(surface, PATH_COLOR, r, radius=5)
                elif self.mode == 'simple' and (i, j) in self.visited_cells \
                        and not is_mouse and not is_cheese:
                    draw_round_rect(surface, VISITED_COLOR, r, radius=5)
                else:
                    draw_round_rect(surface, FLOOR_COLOR, r, radius=5)
                draw_round_rect(surface, BORDER, r, radius=5, width=1)

                if is_cheese and not is_mouse:
                    # highlight goal with a subtle teal ring
                    draw_round_rect(surface, GOAL_RING, r, radius=5, width=2)
                    draw_cheese(surface, r)
                if is_mouse:
                    draw_mouse(surface, r)

    def _draw_banner(self, surface, fonts):
        if self.status == 'won':
            bg, fg, text = SUCCESS_BG, SUCCESS_TEXT, (
                f"Cheese secured in {self.env.steps_taken} "
                f"step{'s' if self.env.steps_taken != 1 else ''}.")
        elif self.status == 'lost':
            bg, fg, text = DANGER_BG, DANGER_TEXT, "Out of moves. Try a new maze."
        else:
            return

        r = pygame.Rect(60, WINDOW_H - 128, WINDOW_W - 120, 40)
        draw_round_rect(surface, bg, r, radius=8)
        draw_text(surface, text, fonts.body, fg, (r.x + 14, r.centery),
                  align="midleft")

    def _draw_key_hint(self, surface, fonts):
        x = 60
        y = WINDOW_H - 28
        label_img = fonts.small.render("Move:", True, TEXT_SECONDARY)
        bx = x + 470
        surface.blit(label_img, (bx, y - 2))
        bx += label_img.get_width() + 6
        for k in ("↑", "↓", "←", "→"):
            key_rect = pygame.Rect(bx, y - 4, 22, 18)
            draw_round_rect(surface, SURFACE, key_rect, radius=4)
            draw_round_rect(surface, BORDER, key_rect, radius=4, width=1)
            img = fonts.mono.render(k, True, TEXT_PRIMARY)
            surface.blit(img, img.get_rect(center=key_rect.center))
            bx += 26


# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Harvest Mouse")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.current = LobbyScreen(self)
        self.running = True

    def start_game(self, mode, size, density):
        self.current = GameScreen(self, mode, size, density)

    def go_to_lobby(self, size=None, density=None):
        screen = LobbyScreen(self)
        if size is not None:
            screen.size = int(size)
            screen.size_slider.value = int(size)
        if density is not None:
            screen.density = density
            screen.density_slider.value = int(density * 100)
        self.current = screen

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.current.handle(event)
            self.current.update(dt)
            self.current.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


def run():
    App().run()


if __name__ == "__main__":
    run()
    sys.exit(0)
