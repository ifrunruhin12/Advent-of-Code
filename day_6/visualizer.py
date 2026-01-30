import sys
from enum import Enum

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor


# ===================== Parser Engine =====================

class Mode(Enum):
    PART1 = 1
    PART2 = 2


class State(Enum):
    SCAN = 1
    BLOCK = 2
    EXTRACT = 3
    REDUCE = 4
    DONE = 5


class ParserEngine:
    def __init__(self, lines, mode=Mode.PART2):
        self.lines = lines
        self.h = len(lines)
        self.w = max(len(l) for l in lines)
        self.mode = mode

        self.col = 0
        self.total = 0

        self.state = State.SCAN
        self.block_start = None
        self.block_end = None

        self.extract_targets = []
        self.nums = []
        self.op = None

        self.reduce_idx = 0
        self.current_result = None

    def is_space_col(self, c):
        for line in self.lines:
            if c < len(line) and line[c] != " ":
                return False
        return True

    def step(self):
        if self.state == State.DONE:
            return

        if self.state == State.SCAN:
            if self.col >= self.w:
                self.state = State.DONE
                return
            if self.is_space_col(self.col):
                self.col += 1
            else:
                self.block_start = self.col
                self.state = State.BLOCK

        elif self.state == State.BLOCK:
            if self.col < self.w and not self.is_space_col(self.col):
                self.col += 1
            else:
                self.block_end = self.col
                self.nums = []
                if self.mode == Mode.PART1:
                    self.extract_targets = list(range(self.h - 1))
                else:
                    self.extract_targets = list(
                        range(self.block_end - 1, self.block_start - 1, -1)
                    )
                self.state = State.EXTRACT

        elif self.state == State.EXTRACT:
            if not self.extract_targets:
                self.op = self.lines[-1][self.block_start:self.block_end].strip()
                self.current_result = self.nums[0]
                self.reduce_idx = 0
                self.state = State.REDUCE
                return

            t = self.extract_targets.pop(0)

            if self.mode == Mode.PART1:
                chunk = self.lines[t][self.block_start:self.block_end].strip()
                if chunk:
                    self.nums.append(int(chunk))
            else:
                digits = []
                for r in range(self.h - 1):
                    if t < len(self.lines[r]) and self.lines[r][t] != " ":
                        digits.append(self.lines[r][t])
                if digits:
                    self.nums.append(int("".join(digits)))

        elif self.state == State.REDUCE:
            if self.reduce_idx == len(self.nums) - 1:
                self.total += self.current_result
                self.col += 1
                self.state = State.SCAN
                return

            nxt = self.nums[self.reduce_idx + 1]
            self.current_result = (
                self.current_result + nxt
                if self.op == "+"
                else self.current_result * nxt
            )
            self.reduce_idx += 1


# ===================== UI =====================

class Visualizer(QWidget):
    def __init__(self, lines):
        super().__init__()
        self.engine = ParserEngine(lines, Mode.PART2)

        self.init_ui(lines)
        self.init_grid(lines)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

    def init_ui(self, lines):
        self.setWindowTitle("Cephalopod Math Visualizer v3")
        self.resize(1400, 500)

        root = QVBoxLayout()

        self.info = QLabel("State: SCAN")
        root.addWidget(self.info)

        self.table = QTableWidget(len(lines), self.engine.w)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table)

        controls = QHBoxLayout()

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)

        step_btn = QPushButton("⏭ Step")
        step_btn.clicked.connect(self.tick)
        controls.addWidget(step_btn)

        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setMinimum(50)
        self.speed.setMaximum(1000)
        self.speed.setValue(300)
        self.speed.valueChanged.connect(self.update_speed)
        controls.addWidget(QLabel("Speed"))
        controls.addWidget(self.speed)

        self.mode_btn = QPushButton("Mode: PART 2")
        self.mode_btn.clicked.connect(self.toggle_mode)
        controls.addWidget(self.mode_btn)

        root.addLayout(controls)
        self.setLayout(root)

    def init_grid(self, lines):
        for r in range(len(lines)):
            for c in range(self.engine.w):
                ch = lines[r][c] if c < len(lines[r]) else " "
                self.table.setItem(r, c, QTableWidgetItem(ch))

    def clear_colors(self):
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                self.table.item(r, c).setBackground(QColor("white"))

    def tick(self):
        self.engine.step()
        self.render()

    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_btn.setText("▶ Play")
        else:
            self.timer.start(self.speed.value())
            self.play_btn.setText("⏸ Pause")

    def update_speed(self):
        if self.timer.isActive():
            self.timer.start(self.speed.value())

    def toggle_mode(self):
        if self.engine.mode == Mode.PART2:
            self.engine = ParserEngine(self.engine.lines, Mode.PART1)
            self.mode_btn.setText("Mode: PART 1")
        else:
            self.engine = ParserEngine(self.engine.lines, Mode.PART2)
            self.mode_btn.setText("Mode: PART 2")

    def render(self):
        self.clear_colors()
        e = self.engine

        if e.col < e.w:
            for r in range(e.h):
                self.table.item(r, e.col).setBackground(QColor("#cce5ff"))

        if e.block_start is not None:
            for c in range(e.block_start, min(e.col, e.w)):
                for r in range(e.h):
                    self.table.item(r, c).setBackground(QColor("#d4edda"))

        self.info.setText(
            f"State={e.state.name} | Col={e.col} | Block={e.block_start}:{e.block_end} "
            f"| nums={e.nums} | current={e.current_result} | total={e.total}"
        )


# ===================== Run =====================

def load_input(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lines = load_input("input.txt")
    w = Visualizer(lines)
    w.show()
    sys.exit(app.exec())

