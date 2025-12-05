import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QPainter, QPen, QColor
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

        # Timer for step animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)

        # UI elements
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start)
        self.step_btn = QPushButton("Step")
        self.step_btn.clicked.connect(self.next_step)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)

        self.step_label = QLabel("Instruction: -")
        self.cross_label = QLabel("Zero Crossings: 0")

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.start_btn)
        h_layout.addWidget(self.step_btn)
        h_layout.addWidget(self.reset_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.step_label)
        layout.addWidget(self.cross_label)
        layout.addLayout(h_layout)
        self.setLayout(layout)

    def start(self):
        self.timer.start(500)  # Half-second per step

    def reset(self):
        self.timer.stop()
        self.current_index = 0
        self.position = 50
        self.zero_crossings = 0
        self.step_label.setText("Instruction: -")
        self.cross_label.setText("Zero Crossings: 0")
        self.update()

    def next_step(self):
        if self.current_index >= len(self.instructions):
            self.timer.stop()
            return

        instr = self.instructions[self.current_index]
        direction = instr[0]
        steps = int(instr[1:])

        loops, steps = divmod(steps, 100)
        self.zero_crossings += loops

        # Check zero crossing for partial steps
        if direction == 'R':
            if self.position >= 100 - steps:
                self.zero_crossings += 1
            self.position = (self.position + steps) % 100
        else:
            if self.position <= steps and self.position != 0:
                self.zero_crossings += 1
            self.position = (self.position - steps) % 100

        self.cross_label.setText(f"Zero Crossings: {self.zero_crossings}")
        self.step_label.setText(f"Instruction: {instr}")
        self.current_index += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = QPoint(self.width() // 2, self.height() // 2 + 50)
        radius = 180

        # Draw the main dial
        painter.setPen(QPen(Qt.GlobalColor.black, 3))
        painter.drawEllipse(center, radius, radius)

        # Draw numbers around the dial
        for i in range(0, 100, 10):
            angle = (i / 100) * 360 - 90
            rad = math.radians(angle)
            x = center.x() + (radius + 15) * math.cos(rad)
            y = center.y() + (radius + 15) * math.sin(rad)
            painter.drawText(int(x - 10), int(y + 5), str(i))
        # Draw zero point
        zero_angle = -90
        zx = center.x() + radius * math.cos(math.radians(zero_angle))
        zy = center.y() + radius * math.sin(math.radians(zero_angle))
        painter.setPen(QPen(Qt.GlobalColor.blue, 8))
        painter.drawLine(center.x(), center.y(), int(x), int(y))
        # Draw needle
        angle = (self.position / 100) * 360 - 90
        rad = math.radians(angle)
        x = center.x() + radius * math.cos(rad)
        y = center.y() + radius * math.sin(rad)

        painter.setPen(QPen(Qt.GlobalColor.red, 5))
        painter.drawLine(center.x(), center.y(), int(x), int(y))


def load_instructions(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f]


if __name__ == "__main__":
    instructions = load_instructions("input.txt")
    app = QApplication(sys.argv)
    window = CircularLock(instructions)
    window.show()
    sys.exit(app.exec())

