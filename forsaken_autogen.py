import tkinter as tk
import keyboard
import pyautogui
import ctypes
from PIL import ImageGrab
import threading
import time
import math
from collections import deque
import winsound

import interception


def sfx(sound_type):

    def _play():
        try:
            if sound_type == "boot":
                winsound.Beep(400, 40)
                winsound.Beep(600, 40)
                winsound.Beep(900, 40)
                winsound.Beep(1400, 80)
            elif sound_type == "grid_lock":
                winsound.Beep(800, 35)
                winsound.Beep(1100, 35)
                winsound.Beep(1600, 35)
                winsound.Beep(2200, 60)
            elif sound_type == "grid_fail":
                winsound.Beep(600, 60)
                winsound.Beep(350, 120)
            elif sound_type == "solve_start":
                winsound.Beep(1200, 30)
                winsound.Beep(1600, 30)
                winsound.Beep(2000, 50)
            elif sound_type == "done":
                winsound.Beep(600, 50)
                winsound.Beep(900, 50)
                winsound.Beep(1300, 50)
                winsound.Beep(1800, 100)
            elif sound_type == "step":
                winsound.Beep(1800, 18)
            elif sound_type == "connect":
                winsound.Beep(2200, 25)
                winsound.Beep(3200, 40)
            elif sound_type == "error":
                winsound.Beep(400, 80)
                winsound.Beep(250, 160)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()


def force_release():
    try:
        interception.mouse_up(button="left")
    except Exception:
        pass
    time.sleep(0.04)
    try:
        interception.mouse_up(button="left")
    except Exception:
        pass
    time.sleep(0.04)


COLOR_MATCH_THRESHOLD = 40
SAFE_SOLVE_TIME = 0.0
GRID = 6

PRESET_COLORS = {
    "red": (220, 50, 50),
    "orange": (230, 120, 30),
    "yellow": (230, 210, 50),
    "green": (50, 180, 50),
    "teal": (40, 180, 160),
    "blue": (50, 100, 220),
    "purple": (140, 50, 200),
    "magenta": (220, 50, 180),
    "pink": (230, 130, 160),
    "white": (230, 220, 210),
    "brown": (150, 80, 30),
    "lime": (130, 220, 50),
    "cyan": (50, 200, 230),
}

COLOR_HEX = {
    "red": "#dc3232",
    "orange": "#e6781e",
    "yellow": "#e6d232",
    "green": "#32b432",
    "teal": "#28b4a0",
    "blue": "#3264dc",
    "purple": "#8c32c8",
    "magenta": "#dc32b4",
    "pink": "#e68296",
    "white": "#e6dcd2",
    "brown": "#964b1e",
    "lime": "#82dc32",
    "cyan": "#32c8e6",
}


def nearest_preset_name(color):
    best_name, best_dist = None, float('inf')
    for name, preset in PRESET_COLORS.items():
        d = math.sqrt(sum((a - b)**2 for a, b in zip(color, preset)))
        if d < best_dist:
            best_dist = d
            best_name = name
    return best_name


def bfs_distance(start, goal, occupied):
    if start == goal:
        return 0
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        (r, c), dist = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nb = (r + dr, c + dc)
            if nb == goal:
                return dist + 1
            if 0 <= nb[0] < GRID and 0 <= nb[
                    1] < GRID and nb not in occupied and nb not in visited:
                visited.add(nb)
                queue.append((nb, dist + 1))
    return float('inf')


def count_reachable(start, occupied):
    visited = {start}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nb = (r + dr, c + dc)
            if 0 <= nb[0] < GRID and 0 <= nb[
                    1] < GRID and nb not in occupied and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited)


def all_pairs_reachable(pairs, pair_idx, occupied):
    for i in range(pair_idx, len(pairs)):
        s = tuple(pairs[i][0])
        e = tuple(pairs[i][1])
        free = occupied - {s, e}
        if bfs_distance(s, e, free) == float('inf'):
            return False
    return True


def order_pairs(pairs, walls):
    occupied = set(map(tuple, walls))
    for p in pairs:
        occupied.add(tuple(p[0]))
        occupied.add(tuple(p[1]))

    def pair_score(p):
        s = tuple(p[0])
        e = tuple(p[1])

        def free_neighbors(cell):
            return sum(
                1 for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= cell[0] + dr < GRID and 0 <= cell[1] + dc < GRID and (
                    cell[0] + dr, cell[1] + dc) not in occupied)

        fn_s = free_neighbors(s)
        fn_e = free_neighbors(e)
        dist = bfs_distance(s, e, occupied - {s, e})
        return (min(fn_s, fn_e), dist)

    return sorted(pairs, key=pair_score)


