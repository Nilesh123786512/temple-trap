"""
**Note**:This is AI Generated for visualisation.
Temple Trap - Pygame Visualization
This file visualizes the Temple Trap puzzle using pygame,
integrating the existing solver and levels without modifying them.

Controls:
- Left/Right Arrow: Switch level
- R: Reset current level
- S: Solve (compute A* solution and queue actions)
- N: Next step (apply one queued action)
- A: Auto-play solution (toggle)
- Mouse click:
    - Slides a tile if it's adjacent to the blank space.
- Pawn Movement:
    - SHIFT + Arrow Keys: Move pawn in that direction.
    - Number Keys (1-9): Move pawn to that cell position.
- ESC: Quit
- ESC: Quit

Run:
    python gemini/temple_trap_game.py
"""

import sys
import re
import os
import pygame
from typing import Dict, List, Tuple, Optional

# Import game logic & data (do not modify these files)
from puzzle_levels import LEVELS, TILES, update_tiles_orientation
from temple_trap_solver import (
    GameState,
    get_neighbors,
    get_reachable_cells,
    a_star_search,
    can_move_between_cells,
)

# ------------- Config -------------
GRID_SIZE = 3
CELL_SIZE = 140
BOARD_PX = GRID_SIZE * CELL_SIZE
MARGIN = 20
RIGHT_PANEL_WIDTH = 320
SCREEN_W = BOARD_PX + RIGHT_PANEL_WIDTH + MARGIN * 3
SCREEN_H = BOARD_PX + MARGIN * 2 + 50

FPS = 60
STEP_INTERVAL_MS = 300  # autoplay step delay

# Colors
COL_BG = (25, 25, 28)
COL_BOARD_BG = (50, 52, 60)
COL_EMPTY = (70, 72, 80)
COL_TILE = (195, 180, 150)
COL_GRID = (100, 104, 112)
COL_TEXT = (235, 235, 235)
COL_HINT = (80, 200, 120)

COL_OPEN_GROUND = (156, 102, 31)  # brown-ish for ground openings
COL_OPEN_TOP = (66, 135, 245)     # blue for top openings

COL_HOLE = (40, 40, 45)
COL_STAIRS = (230, 200, 90)

COL_PAWN = (50, 220, 50) # Green dot for pawn

# Directions mapping (solver uses 1..4: 1 top, 2 right, 3 bottom, 4 left)
SIDE_TOP = 1
SIDE_RIGHT = 2
SIDE_BOTTOM = 3
SIDE_LEFT = 4

# ------------- Utilities -------------
def cell_to_xy(idx: int) -> Tuple[int, int]:
    r, c = divmod(idx, GRID_SIZE)
    x = MARGIN + c * CELL_SIZE
    y = MARGIN + r * CELL_SIZE
    return x, y

def inside_board(mx: int, my: int) -> bool:
    return (MARGIN <= mx < MARGIN + BOARD_PX) and (MARGIN <= my < MARGIN + BOARD_PX)

def pos_to_index(mx: int, my: int) -> Optional[int]:
    if not inside_board(mx, my):
        return None
    c = (mx - MARGIN) // CELL_SIZE
    r = (my - MARGIN) // CELL_SIZE
    idx = r * GRID_SIZE + c
    if 0 <= idx < GRID_SIZE * GRID_SIZE:
        return int(idx)
    return None

def shorten_name(tile_name: str) -> str:
    # Visual short label on tile
    if tile_name in {"+", "=", ">", "*", "X", "."}:
        return tile_name
    if tile_name.upper().startswith("RECT"):
        return "RECT"
    if tile_name.upper().startswith("RHOM"):
        return "RHOM"
    return tile_name[:4].upper()

def draw_opening(surface: pygame.Surface, rect: pygame.Rect, side: int, color: Tuple[int, int, int], thickness: int = 8):
    cx, cy = rect.center
    pad = 20
    inner = 24  # distance from edge into the tile

    if side == SIDE_TOP:
        start = (rect.centerx, rect.top + pad)
        end = (rect.centerx, rect.top + inner)
    elif side == SIDE_RIGHT:
        start = (rect.right - pad, rect.centery)
        end = (rect.right - inner, rect.centery)
    elif side == SIDE_BOTTOM:
        start = (rect.centerx, rect.bottom - pad)
        end = (rect.centerx, rect.bottom - inner)
    elif side == SIDE_LEFT:
        start = (rect.left + pad, rect.centery)
        end = (rect.left + inner, rect.centery)
    else:
        return
    pygame.draw.line(surface, color, start, end, thickness)

