import tkinter as tk
from tkinter import ttk
import keyboard
import pyautogui
import ctypes
from PIL import ImageGrab
import threading
import time
import math

import interception

COLOR_MATCH_THRESHOLD = 40


class ForsakenSolverTool:
    def __init__(self, root):
        self.root = root
        self.root.title("forsaken auto gen")
        self.root.geometry("260x310")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.top_left       = None
        self.bottom_right   = None
        self.is_solving     = False
        self.cell_hitpoints = {}
        self.repeat_full    = tk.BooleanVar(value=False)

        # ── title bar area ───────────────────────────────────────────────────
        title_frame = tk.Frame(root, bg="#2b2b2b", height=32)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame, text="FORSAKEN AUTO GEN",
            bg="#2b2b2b", fg="#ffffff",
            font=("Courier New", 9, "bold")
        ).pack(side="left", padx=8, pady=6)

        # ── status ───────────────────────────────────────────────────────────
        status_frame = tk.Frame(root, bg="#e8e8e8", relief="sunken", bd=1)
        status_frame.pack(fill="x", padx=6, pady=(6, 2))
        self.status_lbl = tk.Label(
            status_frame, text="ready.",
            bg="#e8e8e8", fg="#333333",
            font=("Courier New", 8),
            anchor="w", padx=4, pady=3
        )
        self.status_lbl.pack(fill="x")

        # ── divider ──────────────────────────────────────────────────────────
        tk.Frame(root, bg="#cccccc", height=1).pack(fill="x", padx=6, pady=4)

        # ── hotkey list ──────────────────────────────────────────────────────
        hk_frame = tk.Frame(root, bg="#f0f0f0")
        hk_frame.pack(fill="x", padx=10)

        hotkeys = [
            ("F1", "top left capture"),
            ("F2", "bottom right capture"),
            ("F3", "start"),
            ("F4", "test movement"),
            ("F5", "debug: print colors"),
        ]
        for key, desc in hotkeys:
            row_f = tk.Frame(hk_frame, bg="#f0f0f0")
            row_f.pack(fill="x", pady=1)
            tk.Label(
                row_f, text=key,
                bg="#dddddd", fg="#000000",
                font=("Courier New", 8, "bold"),
                width=4, relief="groove", bd=1
            ).pack(side="left")
            tk.Label(
                row_f, text=f"  {desc}",
                bg="#f0f0f0", fg="#444444",
                font=("Courier New", 8),
                anchor="w"
            ).pack(side="left")

        # ── divider ──────────────────────────────────────────────────────────
        tk.Frame(root, bg="#cccccc", height=1).pack(fill="x", padx=6, pady=8)

        # ── repeat toggle ────────────────────────────────────────────────────
        toggle_frame = tk.Frame(root, bg="#f0f0f0", relief="ridge", bd=1)
        toggle_frame.pack(fill="x", padx=6)

        cb_row = tk.Frame(toggle_frame, bg="#f0f0f0")
        cb_row.pack(fill="x", padx=6, pady=(5, 2))
        self.repeat_cb = tk.Checkbutton(
            cb_row,
            text="fully complete gen (x4)",
            variable=self.repeat_full,
            bg="#f0f0f0", fg="#000000",
            font=("Courier New", 8, "bold"),
            activebackground="#f0f0f0",
            selectcolor="#ffffff",
        )
        self.repeat_cb.pack(side="left")

        tk.Label(
            toggle_frame,
            text="only enable if generator is 0%\nand not completely solved!",
            bg="#f0f0f0", fg="#888888",
            font=("Courier New", 7),
            justify="left"
        ).pack(anchor="w", padx=8, pady=(0, 5))

        # ── bottom bar ───────────────────────────────────────────────────────
        tk.Frame(root, bg="#cccccc", height=1).pack(fill="x", padx=6, pady=(8, 0))
        bottom = tk.Frame(root, bg="#e8e8e8")
        bottom.pack(fill="x")
        tk.Label(
            bottom, text="interception driver active",
            bg="#e8e8e8", fg="#999999",
            font=("Courier New", 7),
        ).pack(pady=3)

        threading.Thread(target=self.listen_hotkeys, daemon=True).start()

    def update_status(self, text, color="#333333"):
        self.status_lbl.config(text=text, fg=color)

    def listen_hotkeys(self):
        while True:
            if keyboard.is_pressed('f1'):
                self.top_left = pyautogui.position()
                self.update_status(f"top left set: {self.top_left}", "#0055cc")
                time.sleep(0.3)
            elif keyboard.is_pressed('f2'):
                if not self.top_left:
                    self.update_status("set top left first!", "#cc0000")
                else:
                    self.bottom_right = pyautogui.position()
                    self.update_status(f"grid locked. ready.", "#007700")
                time.sleep(0.3)
            elif keyboard.is_pressed('f4'):
                self.test_mouse()
                time.sleep(0.5)
            elif keyboard.is_pressed('f5'):
                self.debug_print_colors()
                time.sleep(0.5)
            elif keyboard.is_pressed('f3'):
                if self.top_left and self.bottom_right and not self.is_solving:
                    self.is_solving = True
                    self.update_status("solving...", "#0055cc")
                    threading.Thread(target=self.execute_solve, daemon=True).start()
            time.sleep(0.05)

    # ── interception wrappers ────────────────────────────────────────────────

    def move_to(self, x, y):
        interception.move_to(int(x), int(y))

    def btn_down(self):
        interception.mouse_down(button="left")

    def btn_up(self):
        interception.mouse_up(button="left")

    def force_release(self):
        try:
            interception.mouse_up(button="left")
        except Exception:
            pass
        time.sleep(0.03)

    def test_mouse(self):
        x, y = pyautogui.position()
        self.force_release()
        self.move_to(x, y)
        time.sleep(0.05)
        self.btn_down()
        time.sleep(0.05)
        for tx, ty in [(x+80, y), (x+80, y+80), (x, y+80), (x, y)]:
            self.move_to(tx, ty)
            time.sleep(0.04)
        self.btn_up()
        self.update_status("test done.", "#007700")

    # ── debug ────────────────────────────────────────────────────────────────

    def debug_print_colors(self):
        if not (self.top_left and self.bottom_right):
            self.update_status("set grid first!", "#cc0000")
            return
        bbox   = (self.top_left[0], self.top_left[1], self.bottom_right[0], self.bottom_right[1])
        screen = ImageGrab.grab(bbox=bbox)
        width  = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        step_x = width  / 6.0
        step_y = height / 6.0
        print("\n── debug color dump ──")
        for row in range(6):
            for col in range(6):
                cx = int((col * step_x) + (step_x / 2))
                cy = int((row * step_y) + (step_y / 2))
                r, g, b = screen.getpixel((cx, cy))
                sat = max(r,g,b) - min(r,g,b)
                print(f"  [{row},{col}] rgb=({r:3},{g:3},{b:3}) sat={sat}")
        print("─────────────────────\n")
        self.update_status("colors printed to console.", "#555555")

    # ── execute ──────────────────────────────────────────────────────────────

    def execute_solve(self):
        try:
            runs = 4 if self.repeat_full.get() else 1
            for i in range(runs):
                if runs > 1:
                    self.update_status(f"solving... pass {i+1}/{runs}", "#0055cc")
                success = self.run_solve_routine()
                if not success:
                    self.update_status(f"failed on pass {i+1}. check console.", "#cc0000")
                    return
                if i < runs - 1:
                    time.sleep(0.04)
            self.update_status("done. press f3 for next.", "#007700")
        except Exception as e:
            print(e)
            self.update_status("error occurred.", "#cc0000")
        finally:
            self.is_solving = False

    # ── color helpers ────────────────────────────────────────────────────────

    def color_distance(self, c1, c2):
        return math.sqrt(sum((a-b)**2 for a, b in zip(c1, c2)))

    def sample_cell_color(self, screen, cx, cy, step_x, step_y):
        width, height = screen.size
        offset = int(min(step_x, step_y) * 0.15)
        pts = [
            (cx, cy),
            (max(0, cx - offset), cy),
            (min(width-1, cx + offset), cy),
            (cx, max(0, cy - offset)),
            (cx, min(height-1, cy + offset)),
        ]
        best_color, best_sat = None, 0
        for sx, sy in pts:
            r, g, b = screen.getpixel((sx, sy))
            if r < 40 and g < 40 and b < 40: continue
            if r > 220 and g > 220 and b > 220: continue
            sat = max(r,g,b) - min(r,g,b)
            if sat > 20 and sat > best_sat:
                best_sat   = sat
                best_color = (r, g, b)
        return best_color

    # ── detection ────────────────────────────────────────────────────────────

    def detect_grid(self, screen, bbox, step_x, step_y):
        color_groups = {}
        hitpoints    = {}

        for row in range(6):
            for col in range(6):
                cx = int((col * step_x) + (step_x / 2))
                cy = int((row * step_y) + (step_y / 2))
                hitpoints[(row, col)] = (bbox[0] + cx, bbox[1] + cy)

                color = self.sample_cell_color(screen, cx, cy, step_x, step_y)
                if color:
                    matched = next(
                        (k for k in color_groups if self.color_distance(color, k) < COLOR_MATCH_THRESHOLD),
                        None
                    )
                    if not matched:
                        matched = color
                    color_groups.setdefault(matched, []).append((row, col))

        pairs, walls = [], set()
        for color, cells in color_groups.items():
            if len(cells) == 2:  pairs.append(cells)
            else:                walls.update(cells)

        return pairs, walls, hitpoints

    # ── solve routine ────────────────────────────────────────────────────────

    def run_solve_routine(self):
        bbox   = (self.top_left[0], self.top_left[1], self.bottom_right[0], self.bottom_right[1])
        screen = ImageGrab.grab(bbox=bbox)
        width  = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        step_x = width  / 6.0
        step_y = height / 6.0

        pairs, walls, hitpoints = self.detect_grid(screen, bbox, step_x, step_y)
        self.cell_hitpoints = hitpoints

        print(f"detected {len(pairs)} pairs, {len(walls)} walls")
        for p in pairs:
            print(f"  pair: {p}")

        if not pairs:
            return False

        pairs.sort(key=lambda p: abs(p[0][0]-p[1][0]) + abs(p[0][1]-p[1][1]))
        self.dfs_iterations = 0
        paths = self.solve_grid_logic(pairs, walls)

        if paths:
            for path in paths:
                self.drag_path(path, bbox, step_x, step_y)
            return True
        return False

    # ── solver ───────────────────────────────────────────────────────────────

    def solve_grid_logic(self, pairs, walls):
        def get_neighbors(r, c, target, occupied):
            candidates = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < 6 and 0 <= nc < 6:
                    if (nr,nc) not in occupied:
                        candidates.append(((nr,nc), abs(nr-target[0])+abs(nc-target[1])))
                    elif (nr,nc) == target:
                        candidates.insert(0, ((nr,nc), 0))
            candidates.sort(key=lambda x: x[1])
            return [x[0] for x in candidates]

        def solve_recursive(pair_idx, current_path, occupied_set):
            self.dfs_iterations += 1
            if self.dfs_iterations > 100000: return None
            if pair_idx >= len(pairs): return []
            start_node, end_node = pairs[pair_idx]
            if not current_path: current_path = [start_node]
            curr = current_path[-1]
            if curr == end_node:
                result = solve_recursive(pair_idx + 1, [], occupied_set)
                return ([list(current_path)] + result) if result is not None else None
            future_endpoints = {p[i] for i in range(2) for p in pairs[pair_idx+1:]}
            for next_node in get_neighbors(curr[0], curr[1], end_node, occupied_set):
                if next_node in future_endpoints and next_node != end_node: continue
                occupied_set.add(next_node)
                res = solve_recursive(pair_idx, current_path + [next_node], occupied_set)
                if res is not None: return res
                occupied_set.remove(next_node)
            return None

        initial_occupied = set(walls)
        for p in pairs: initial_occupied.update(p)
        return solve_recursive(0, [], initial_occupied)

    # ── drag ─────────────────────────────────────────────────────────────────

    def cell_center(self, row, col, bbox, step_x, step_y):
        return (
            bbox[0] + int((col * step_x) + (step_x / 2)),
            bbox[1] + int((row * step_y) + (step_y / 2)),
        )

    def drag_path(self, path, bbox, step_x, step_y):
        if not path or len(path) < 2:
            return

        self.force_release()
        time.sleep(0.03)

        sx, sy = self.cell_hitpoints.get(
            path[0],
            self.cell_center(path[0][0], path[0][1], bbox, step_x, step_y)
        )

        self.move_to(sx, sy)
        time.sleep(0.05)
        self.btn_down()
        time.sleep(0.05)

        for i in range(1, len(path)):
            r, c = path[i]
            if i == len(path) - 1:
                tx, ty = self.cell_hitpoints.get((r,c), self.cell_center(r, c, bbox, step_x, step_y))
            else:
                tx, ty = self.cell_center(r, c, bbox, step_x, step_y)
            self.move_to(tx, ty)
            time.sleep(0.04)

        self.btn_up()
        time.sleep(0.08)


if __name__ == "__main__":
    root = tk.Tk()
    app  = ForsakenSolverTool(root)
    root.mainloop()