class SolverVisualizer:
    LINE_W = 3
    EXPLORE_W = 1
    TICK_SIZE = 5
    CORNER_ARM = 7

    def __init__(self, root, bbox, pairs, walls, pair_color_map, abort_event):
        self.bbox = bbox
        self.pairs = pairs
        self.walls = walls
        self.pair_color_map = pair_color_map
        self.abort_event = abort_event
        self._iter_count = 0
        self._path_lens = {}

        bx0, by0, bx1, by1 = bbox
        gw = bx1 - bx0
        gh = by1 - by0
        self.step_x = gw / 6.0
        self.step_y = gh / 6.0
        self._gw = gw
        self._gh = gh

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-transparentcolor", "#010101")
        self.win.geometry(f"{gw}x{gh}+{bx0}+{by0}")
        self.win.configure(bg="#010101")

        self.canvas = tk.Canvas(self.win,
                                width=gw,
                                height=gh,
                                bg="#010101",
                                highlightthickness=0)
        self.canvas.pack()
        self._draw_base()

    def _cell_xy(self, row, col):
        return (col * self.step_x) + (self.step_x / 2), (row * self.step_y) + (
            self.step_y / 2)

    def _draw_base(self):
        self.canvas.delete("base")

        for row in range(GRID):
            for col in range(GRID):
                sx = col * self.step_x
                sy = row * self.step_y
                ex = sx + self.step_x
                ey = sy + self.step_y
                a = self.CORNER_ARM
                corners = [
                    (sx, sy + a, sx, sy, sx + a, sy),
                    (ex - a, sy, ex, sy, ex, sy + a),
                    (ex, ey - a, ex, ey, ex - a, ey),
                    (sx + a, ey, sx, ey, sx, ey - a),
                ]
                for x1, y1, x2, y2, x3, y3 in corners:
                    self.canvas.create_line(x1,
                                            y1,
                                            x2,
                                            y2,
                                            x3,
                                            y3,
                                            fill="#2a2a2a",
                                            width=1,
                                            tags="base")

                label = f"{row},{col}"
                self.canvas.create_text(sx + 4,
                                        sy + 3,
                                        text=label,
                                        anchor="nw",
                                        fill="#1e1e1e",
                                        font=("Courier New", 6),
                                        tags="base")

        for (wr, wc) in self.walls:
            sx = wc * self.step_x
            sy = wr * self.step_y
            ex = sx + self.step_x
            ey = sy + self.step_y
            p = 6
            self.canvas.create_rectangle(sx + p,
                                         sy + p,
                                         ex - p,
                                         ey - p,
                                         outline="#3a3a3a",
                                         fill="",
                                         width=1,
                                         dash=(2, 3),
                                         tags="base")
            self.canvas.create_line(sx + p,
                                    sy + p,
                                    ex - p,
                                    ey - p,
                                    fill="#2a2a2a",
                                    width=1,
                                    tags="base")
            self.canvas.create_line(ex - p,
                                    sy + p,
                                    sx + p,
                                    ey - p,
                                    fill="#2a2a2a",
                                    width=1,
                                    tags="base")

        for idx, pair in enumerate(self.pairs):
            color_name = self.pair_color_map.get(idx, "white")
            hex_col = COLOR_HEX.get(color_name, "#ffffff")
            dim_col = self._dim(hex_col, 0.55)
            for (pr, pc) in pair:
                x, y = self._cell_xy(pr, pc)
                t = self.TICK_SIZE
                self.canvas.create_line(x - t,
                                        y,
                                        x + t,
                                        y,
                                        fill=dim_col,
                                        width=1,
                                        tags="base")
                self.canvas.create_line(x,
                                        y - t,
                                        x,
                                        y + t,
                                        fill=dim_col,
                                        width=1,
                                        tags="base")
                self.canvas.create_rectangle(x - 2,
                                             y - 2,
                                             x + 2,
                                             y + 2,
                                             outline=dim_col,
                                             fill="",
                                             width=1,
                                             tags="base")
                self.canvas.create_text(x + t + 2,
                                        y - t,
                                        text=color_name[:3].upper(),
                                        anchor="nw",
                                        fill=dim_col,
                                        font=("Courier New", 6),
                                        tags="base")

        self.canvas.update()

    def _update_hud(self, iters, phase, active_pair_idx=None, path_len=None):
        self.canvas.delete("hud")
        lines = [
            f"iter  {iters:>7}",
            f"phase {phase}",
        ]
        if active_pair_idx is not None:
            color_name = self.pair_color_map.get(active_pair_idx, "?")
            lines.append(f"pair  {color_name[:6]:<6} [{active_pair_idx}]")
        if path_len is not None:
            lines.append(f"depth {path_len:>7}")
        total_pairs = len(self.pairs)
        done = sum(1 for k, v in self._path_lens.items() if v > 0)
        lines.append(f"paths {done}/{total_pairs}")

        x = self._gw - 4
        y = 4
        for line in lines:
            self.canvas.create_text(x,
                                    y,
                                    text=line,
                                    anchor="ne",
                                    fill="#3a3a3a",
                                    font=("Courier New", 7),
                                    tags="hud")
            y += 11

    def draw_explore_step(self, pair_idx, path, iter_count=0):
        self.canvas.delete("explore")
        self._iter_count = iter_count
        if not path or len(path) < 2:
            self._update_hud(iter_count, "dfs", pair_idx, len(path))
            return
        color_name = self.pair_color_map.get(pair_idx, "white")
        hex_col = COLOR_HEX.get(color_name, "#ffffff")
        probe_col = self._dim(hex_col, 0.22)

        coords = []
        for (r, c) in path:
            x, y = self._cell_xy(r, c)
            coords += [x, y]

        self.canvas.create_line(*coords,
                                fill=probe_col,
                                width=self.EXPLORE_W,
                                capstyle="butt",
                                joinstyle="miter",
                                tags="explore")

        hx, hy = self._cell_xy(path[-1][0], path[-1][1])
        t = 3
        self.canvas.create_line(hx - t,
                                hy,
                                hx + t,
                                hy,
                                fill=probe_col,
                                width=1,
                                tags="explore")
        self.canvas.create_line(hx,
                                hy - t,
                                hx,
                                hy + t,
                                fill=probe_col,
                                width=1,
                                tags="explore")

        self._update_hud(iter_count, "dfs", pair_idx, len(path))

    def animate_solved_paths(self, paths, abort_event):
        self.canvas.delete("explore")
        self.canvas.delete("solved")
        total_cells = sum(len(p) for p in paths)

        drawn_count = 0
        for idx, path in enumerate(paths):
            if abort_event.is_set():
                return
            color_name = self.pair_color_map.get(idx, "white")
            hex_col = COLOR_HEX.get(color_name, "#ffffff")
            self._path_lens[idx] = len(path)

            drawn = []
            for step_i, (r, c) in enumerate(path):
                if abort_event.is_set():
                    return
                drawn.append((r, c))
                self.canvas.delete(f"anim_seg_{idx}")

                if len(drawn) >= 2:
                    coords = []
                    for (dr, dc) in drawn:
                        x, y = self._cell_xy(dr, dc)
                        coords += [x, y]
                    self.canvas.create_line(*coords,
                                            fill=hex_col,
                                            width=self.LINE_W,
                                            capstyle="butt",
                                            joinstyle="miter",
                                            tags=("solved", f"anim_seg_{idx}"))

                drawn_count += 1
                pct = int((drawn_count / max(total_cells, 1)) * 100)
                self._update_hud(self._iter_count, f"write {pct:>3}%", idx,
                                 step_i + 1)
                self.canvas.update()
                time.sleep(0.0095)

            time.sleep(0.01)

    def highlight_dragging(self, path_idx, path):
        self.canvas.delete("drag_highlight")
        color_name = self.pair_color_map.get(path_idx, "white")
        hex_col = COLOR_HEX.get(color_name, "#ffffff")
        bright_col = self._dim(hex_col, 1.6, clamp=True)

        coords = []
        for (r, c) in path:
            x, y = self._cell_xy(r, c)
            coords += [x, y]

        if len(coords) >= 4:
            self.canvas.create_line(*coords,
                                    fill=bright_col,
                                    width=self.LINE_W + 2,
                                    capstyle="butt",
                                    joinstyle="miter",
                                    tags="drag_highlight")

        self._update_hud(self._iter_count, "exec", path_idx, len(path))
        self.canvas.update()

    def simulate_drag_visual(self, path_idx, path, sleep_fn, abort_event):
        color_name = self.pair_color_map.get(path_idx, "white")
        hex_col = COLOR_HEX.get(color_name, "#ffffff")
        bright_col = self._dim(hex_col, 1.6, clamp=True)

        coords = []
        for (r, c) in path:
            x, y = self._cell_xy(r, c)
            coords += [x, y]

        if len(coords) >= 4:
            self.canvas.create_line(*coords,
                                    fill=bright_col,
                                    width=self.LINE_W + 2,
                                    capstyle="butt",
                                    joinstyle="miter",
                                    tags="drag_highlight")

        self._update_hud(self._iter_count, "exec", path_idx, len(path))
        self.canvas.update()

        last_i = len(path) - 1
        for i, (r, c) in enumerate(path):
            if abort_event.is_set():
                break
            self.canvas.delete("drag_cursor")
            x, y = self._cell_xy(r, c)
            t = 4
            self.canvas.create_line(x - t,
                                    y,
                                    x + t,
                                    y,
                                    fill="#ffffff",
                                    width=2,
                                    tags="drag_cursor")
            self.canvas.create_line(x,
                                    y - t,
                                    x,
                                    y + t,
                                    fill="#ffffff",
                                    width=2,
                                    tags="drag_cursor")
            self.canvas.update()
            if i < last_i:
                if i == last_i - 1:
                    sfx("connect")
                else:
                    sfx("step")
                sleep_fn(0.04)

        self.canvas.delete("drag_cursor")
        self.canvas.delete("drag_highlight")
        self.canvas.update()

    def clear_drag_highlight(self):
        self.canvas.delete("drag_highlight")
        self.canvas.update()

    def close(self):
        try:
            self.win.destroy()
        except Exception:
            pass

    @staticmethod
    def _dim(hex_col, factor, clamp=False):
        hex_col = hex_col.lstrip("#")
        r = int(hex_col[0:2], 16)
        g = int(hex_col[2:4], 16)
        b = int(hex_col[4:6], 16)
        r = min(255, int(r * factor)) if clamp else max(
            0, min(255, int(r * factor)))
        g = min(255, int(g * factor)) if clamp else max(
            0, min(255, int(g * factor)))
        b = min(255, int(b * factor)) if clamp else max(
            0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"


class GridOverlay:

    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-alpha", 0.3)
        self.top.attributes("-topmost", True)
        self.top.configure(cursor="cross")
        self.canvas = tk.Canvas(self.top, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.start_x = None
        self.start_y = None
        self.callback = callback
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        self.canvas.delete("overlay")
        min_x = min(self.start_x, event.x)
        max_x = max(self.start_x, event.x)
        min_y = min(self.start_y, event.y)
        max_y = max(self.start_y, event.y)
        w = max_x - min_x
        h = max_y - min_y
        self.canvas.create_rectangle(min_x,
                                     min_y,
                                     max_x,
                                     max_y,
                                     outline="#00ff00",
                                     width=2,
                                     tags="overlay")
        for i in range(1, 6):
            lx = min_x + (w * i / 6.0)
            self.canvas.create_line(lx,
                                    min_y,
                                    lx,
                                    max_y,
                                    fill="#00ff00",
                                    dash=(2, 2),
                                    tags="overlay")
            ly = min_y + (h * i / 6.0)
            self.canvas.create_line(min_x,
                                    ly,
                                    max_x,
                                    ly,
                                    fill="#00ff00",
                                    dash=(2, 2),
                                    tags="overlay")

    def on_release(self, event):
        if self.start_x is None:
            return
        min_x = min(self.start_x, event.x)
        max_x = max(self.start_x, event.x)
        min_y = min(self.start_y, event.y)
        max_y = max(self.start_y, event.y)
        if (max_x - min_x) > 50 and (max_y - min_y) > 50:
            self.callback((min_x, min_y), (max_x, max_y))
        self.top.destroy()


class ForsakenSolverTool:

    def __init__(self, root):
        self.root = root
        self.root.title("forsaken autogen v1.0")
        self.root.geometry("280x400")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.bg_color = "#d4d0c8"
        self.root.configure(bg=self.bg_color)

        self.top_left = None
        self.bottom_right = None
        self.is_solving = False
        self.cell_hitpoints = {}
        self.repeat_full = tk.BooleanVar(value=False)
        self.speed_mult = tk.DoubleVar(value=1.0)
        self.visualize_on = tk.BooleanVar(value=False)
        self._abort = threading.Event()
        self._visualizer = None

        self._build_ui()
        sfx("boot")
        threading.Thread(target=self.listen_hotkeys, daemon=True).start()
        threading.Thread(target=self._abort_watcher, daemon=True).start()

    def _build_ui(self):
        font_main = ("MS Sans Serif", 8)
        font_bold = ("MS Sans Serif", 8, "bold")

        tk.Label(self.root,
                 text="forsaken autogen",
                 bg=self.bg_color,
                 fg="black",
                 font=("Tahoma", 10, "bold")).pack(pady=(10, 5))

        status_frame = tk.Frame(self.root, bg="white", relief="sunken", bd=2)
        status_frame.pack(fill="x", padx=15, pady=5)
        self.status_lbl = tk.Label(status_frame,
                                   text="ready.",
                                   bg="white",
                                   fg="black",
                                   font=font_main,
                                   anchor="w",
                                   padx=5,
                                   pady=3)
        self.status_lbl.pack(fill="x")

        hotkey_frame = tk.Frame(self.root,
                                bg=self.bg_color,
                                relief="ridge",
                                bd=2)
        hotkey_frame.pack(fill="x", padx=15, pady=5)
        tk.Button(hotkey_frame,
                  text="draw grid box (f1)",
                  font=font_main,
                  command=self.open_grid_overlay).pack(fill="x",
                                                       padx=5,
                                                       pady=(5, 2))
        tk.Label(
            hotkey_frame,
            text=
            "draw on the grey cells only.\nnot the white border or pure black!",
            bg=self.bg_color,
            fg="#444444",
            font=("Tahoma", 7),
            justify="center").pack(anchor="center", padx=6, pady=(0, 3))
        tk.Label(
            hotkey_frame,
            text=
            "f3 = start solver\nf4 = test mouse\nf5 = print colors\nf6 = run path trace analysis",
            bg=self.bg_color,
            font=font_main,
            justify="left").pack(pady=2)

        set_frame = tk.Frame(self.root, bg=self.bg_color, relief="ridge", bd=2)
        set_frame.pack(fill="x", padx=15, pady=5)

        speed_row = tk.Frame(set_frame, bg=self.bg_color)
        speed_row.pack(fill="x", padx=5, pady=(5, 0))
        tk.Label(speed_row,
                 text="speed multiplier:",
                 bg=self.bg_color,
                 font=font_main).pack(side="left")
        self.speed_val_lbl = tk.Label(speed_row,
                                      text="1.00x",
                                      bg=self.bg_color,
                                      font=font_bold)
        self.speed_val_lbl.pack(side="right")
        tk.Scale(
            set_frame,
            variable=self.speed_mult,
            from_=0.5,
            to=1.5,
            resolution=0.05,
            orient="horizontal",
            showvalue=False,
            bg=self.bg_color,
            highlightthickness=0,
            bd=1,
            command=self._on_speed_change,
        ).pack(fill="x", expand=True, padx=5)

        cb_row = tk.Frame(set_frame, bg=self.bg_color)
        cb_row.pack(fill="x", padx=5, pady=(4, 5))
        tk.Checkbutton(cb_row,
                       text="repeat 4x",
                       variable=self.repeat_full,
                       bg=self.bg_color,
                       font=font_main,
                       activebackground=self.bg_color).pack(side="left")

        tk.Label(
            self.root,
            text=
            "only enable repeat 4x if gen is at 0%\nand has not been touched yet.\nany keypress aborts solve + visualizer.\ninterception driver active.",
            bg=self.bg_color,
            fg="#555555",
            font=("Tahoma", 7)).pack(side="bottom", pady=5)

    def _on_speed_change(self, val):
        self.speed_val_lbl.config(text=f"{float(val):.2f}x")

    def _sleep(self, base_seconds):
        end = time.time() + (base_seconds / self.speed_mult.get())
        while time.time() < end:
            if self._abort.is_set():
                return
            time.sleep(0.005)

    def update_status(self, text):
        self.status_lbl.config(text=text)

    def open_grid_overlay(self):
        GridOverlay(self.root, self.on_grid_selected)

    def on_grid_selected(self, top_l, bot_r):
        self.top_left = top_l
        self.bottom_right = bot_r
        sfx("grid_lock")
        self.update_status("grid locked. press f3 to solve.")

    def _abort_watcher(self):
        PASSTHROUGH = {'f1', 'f3', 'f4', 'f5', 'f6'}
        while True:
            event = keyboard.read_event(suppress=False)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name not in PASSTHROUGH:
                    if self.is_solving or self._visualizer is not None:
                        self._abort.set()
            time.sleep(0.01)

    def listen_hotkeys(self):
        while True:
            if keyboard.is_pressed('f1'):
                self.root.after(0, self.open_grid_overlay)
                time.sleep(0.3)
            elif keyboard.is_pressed('f4'):
                self.test_mouse()
                time.sleep(0.3)
            elif keyboard.is_pressed('f5'):
                self.debug_print_colors()
                time.sleep(0.3)
            elif keyboard.is_pressed('f3'):
                if not self.top_left or not self.bottom_right:
                    self.update_status("set grid first!")
                    sfx("error")
                elif not self.is_solving:
                    self._abort.clear()
                    self.is_solving = True
                    self.update_status("solving...")
                    sfx("solve_start")
                    threading.Thread(target=self.execute_solve,
                                     daemon=True).start()
                time.sleep(0.3)
            elif keyboard.is_pressed('f6'):
                if not self.top_left or not self.bottom_right:
                    self.update_status("set grid first!")
                    sfx("error")
                elif not self.is_solving:
                    self._abort.clear()
                    self.is_solving = True
                    self.update_status("path trace analysis...")
                    sfx("solve_start")
                    threading.Thread(target=self.execute_solve_visual,
                                     daemon=True).start()
                time.sleep(0.3)
            time.sleep(0.02)

    def move_to(self, x, y):
        interception.move_to(int(x), int(y))

    def btn_down(self):
        interception.mouse_down(button="left")

    def btn_up(self):
        interception.mouse_up(button="left")

    def test_mouse(self):
        x, y = pyautogui.position()
        force_release()
        self.move_to(x, y)
        self._sleep(0.05)
        self.btn_down()
        self._sleep(0.05)
        for tx, ty in [(x + 80, y), (x + 80, y + 80), (x, y + 80), (x, y)]:
            self.move_to(tx, ty)
            self._sleep(0.04)
        self.btn_up()
        self.update_status("test done.")

    def debug_print_colors(self):
        if not (self.top_left and self.bottom_right):
            self.update_status("set grid first!")
            return
        bbox = (self.top_left[0], self.top_left[1], self.bottom_right[0],
                self.bottom_right[1])
        screen = ImageGrab.grab(bbox=bbox)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        step_x = width / 6.0
        step_y = height / 6.0
        print(f"\n── color dump (bbox={bbox}) ──")
        for row in range(6):
            for col in range(6):
                cx = int((col * step_x) + (step_x / 2))
                cy = int((row * step_y) + (step_y / 2))
                r, g, b = screen.getpixel((cx, cy))
                color = self.sample_cell_color(screen, cx, cy, step_x, step_y)
                if color:
                    name = nearest_preset_name(color)
                    print(
                        f"  [{row},{col}] raw=({r:3},{g:3},{b:3})  sampled={color}  → {name}"
                    )
                else:
                    print(f"  [{row},{col}] raw=({r:3},{g:3},{b:3})  empty")
        print("─────────────────────\n")
        self.update_status("colors printed to console.")

    def execute_solve_visual(self):
        try:
            bbox = (self.top_left[0], self.top_left[1], self.bottom_right[0],
                    self.bottom_right[1])
            screen = ImageGrab.grab(bbox=bbox)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            step_x = width / 6.0
            step_y = height / 6.0

            pairs, walls, hitpoints = self.detect_grid(screen, bbox, step_x,
                                                       step_y)
            self.cell_hitpoints = hitpoints

            if not pairs:
                self.update_status("no pairs detected. check grid.")
                sfx("error")
                return

            ordered_pairs = order_pairs(pairs, walls)

            name_to_cells_map = {}
            for row in range(GRID):
                for col in range(GRID):
                    cx = int((col * step_x) + (step_x / 2))
                    cy = int((row * step_y) + (step_y / 2))
                    color = self.sample_cell_color(screen, cx, cy, step_x,
                                                   step_y)
                    if color:
                        name = nearest_preset_name(color)
                        name_to_cells_map.setdefault(name, []).append(
                            (row, col))

            pair_color_map = {}
            for idx, pair in enumerate(ordered_pairs):
                pair_set = set(map(tuple, pair))
                for name, cells in name_to_cells_map.items():
                    if len(cells) == 2 and set(map(tuple, cells)) == pair_set:
                        pair_color_map[idx] = name
                        break
                if idx not in pair_color_map:
                    pair_color_map[idx] = "white"

            vis = SolverVisualizer(self.root, bbox, ordered_pairs, walls,
                                   pair_color_map, self._abort)
            self._visualizer = vis

            self.update_status("path trace analysis: solving...")
            self.dfs_iterations = 0
            paths = self.solve_grid_logic(ordered_pairs, walls, vis)

            if self._abort.is_set():
                self.update_status("aborted.")
                return

            if not paths:
                self.update_status("no solution found.")
                sfx("error")
                return

            self.update_status("path trace analysis: animating...")
            vis.animate_solved_paths(paths, self._abort)

            if self._abort.is_set():
                self.update_status("aborted.")
                return

            self.update_status("path trace analysis: executing...")
            for path_idx, path in enumerate(paths):
                if self._abort.is_set():
                    break
                vis.simulate_drag_visual(path_idx, path, self._sleep,
                                         self._abort)

            if self._abort.is_set():
                self.update_status("aborted.")
                return

            sfx("done")
            self.update_status("trace complete.")
            time.sleep(0.67)
            self.update_status("ready.")

        except Exception:
            import traceback
            traceback.print_exc()
            self.update_status("error occurred.")
            sfx("error")
        finally:
            self.is_solving = False
            if self._visualizer:
                try:
                    self.root.after(0, self._visualizer.close)
                except Exception:
                    pass
                self._visualizer = None

    def execute_solve(self):
        try:
            runs = 4 if self.repeat_full.get() else 1
            for i in range(runs):
                if self._abort.is_set():
                    break
                if runs > 1:
                    self.update_status(f"solving... pass {i+1}/{runs}")
                t_start = time.time()
                success = self.run_solve_routine()
                elapsed = time.time() - t_start
                if self._abort.is_set():
                    break
                if not success:
                    self.update_status(f"failed on pass {i+1}. check console.")
                    sfx("error")
                    return
                if elapsed < SAFE_SOLVE_TIME:
                    time.sleep(SAFE_SOLVE_TIME - elapsed)
                if i < runs - 1:
                    self._sleep(0.04)

            if self._abort.is_set():
                self.update_status("aborted.")
            else:
                self.update_status("done. press f3 for next.")
                sfx("done")
        except Exception:
            import traceback
            traceback.print_exc()
            self.update_status("error occurred.")
            sfx("error")
        finally:
            self.is_solving = False
            if self._visualizer:
                try:
                    self.root.after(0, self._visualizer.close)
                except Exception:
                    pass
                self._visualizer = None

    def color_distance(self, c1, c2):
        return math.sqrt(sum((a - b)**2 for a, b in zip(c1, c2)))

    def sample_cell_color(self, screen, cx, cy, step_x, step_y):
        width, height = screen.size
        o1 = int(min(step_x, step_y) * 0.30)
        o2 = int(min(step_x, step_y) * 0.45)
        pts = [
            (max(0, cx - o1), cy),
            (min(width - 1, cx + o1), cy),
            (cx, max(0, cy - o1)),
            (cx, min(height - 1, cy + o1)),
            (max(0, cx - o2), cy),
            (min(width - 1, cx + o2), cy),
            (cx, max(0, cy - o2)),
            (cx, min(height - 1, cy + o2)),
        ]
        best_color, best_sat = None, 0
        for sx, sy in pts:
            r, g, b = screen.getpixel((sx, sy))
            if r < 40 and g < 40 and b < 40: continue
            if r > 220 and g > 220 and b > 220: continue
            sat = max(r, g, b) - min(r, g, b)
            if sat > 20 and sat > best_sat:
                best_sat = sat
                best_color = (r, g, b)
        return best_color

    def detect_grid(self, screen, bbox, step_x, step_y):
        name_to_cells = {}
        hitpoints = {}
        for row in range(GRID):
            for col in range(GRID):
                cx = int((col * step_x) + (step_x / 2))
                cy = int((row * step_y) + (step_y / 2))
                hitpoints[(row, col)] = (bbox[0] + cx, bbox[1] + cy)
                color = self.sample_cell_color(screen, cx, cy, step_x, step_y)
                if color:
                    name = nearest_preset_name(color)
                    name_to_cells.setdefault(name, []).append((row, col))
        pairs, walls = [], set()
        for name, cells in name_to_cells.items():
            if len(cells) == 2:
                pairs.append(cells)
            else:
                walls.update(cells)
        return pairs, walls, hitpoints

    def run_solve_routine(self):
        bbox = (self.top_left[0], self.top_left[1], self.bottom_right[0],
                self.bottom_right[1])
        screen = ImageGrab.grab(bbox=bbox)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        step_x = width / 6.0
        step_y = height / 6.0

        pairs, walls, hitpoints = self.detect_grid(screen, bbox, step_x,
                                                   step_y)
        self.cell_hitpoints = hitpoints

        print(f"detected {len(pairs)} pairs, {len(walls)} walls")
        for p in pairs:
            print(f"  pair: {p}")

        if not pairs:
            return False

        ordered_pairs = order_pairs(pairs, walls)

        name_to_cells_map = {}
        for row in range(GRID):
            for col in range(GRID):
                cx = int((col * step_x) + (step_x / 2))
                cy = int((row * step_y) + (step_y / 2))
                color = self.sample_cell_color(screen, cx, cy, step_x, step_y)
                if color:
                    name = nearest_preset_name(color)
                    name_to_cells_map.setdefault(name, []).append((row, col))

        pair_color_map = {}
        for idx, pair in enumerate(ordered_pairs):
            pair_set = set(map(tuple, pair))
            for name, cells in name_to_cells_map.items():
                if len(cells) == 2 and set(map(tuple, cells)) == pair_set:
                    pair_color_map[idx] = name
                    break
            if idx not in pair_color_map:
                pair_color_map[idx] = "white"

        vis = None
        if self.visualize_on.get():
            vis = SolverVisualizer(self.root, bbox, ordered_pairs, walls,
                                   pair_color_map, self._abort)
            self._visualizer = vis

        self.dfs_iterations = 0
        paths = self.solve_grid_logic(ordered_pairs, walls, vis)

        if self._abort.is_set():
            if vis:
                self.root.after(0, vis.close)
                self._visualizer = None
            force_release()
            return False

        if paths:
            if vis:
                self.update_status("animating solution...")
                vis.animate_solved_paths(paths, self._abort)
                if self._abort.is_set():
                    self.root.after(0, vis.close)
                    self._visualizer = None
                    force_release()
                    return False
                time.sleep(0.3)

            for path_idx, path in enumerate(paths):
                if self._abort.is_set():
                    force_release()
                    break
                if vis:
                    vis.highlight_dragging(path_idx, path)
                self.drag_path(path, bbox, step_x, step_y, vis, path_idx)
                if vis:
                    vis.clear_drag_highlight()

            if self._abort.is_set():
                if vis:
                    self.root.after(0, vis.close)
                    self._visualizer = None
                force_release()
                return False

            self._sleep(0.15)
            screen2 = ImageGrab.grab(bbox=bbox)
            pairs2, _, _ = self.detect_grid(screen2, bbox, step_x, step_y)
            missed = []
            solved_sets = [set(map(tuple, p)) for p in ordered_pairs]
            for p2 in pairs2:
                p2_set = set(map(tuple, p2))
                for orig_idx, orig_set in enumerate(solved_sets):
                    if p2_set == orig_set:
                        missed.append((orig_idx, paths[orig_idx]))
                        break

            if missed:
                print(
                    f"retry: {len(missed)} pair(s) did not register, redragging."
                )
                self.update_status(f"retrying {len(missed)} missed pair(s)...")
                for orig_idx, path in missed:
                    if self._abort.is_set():
                        force_release()
                        break
                    if vis:
                        vis.highlight_dragging(orig_idx, path)
                    self.drag_path(path, bbox, step_x, step_y, vis, orig_idx)
                    if vis:
                        vis.clear_drag_highlight()

            if vis:
                self.root.after(0, vis.close)
                self._visualizer = None
            return not self._abort.is_set()

        if vis:
            self.root.after(0, vis.close)
            self._visualizer = None
        return False

    def solve_grid_logic(self, pairs, walls, vis=None):
        EXPLORE_EVERY = 80

        def solve_recursive(pair_idx, current_path, occupied_set):
            self.dfs_iterations += 1
            if self._abort.is_set():
                return None
            if self.dfs_iterations > 2000000:
                return None
            if pair_idx >= len(pairs):
                return []

            start_node = tuple(pairs[pair_idx][0])
            end_node = tuple(pairs[pair_idx][1])
            if not current_path:
                current_path = [start_node]
            curr = current_path[-1]

            if curr == end_node:
                if not all_pairs_reachable(pairs, pair_idx + 1, occupied_set):
                    return None
                result = solve_recursive(pair_idx + 1, [], occupied_set)
                return ([list(current_path)] +
                        result) if result is not None else None

            if vis and self.dfs_iterations % EXPLORE_EVERY == 0:
                try:
                    vis.draw_explore_step(pair_idx, current_path,
                                          self.dfs_iterations)
                    vis.canvas.update()
                except Exception:
                    pass

            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = curr[0] + dr, curr[1] + dc
                if not (0 <= nr < GRID and 0 <= nc < GRID):
                    continue
                nb = (nr, nc)
                if nb != end_node and nb in occupied_set:
                    continue
                test_occ = occupied_set | {nb}
                if not all_pairs_reachable(pairs, pair_idx + 1, test_occ):
                    continue
                dist = bfs_distance(nb, end_node, test_occ - {end_node})
                free_n = sum(
                    1 for ddr, ddc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= nb[0] + ddr < GRID and 0 <= nb[1] +
                    ddc < GRID and (nb[0] + ddr, nb[1] + ddc) not in test_occ)
                neighbors.append((nb, free_n, dist))

            neighbors.sort(key=lambda x: (x[1], x[2]))

            for next_node, _, _ in neighbors:
                occupied_set.add(next_node)
                res = solve_recursive(pair_idx, current_path + [next_node],
                                      occupied_set)
                if res is not None:
                    return res
                occupied_set.remove(next_node)

            return None

        initial_occupied = set(map(tuple, walls))
        for p in pairs:
            initial_occupied.add(tuple(p[0]))
            initial_occupied.add(tuple(p[1]))

        return solve_recursive(0, [], initial_occupied)

    def cell_center(self, row, col, bbox, step_x, step_y):
        return (
            bbox[0] + int((col * step_x) + (step_x / 2)),
            bbox[1] + int((row * step_y) + (step_y / 2)),
        )

    def drag_path(self, path, bbox, step_x, step_y, vis=None, path_idx=0):
        if not path or len(path) < 2:
            return

        force_release()
        self._sleep(0.02)
        if self._abort.is_set():
            return

        if path[0] in self.cell_hitpoints:
            sx, sy = self.cell_hitpoints[path[0]]
        else:
            sx, sy = self.cell_center(path[0][0], path[0][1], bbox, step_x,
                                      step_y)

        self.move_to(sx, sy)
        self._sleep(0.02)
        if self._abort.is_set():
            return
        self.btn_down()
        self._sleep(0.02)

        if vis:
            vis.highlight_dragging(path_idx, path)

        curr_x, curr_y = sx, sy
        last_i = len(path) - 1
        for i in range(1, len(path)):
            if self._abort.is_set():
                self.btn_up()
                force_release()
                return
            r, c = path[i]
            is_last = (i == last_i)
            if is_last and (r, c) in self.cell_hitpoints:
                tx, ty = self.cell_hitpoints[(r, c)]
            else:
                tx, ty = self.cell_center(r, c, bbox, step_x, step_y)

            steps = 3
            for step in range(1, steps + 1):
                if self._abort.is_set():
                    self.btn_up()
                    force_release()
                    return
                t = step / float(steps)
                ix = int(curr_x + (tx - curr_x) * t)
                iy = int(curr_y + (ty - curr_y) * t)
                self.move_to(ix, iy)
                self._sleep(0.01)

            if vis:
                if is_last:
                    sfx("connect")
                else:
                    sfx("step")

            curr_x, curr_y = tx, ty
            self._sleep(0.01)

        self._sleep(0.01)
        self.btn_up()
        self._sleep(0.02)


if __name__ == "__main__":
    root = tk.Tk()
    app = ForsakenSolverTool(root)
    root.mainloop()
