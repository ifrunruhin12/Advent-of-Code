import sys
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
import random

CELL_SIZE = 25

def random_color():
    # generate a random color
    return QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

class QuantumVisualizer(QWidget):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.R = len(grid)
        self.C = len(grid[0])

        self.initUI()
        self.reset_simulation()

    def initUI(self):
        layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.cells = []

        for r in range(self.R):
            row_cells = []
            for c in range(self.C):
                lbl = QLabel(self.grid[r][c])
                lbl.setFixedSize(CELL_SIZE, CELL_SIZE)
                lbl.setStyleSheet("border:1px solid gray; font-weight:bold; font-size:14px;")
                self.grid_layout.addWidget(lbl, r, c)
                row_cells.append(lbl)
            self.cells.append(row_cells)
        layout.addLayout(self.grid_layout)

        # controls
        control_layout = QHBoxLayout()
        self.mode_box = QComboBox()
        self.mode_box.addItems(["Part 1: Beam Splits", "Part 2: Quantum Timelines"])
        control_layout.addWidget(self.mode_box)

        self.play_btn = QPushButton("Play / Pause")
        self.play_btn.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_btn)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_btn)

        self.counter_lbl = QLabel("Splits / Timelines: 0")
        control_layout.addWidget(self.counter_lbl)

        layout.addLayout(control_layout)
        self.setLayout(layout)
        self.setWindowTitle("Quantum Tachyon Visualizer")
        self.show()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.step)

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(150)  # milliseconds per step

    def reset_simulation(self):
        # Reset grid
        for r in range(self.R):
            for c in range(self.C):
                self.cells[r][c].setText(self.grid[r][c])
                self.cells[r][c].setStyleSheet("border:1px solid gray; font-weight:bold; font-size:14px;")

        # find S
        self.start_row = self.start_col = None
        for r in range(self.R):
            for c in range(self.C):
                if self.grid[r][c] == 'S':
                    self.start_row, self.start_col = r, c
                    break
            if self.start_row is not None:
                break

        self.timestep = 0
        self.mode = self.mode_box.currentIndex()
        self.counter = 0
        self.update_counter_label()

        # Simulation states
        self.beams = [(self.start_row + 1, self.start_col, QColor(0, 255, 255))]  # Part 1: single color, Part 2: timeline color
        self.used_splitters = set()
        self.memo = {}

    def update_counter_label(self):
        if self.mode == 0:
            self.counter_lbl.setText(f"Splits: {self.counter}")
        else:
            self.counter_lbl.setText(f"Timelines: {self.counter}")

    # -------- Part 1: Beam Splits Step -----------
    def step_part1(self):
        new_beams = []
        for r, c, color in self.beams:
            if r >= self.R:
                continue
            cell = self.grid[r][c]
            if cell == '^':
                if (r, c) not in self.used_splitters:
                    self.counter += 1
                    self.used_splitters.add((r, c))
                if c - 1 >= 0:
                    new_beams.append((r, c-1, color))
                if c + 1 < self.C:
                    new_beams.append((r, c+1, color))
                self.cells[r][c].setStyleSheet(f"background-color: yellow; border:1px solid gray;")
            else:
                if r + 1 < self.R:
                    new_beams.append((r+1, c, color))
                self.cells[r][c].setStyleSheet(f"background-color: {color.name()}; border:1px solid gray;")
        self.beams = new_beams
        self.update_counter_label()

    # -------- Part 2: Quantum Timelines Step -----------
    def step_part2(self):
        if self.timestep == 0:
            # initialize all active paths
            self.active_paths = [(self.start_row + 1, self.start_col, random_color())]
            self.counter = 0

        new_paths = []
        for r, c, color in self.active_paths:
            if r >= self.R:
                continue
            cell = self.grid[r][c]
            if cell == '^':
                # split left and right, new color for each timeline
                if c-1 >= 0:
                    new_paths.append((r, c-1, color))
                if c+1 < self.C:
                    new_paths.append((r, c+1, color))
                self.cells[r][c].setStyleSheet("background-color: yellow; border:1px solid gray;")
                self.counter += 1
            else:
                if r + 1 < self.R:
                    new_paths.append((r+1, c, color))
                self.cells[r][c].setStyleSheet(f"background-color: {color.name()}; border:1px solid gray;")
        self.active_paths = new_paths
        self.update_counter_label()
        if not self.active_paths:
            self.timer.stop()  # stop when all paths finish
        self.timestep += 1

    # -------- Step Dispatcher -----------
    def step(self):
        self.mode = self.mode_box.currentIndex()
        if self.mode == 0:
            self.step_part1()
        else:
            self.step_part2()


# --------- Main ---------
def read_input(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    input_file = "example_in.txt"
    grid = read_input(input_file)

    app = QApplication(sys.argv)
    viz = QuantumVisualizer(grid)
    sys.exit(app.exec())
