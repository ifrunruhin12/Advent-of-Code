import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt, QTimer, QPoint


class CircularLock(QWidget):
    def __init__(self, instructions):
        super().__init__()
        self.setWindowTitle("Circular Lock Visualizer")
        self.resize(500, 600)

        self.instructions = instructions
        self.current_index = 0
        self.position = 50

        self.zero_crossings = 0
        self.zero_stops_live = 0

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)

        # UI buttons
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start)

        self.step_btn = QPushButton("Step")
        self.step_btn.clicked.connect(self.next_step)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)

        # Labels
        self.step_label = QLabel("Instruction: -")
        self.cross_label = QLabel("Zero Crossings: 0")
        self.stop_label = QLabel("Stops at 0 (Part 1): 0")

        # Layout
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.start_btn)
        h_layout.addWidget(self.step_btn)
        h_layout.addWidget(self.reset_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.step_label)
        layout.addWidget(self.cross_label)
        layout.addWidget(self.stop_label)
        layout.addLayout(h_layout)
        self.setLayout(layout)

    def start(self):
        self.timer.start(500)

    def reset(self):
        self.timer.stop()
        self.current_index = 0
        self.position = 50
        self.zero_crossings = 0
        self.zero_stops_live = 0

        self.step_label.setText("Instruction: -")
        self.cross_label.setText("Zero Crossings: 0")
        self.stop_label.setText("Stops at 0 (Part 1): 0")

        self.update()

    def next_step(self):
        if self.current_index >= len(self.instructions):
            self.timer.stop()
            return

        instr = self.instructions[self.current_index]
        direction = instr[0]
        steps = int(instr[1:])

        self.step_label.setText(f"Instruction: {instr}")

        full_loops, move_steps = divmod(steps, 100)
        self.zero_crossings += full_loops

        old_pos = self.position

        if direction == "R":
            if old_pos >= 100 - move_steps:
                self.zero_crossings += 1
            new_pos = (old_pos + move_steps) % 100
        else:
            if old_pos <= move_steps and old_pos != 0:
                self.zero_crossings += 1
            new_pos = (old_pos - move_steps) % 100

        self.position = new_pos

        if self.position == 0:
            self.zero_stops_live += 1

        # Update labels
        self.cross_label.setText(f"Zero Crossings: {self.zero_crossings}")
        self.stop_label.setText(f"Stops at 0 (Part 1): {self.zero_stops_live}")

        self.current_index += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2 + 50)
        radius = 180

        # Draw circle
        painter.setPen(QPen(Qt.GlobalColor.black, 3))
        painter.drawEllipse(center, radius, radius)

        # Draw numbers
        for i in range(0, 100, 10):
            angle_deg = (i / 100) * 360 - 90
            rad = math.radians(angle_deg)
            x = center.x() + (radius + 15) * math.cos(rad)
            y = center.y() + (radius + 15) * math.sin(rad)
            painter.drawText(int(x - 10), int(y + 5), str(i))

        # Fixed blue "zero" indicator
        painter.setPen(QPen(Qt.GlobalColor.blue, 6))
        zero_angle = -90
        zx = center.x() + radius * math.cos(math.radians(zero_angle))
        zy = center.y() + radius * math.sin(math.radians(zero_angle))
        painter.drawLine(center.x(), center.y(), int(zx), int(zy))

        # Red needle = current position
        angle_deg = (self.position / 100) * 360 - 90
        rad = math.radians(angle_deg)
        x = center.x() + radius * math.cos(rad)
        y = center.y() + radius * math.sin(rad)

        painter.setPen(QPen(Qt.GlobalColor.red, 5))
        painter.drawLine(center.x(), center.y(), int(x), int(y))


def load_instructions(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    instructions = load_instructions("input.txt")
    app = QApplication(sys.argv)
    window = CircularLock(instructions)
    window.show()
    sys.exit(app.exec())