def draw_stairs(surface: pygame.Surface, rect: pygame.Rect, side: int):
    # Draw a small wedge/ladder indicator on the given side
    # We'll render a small triangle pointing towards the side
    inset = 28
    if side == SIDE_TOP:
        pts = [(rect.centerx, rect.top + inset),
               (rect.centerx - 14, rect.top + inset + 20),
               (rect.centerx + 14, rect.top + inset + 20)]
    elif side == SIDE_RIGHT:
        pts = [(rect.right - inset, rect.centery),
               (rect.right - inset - 20, rect.centery - 14),
               (rect.right - inset - 20, rect.centery + 14)]
    elif side == SIDE_BOTTOM:
        pts = [(rect.centerx, rect.bottom - inset),
               (rect.centerx - 14, rect.bottom - inset - 20),
               (rect.centerx + 14, rect.bottom - inset - 20)]
    elif side == SIDE_LEFT:
        pts = [(rect.left + inset, rect.centery),
               (rect.left + inset + 20, rect.centery - 14),
               (rect.left + inset + 20, rect.centery + 14)]
    else:
        return
    pygame.draw.polygon(surface, COL_STAIRS, pts)

def draw_exit(surface: pygame.Surface, font: pygame.font.Font):
    # Draw a marker to the left of cell 0 (top-left cell)
    x0, y0 = cell_to_xy(0)
    arrow_rect = pygame.Rect(x0 - 40, y0 + CELL_SIZE // 2 - 12, 32, 24)
    pygame.draw.rect(surface, (60, 160, 75), arrow_rect, border_radius=6)
    # Draw a small triangle arrow pointing left
    pts = [(arrow_rect.right, arrow_rect.centery),
           (arrow_rect.left + 8, arrow_rect.top),
           (arrow_rect.left + 8, arrow_rect.bottom)]
    pygame.draw.polygon(surface, (70, 220, 100), pts)
    txt = font.render("EXIT", True, (0, 0, 0))
    surface.blit(txt, (arrow_rect.left + 4, arrow_rect.top - 20))

# ------------- Game Class -------------
class TempleTrapGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Temple Trap - Pygame Visualization")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small = pygame.font.SysFont("consolas", 16)

        # Image assets
        self.tile_images: Dict[str, pygame.Surface] = {}
        self._load_assets()

        # Levels
        self.level_names: List[str] = list(LEVELS.keys())
        if not self.level_names:
            print("No levels found.")
            pygame.quit()
            sys.exit(1)
        self.level_index = 0

        # State
        self.tiles_state: Dict[str, dict] = {}
        self.board: List[Optional[str]] = []
        self.pawn_pos: int = 0
        self.pawn_layer: str = "GROUND"
        self.blank_pos: int = 0

        # Solver playback
        self.action_queue: List[str] = []
        self.autoplay: bool = False
        self._last_step_ms: int = 0

        # Level orientation data
        self.orientations: List[int] = []

        self.load_level(self.level_names[self.level_index])

    def _load_assets(self):
        """Load all tile images from the images directory."""
        # Use absolute path to ensure images are found regardless of execution directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(script_dir, "images")
        if not os.path.isdir(img_path):
            print(f"Warning: Image directory not found at '{img_path}'")
            return
        
        # Mapping from solver names to filenames
        name_map = {
            ".": "dot.png",
            "*": "star.png",
            ">": "triangle.png"
        }

        for fname in os.listdir(img_path):
            if fname.endswith(".png"):
                key = os.path.splitext(fname)[0]
                # Reverse lookup for keys like '.', '*', etc.
                rev_map_key = next((k for k, v in name_map.items() if v == fname), None)
                final_key = rev_map_key or key

                try:
                    img = pygame.image.load(os.path.join(img_path, fname)).convert_alpha()
                    # Scale image to fit within the cell with a small margin
                    self.tile_images[final_key] = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))
                except pygame.error as e:
                    print(f"Error loading image {fname}: {e}")
        print(f"Loaded {len(self.tile_images)} tile images.")

    def toggle_autoplay(self):
        """Toggle autoplay ON or OFF."""
        self.autoplay = not self.autoplay
        # Reset timer only when turning it on and there's a queue
        if self.autoplay and self.action_queue:
            self._last_step_ms = pygame.time.get_ticks()
        else:
            self.autoplay = False # Ensure it's off if no queue

    def load_level(self, name: str):
        level_data = LEVELS[name]
        # Store orientations for rendering rotations
        self.orientations = level_data.get("orientation", [0] * (GRID_SIZE * GRID_SIZE))
        # Get tile state definitions for the given level
        self.tiles_state = update_tiles_orientation(TILES, level_data, verbose=False)
        self.board = list(level_data["board"])
        self.pawn_pos = int(level_data["pawn_pos"])
        self.pawn_layer = "GROUND"  # default (solver uses this default too)
        self.blank_pos = self.board.index(None)
        # Reset any playback
        self.action_queue.clear()
        self.autoplay = False
        self._last_step_ms = 0

    def reset_level(self):
        self.load_level(self.level_names[self.level_index])

    def build_state(self) -> GameState:
        return GameState(
            board=list(self.board),
            pawn_pos=self.pawn_pos,
            pawn_layer=self.pawn_layer,
            g_cost=0,
            path=[],
            tiles_state=self.tiles_state,
        )

    # --------- Interaction Logic ---------
    def get_allowed_pawn_destinations(self) -> Dict[int, Tuple[str, int]]:
        """
        Returns a mapping: pos -> (layer, cost) for cells that are reachable AND have a hole.
        If both layers are reachable for same pos, choose the cheaper cost.
        """
        st = self.build_state()
        reach = get_reachable_cells(st)
        allowed: Dict[int, Tuple[str, int]] = {}
        for (pos, layer), cost in reach.items():
            if pos < 0 or pos >= GRID_SIZE * GRID_SIZE:
                continue
            tile_name = self.board[pos]
            if tile_name is None:
                continue
            tile_def = self.tiles_state.get(tile_name, {})
            if tile_def.get("has_hole", False):
                if pos not in allowed or cost < allowed[pos][1]:
                    allowed[pos] = (layer, cost)
        return allowed

    def click_on_cell(self, idx: int):
        # Mouse click is ONLY for sliding tiles.
        neighbors = get_neighbors(self.blank_pos)
        if idx in neighbors:
            # Do not allow sliding the tile the pawn is on.
            if idx == self.pawn_pos:
                return

            # Slide tile at idx into the blank
            if self.board[idx] is not None:
                # Swap tile names
                self.board[self.blank_pos], self.board[idx] = self.board[idx], self.board[self.blank_pos]
                # Swap orientations as well to preserve rotation
                self.orientations[self.blank_pos], self.orientations[idx] = self.orientations[idx], self.orientations[self.blank_pos]
                self.blank_pos = idx
                # Note: We are not checking if the pawn is on the tile being moved,
                # allowing for more flexible manual play than the solver.

    def move_pawn_to(self, dest_pos: int):
        """Move pawn to a destination if it's in the allowed list."""
        allowed = self.get_allowed_pawn_destinations()
        if dest_pos in allowed:
            target_layer, _ = allowed[dest_pos]
            self.pawn_pos = dest_pos
            self.pawn_layer = target_layer

    def move_pawn_direction(self, dx: int, dy: int):
        """Move pawn one step in a given direction (dx, dy)."""
        if not (-1 <= dx <= 1 and -1 <= dy <= 1 and dx * dy == 0 and dx + dy != 0):
            return  # Invalid direction
        
        curr_r, curr_c = divmod(self.pawn_pos, GRID_SIZE)
        next_r, next_c = curr_r + dy, curr_c + dx

        if not (0 <= next_r < GRID_SIZE and 0 <= next_c < GRID_SIZE):
            return # Out of bounds

        next_pos = next_r * GRID_SIZE + next_c
        self.move_pawn_to(next_pos)

    # --------- Solver Integration ---------
    SLIDE_RE = re.compile(r"^Slide\s+(.+?)\s+(Left|Right|Up|Down)\s+\(from\s+(\d+)\s+to\s+(\d+)\)")
    MOVE_RE = re.compile(r"^Move pawn to\s+(\d+)\s+\((TOP|GROUND)\)")

    def solve(self):
        self.action_queue.clear()
        self.autoplay = False
        st = self.build_state()
        path, total_cost = a_star_search(st)
        if not path:
            self.action_queue = ["No solution found."]
            return
        self.action_queue = list(path)  # copy
        # We'll handle "Walk to Exit!" specially during playback

    def apply_next_action(self):
        if not self.action_queue:
            return
        action = self.action_queue.pop(0)
        if action == "No solution found.":
            return

        if action.strip() == "Walk to Exit!":
            # Auto walk to exit by finding a shortest path to (0, valid_layer)
            self.walk_to_exit()
            return

        m_slide = self.SLIDE_RE.match(action)
        if m_slide:
            from_pos = int(m_slide.group(3))
            to_blank = int(m_slide.group(4))
            # Perform slide: swap tile at from_pos with blank at to_blank
            if 0 <= from_pos < GRID_SIZE * GRID_SIZE and 0 <= to_blank < GRID_SIZE * GRID_SIZE:
                if self.board[to_blank] is None and self.board[from_pos] is not None:
                    # Swap tile names
                    self.board[to_blank], self.board[from_pos] = self.board[from_pos], self.board[to_blank]
                    # Swap orientations to preserve rotation during solver playback
                    self.orientations[to_blank], self.orientations[from_pos] = self.orientations[from_pos], self.orientations[to_blank]
                    self.blank_pos = from_pos  # After sliding, blank moves to previous tile position
            return

        m_move = self.MOVE_RE.match(action)
        if m_move:
            dest = int(m_move.group(1))
            layer = m_move.group(2)
            # Trust solver, directly move
            self.pawn_pos = dest
            self.pawn_layer = layer
            return

        # Fallback: ignore unknown action strings

    def walk_to_exit(self):
        """
        After solver signals 'Walk to Exit!', compute and perform a sequence of pawn moves
        to the actual exit cell (0) on the valid layer (GROUND or TOP depending on tile openings).
        """
        target_layer = None
        tile_name_at_zero = self.board[0]
        if tile_name_at_zero is None:
            return
        tile_def = self.tiles_state.get(tile_name_at_zero, {})
        if SIDE_LEFT in tile_def.get("ground_opens", set()):
            target_layer = "GROUND"
        elif SIDE_LEFT in tile_def.get("top_opens", set()):
            target_layer = "TOP"
        else:
            # Exit isn't actually open; nothing to do
            return
        path = self._bfs_path_to((self.pawn_pos, self.pawn_layer), (0, target_layer))
        if path and len(path) > 1:
            # path is a list of (pos, layer), include start; apply moves along it
            # Skip the first (current) entry
            for pos, layer in path[1:]:
                self.pawn_pos = pos
                self.pawn_layer = layer

    def _bfs_path_to(self, start: Tuple[int, str], goal: Tuple[int, str]) -> Optional[List[Tuple[int, str]]]:
        """
        Breadth-first search on the layered graph of cells to find a path
        using the same movement rules as get_reachable_cells (including stairs).
        Returns list of (pos, layer) from start to goal.
        """
        st = self.build_state()
        from collections import deque

        q = deque()
        q.append(start)
        visited = set([start])
        parent: Dict[Tuple[int, str], Optional[Tuple[int, str]]] = {start: None}

        while q:
            curr = q.popleft()
            if curr == goal:
                # reconstruct
                path = []
                at = curr
                while at is not None:
                    path.append(at)
                    at = parent[at]
                path.reverse()
                return path

            curr_pos, curr_layer = curr

            # neighbors by adjacency
            for nb in get_neighbors(curr_pos).keys():
                if can_move_between_cells(st, curr_pos, nb, curr_layer):
                    nxt = (nb, curr_layer)
                    if nxt not in visited:
                        visited.add(nxt)
                        parent[nxt] = curr
                        q.append(nxt)

            # stairs transition within same tile (zero cost)
            curr_tile_name = self.board[curr_pos]
            if curr_tile_name:
                tile_def = self.tiles_state.get(curr_tile_name, {})
                if tile_def.get("has_stairs", False):
                    other = "GROUND" if curr_layer == "TOP" else "TOP"
                    nxt = (curr_pos, other)
                    if nxt not in visited:
                        visited.add(nxt)
                        parent[nxt] = curr
                        q.append(nxt)
        return None

    # --------- Rendering ---------
    def draw_tile(self, surface: pygame.Surface, idx: int):
        x, y = cell_to_xy(idx)
        rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)

        # Draw background cell
        pygame.draw.rect(surface, COL_BOARD_BG, rect, border_radius=12)

        tile_name = self.board[idx]
        if tile_name is None:
            # Draw empty cell marker
            pygame.draw.rect(surface, COL_EMPTY, rect.inflate(-10, -10), border_radius=10)
            return

        # Blit the tile image, rotated
        if tile_name in self.tile_images:
            orientation_angle = self.orientations[idx] * -90 # Pygame rotates counter-clockwise
            rotated_img = pygame.transform.rotate(self.tile_images[tile_name], orientation_angle)
            img_rect = rotated_img.get_rect(center=rect.center)
            surface.blit(rotated_img, img_rect)
        else:
            # Fallback if image is missing: draw old style
            pygame.draw.rect(surface, COL_TILE, rect, border_radius=12)
            label = self.small.render(f"{shorten_name(tile_name)}?", True, (255, 0, 0))
            surface.blit(label, (rect.x + 8, rect.y + 6))

        # Outline
        pygame.draw.rect(surface, COL_GRID, rect, width=2, border_radius=12)

    def draw_pawn(self, surface: pygame.Surface):
        x, y = cell_to_xy(self.pawn_pos)
        rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        
        # Draw a green dot for the pawn
        pygame.draw.circle(surface, COL_PAWN, rect.center, 18)
        # Add a subtle border and highlight to show layer
        if self.pawn_layer == "TOP":
            pygame.draw.circle(surface, (255, 255, 0, 150), rect.center, 18, width=3)
        else: # GROUND
            pygame.draw.circle(surface, (0, 0, 0, 150), rect.center, 18, width=3)

    def draw_reachable_hints(self, surface: pygame.Surface):
        allowed = self.get_allowed_pawn_destinations()
        for pos in allowed.keys():
            x, y = cell_to_xy(pos)
            rect = pygame.Rect(x + 6, y + 6, CELL_SIZE - 12, CELL_SIZE - 12)
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill((COL_HINT[0], COL_HINT[1], COL_HINT[2], 60))
            surface.blit(s, (rect.x, rect.y))
            pygame.draw.rect(surface, COL_HINT, rect, width=2, border_radius=10)

    def draw_right_panel(self, surface: pygame.Surface):
        panel_x = MARGIN * 2 + BOARD_PX
        panel_rect = pygame.Rect(panel_x, MARGIN, RIGHT_PANEL_WIDTH, self.screen.get_height() - MARGIN * 2)
        pygame.draw.rect(surface, COL_BOARD_BG, panel_rect, border_radius=12)

        lv_name = self.level_names[self.level_index]
        head = self.font.render(f"Level: {lv_name}", True, COL_TEXT)
        surface.blit(head, (panel_rect.x + 12, panel_rect.y + 12))

        info_lines = [
            "Controls:",
            "  Left/Right: Switch Level",
            "  R: Reset Level",
            "  S: Solve (A*)",
            "  N: Next Step",
            "  A: Autoplay Toggle",
            "",
            "Mouse:",
            "  - Click adjacent tile to slide",
            "  - Shift + Click the tile to move",
            "    the pawn to the position",
            "",
            "Pawn Movement:",
            "  - SHIFT + Arrows: Directional",
            "  - Numpad 1-9: To Cell",
            "",
            f"Pawn: pos={self.pawn_pos}, layer={self.pawn_layer}",
            f"Blank: pos={self.blank_pos}",
            f"Queued steps: {len(self.action_queue)}",
            f"Autoplay: {'ON' if self.autoplay else 'OFF'}",
        ]
        y = panel_rect.y + 48
        for line in info_lines:
            txt = self.small.render(line, True, COL_TEXT)
            surface.blit(txt, (panel_rect.x + 12, y))
            y += 20

        # If the exit is open in any layer, show a hint
        tile0 = self.board[0]
        if tile0:
            tdef = self.tiles_state.get(tile0, {})
            open_ground = SIDE_LEFT in tdef.get("ground_opens", set())
            open_top = SIDE_LEFT in tdef.get("top_opens", set())
            if open_ground or open_top:
                hint = self.small.render("Exit is reachable when pawn can walk to cell 0.", True, (180, 255, 180))
                surface.blit(hint, (panel_rect.x + 12, panel_rect.bottom - 28))

    # --------- Main Loop ---------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    is_shift = mods & pygame.KMOD_SHIFT

                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Level navigation (no shift)
                    elif not is_shift and event.key == pygame.K_RIGHT:
                        self.level_index = (self.level_index + 1) % len(self.level_names)
                        self.load_level(self.level_names[self.level_index])
                    elif not is_shift and event.key == pygame.K_LEFT:
                        self.level_index = (self.level_index - 1) % len(self.level_names)
                        self.load_level(self.level_names[self.level_index])

                    # Game controls (no shift)
                    elif not is_shift and event.key == pygame.K_r: self.reset_level()
                    elif not is_shift and event.key == pygame.K_s: self.solve()
                    elif not is_shift and event.key == pygame.K_n: self.apply_next_action()
                    elif not is_shift and event.key == pygame.K_a: self.toggle_autoplay()

                    # Pawn movement (SHIFT + ARROWS)
                    elif is_shift and event.key == pygame.K_UP: self.move_pawn_direction(0, -1)
                    elif is_shift and event.key == pygame.K_DOWN: self.move_pawn_direction(0, 1)
                    elif is_shift and event.key == pygame.K_LEFT: self.move_pawn_direction(-1, 0)
                    elif is_shift and event.key == pygame.K_RIGHT: self.move_pawn_direction(1, 0)
                    
                    # Pawn movement (NUMPAD 1-9) -> maps to cell 0-8
                    elif event.key in [pygame.K_1, pygame.K_KP1]: self.move_pawn_to(0)
                    elif event.key in [pygame.K_2, pygame.K_KP2]: self.move_pawn_to(1)
                    elif event.key in [pygame.K_3, pygame.K_KP3]: self.move_pawn_to(2)
                    elif event.key in [pygame.K_4, pygame.K_KP4]: self.move_pawn_to(3)
                    elif event.key in [pygame.K_5, pygame.K_KP5]: self.move_pawn_to(4)
                    elif event.key in [pygame.K_6, pygame.K_KP6]: self.move_pawn_to(5)
                    elif event.key in [pygame.K_7, pygame.K_KP7]: self.move_pawn_to(6)
                    elif event.key in [pygame.K_8, pygame.K_KP8]: self.move_pawn_to(7)
                    elif event.key in [pygame.K_9, pygame.K_KP9]: self.move_pawn_to(8)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mods = pygame.key.get_mods()
                    is_shift = mods & pygame.KMOD_SHIFT
                    mx, my = event.pos
                    idx = pos_to_index(mx, my)
                    if idx is not None:
                        if is_shift:
                            self.move_pawn_to(idx)
                        else:
                            self.click_on_cell(idx)

            # Autoplay timing
            if self.autoplay and self.action_queue:
                now = pygame.time.get_ticks()
                if (now - self._last_step_ms) >= STEP_INTERVAL_MS:
                    self.apply_next_action()
                    self._last_step_ms = now # Reset timer after each step
            elif not self.action_queue:
                self.autoplay = False # Turn off when queue is empty

            # Draw
            self.screen.fill(COL_BG)

            # Board background
            board_rect = pygame.Rect(MARGIN, MARGIN, BOARD_PX, BOARD_PX)
            pygame.draw.rect(self.screen, COL_BOARD_BG, board_rect, border_radius=12)

            # Exit marker
            draw_exit(self.screen, self.small)

            # Grid + tiles
            for idx in range(GRID_SIZE * GRID_SIZE):
                self.draw_tile(self.screen, idx)

            # Reachable hints
            self.draw_reachable_hints(self.screen)

            # Pawn
            self.draw_pawn(self.screen)

            # Panel
            self.draw_right_panel(self.screen)

            pygame.display.flip()

        pygame.quit()

# ------------- Main -------------
if __name__ == "__main__":
    game = TempleTrapGame()
    game.run()
