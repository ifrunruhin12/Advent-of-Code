import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QSlider, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class Day3Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Day 3 — Digit Sequence Visualizer")
        self.resize(900, 700)

        # State
        self.current_part = 1
        self.lines = []
        self.current_line_idx = 0
        self.current_step = 0
        self.is_playing = False
        self.speed = 500

        # Part 1 state
        self.current_string = ""
        self.current_pos = -1
        self.max_right = -1
        self.best = -1
        
        # Part 2 state
        self.stack = []
        self.remove_count = 0
        self.total_to_remove = 0

        self.line_results = []
        self.total_sum = 0

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        self._build_ui()
        self._update_ui()

    def _build_ui(self):
        main = QVBoxLayout()
        
        title = QLabel("<h2>Day 3 — Digit Sequence Visualizer</h2>")
        main.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Part buttons
        parts = QHBoxLayout()
        self.part1_btn = QPushButton("Part 1: Highest Two-Digit")
        self.part1_btn.clicked.connect(self._set_part1)
        self.part2_btn = QPushButton("Part 2: Max Joltage")
        self.part2_btn.clicked.connect(self._set_part2)
        parts.addWidget(self.part1_btn)
        parts.addWidget(self.part2_btn)
        main.addLayout(parts)

        # Description
        self.desc = QLabel("")
        self.desc.setWordWrap(True)
        main.addWidget(self.desc)

        # Input area
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Input (one number per line):"))
        self.load_btn = QPushButton("Load from File")
        self.load_btn.clicked.connect(self._load_file)
        input_row.addWidget(self.load_btn)
        main.addLayout(input_row)

        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Enter numbers, one per line (or load from file)")
        self.input_area.setMaximumHeight(100)
        main.addWidget(self.input_area)

        # Control buttons
        ctrl = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_processing)
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        self.step_btn = QPushButton("→ Step")
        self.step_btn.clicked.connect(self.step_forward)
        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.clicked.connect(self.reset)
        
        ctrl.addWidget(self.start_btn)
        ctrl.addWidget(self.play_btn)
        ctrl.addWidget(self.step_btn)
        ctrl.addWidget(self.reset_btn)

        # Speed slider
        ctrl.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(100, 1000)
        self.speed_slider.setSingleStep(50)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.valueChanged.connect(self._on_speed_change)
        ctrl.addWidget(self.speed_slider)
        self.speed_label = QLabel(f"{self.speed} ms")
        ctrl.addWidget(self.speed_label)
        main.addLayout(ctrl)

        # Current line info
        self.line_label = QLabel("Line: -")
        main.addWidget(self.line_label)

        # Visualization area
        self.visual_box = QTextEdit()
        self.visual_box.setReadOnly(True)
        self.visual_box.setFont(QFont("Courier", 11))
        main.addWidget(self.visual_box)

        # Results
        results = QHBoxLayout()
        results.addWidget(QLabel("Current Result:"))
        self.current_result_label = QLabel("-")
        self.current_result_label.setStyleSheet("color: blue; font-weight: bold; font-size: 14pt;")
        results.addWidget(self.current_result_label)
        results.addStretch()
        results.addWidget(QLabel("Total Sum:"))
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("color: green; font-weight: bold; font-size: 14pt;")
        results.addWidget(self.total_label)
        main.addLayout(results)

        # Results list
        main.addWidget(QLabel("Results per line:"))
        self.results_list = QTextEdit()
        self.results_list.setReadOnly(True)
        self.results_list.setMaximumHeight(100)
        main.addWidget(self.results_list)

        self.setLayout(main)

    def _set_part1(self):
        self.current_part = 1
        self.reset()
        self._update_ui()

    def _set_part2(self):
        self.current_part = 2
        self.reset()
        self._update_ui()

    def _on_speed_change(self, val):
        self.speed = int(val)
        self.speed_label.setText(f"{self.speed} ms")
        if self.timer.isActive():
            self.timer.setInterval(self.speed)

    def _load_file(self):
        try:
            with open("example_in.txt", "r") as f:
                content = f.read()
                self.input_area.setPlainText(content)
        except FileNotFoundError:
            QMessageBox.warning(self, "File Error", "Could not find day_3/input.txt")

    def start_processing(self):
        text = self.input_area.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Input Error", "Please enter some numbers")
            return

        self.lines = [line.strip() for line in text.split('\n') if line.strip()]
        self.current_line_idx = 0
        self.current_step = 0
        self.line_results = []
        self.total_sum = 0
        
        if self.lines:
            self._start_new_line()
        
        self._update_ui()

    def _start_new_line(self):
        if self.current_line_idx >= len(self.lines):
            return

        self.current_string = self.lines[self.current_line_idx]
        
        if self.current_part == 1:
            # Part 1: Start from the end
            self.current_pos = len(self.current_string) - 1
            self.max_right = -1
            self.best = -1
        else:
            # Part 2: Start from the beginning
            self.current_pos = 0
            self.stack = []
            self.total_to_remove = len(self.current_string) - 12
            self.remove_count = 0

    def step_forward(self):
        if not self.lines or self.current_line_idx >= len(self.lines):
            return

        if self.current_part == 1:
            self._step_part1()
        else:
            self._step_part2()
        
        self._update_ui()

    def _step_part1(self):
        if self.current_pos < 0:
            # Finished current line, move to next
            self.line_results.append(self.best)
            self.total_sum += self.best
            self.current_line_idx += 1
            
            if self.current_line_idx < len(self.lines):
                self._start_new_line()
            else:
                self.is_playing = False
                self.timer.stop()
            return

        d = int(self.current_string[self.current_pos])
        
        if self.max_right != -1:
            self.best = max(self.best, d * 10 + self.max_right)
        
        self.max_right = max(self.max_right, d)
        self.current_pos -= 1

    def _step_part2(self):
        if self.current_pos >= len(self.current_string):
            # Finished processing, extract result
            result_str = "".join(self.stack[:12])
            result = int(result_str) if result_str else 0
            self.line_results.append(result)
            self.total_sum += result
            self.current_line_idx += 1
            
            if self.current_line_idx < len(self.lines):
                self._start_new_line()
            else:
                self.is_playing = False
                self.timer.stop()
            return

        ch = self.current_string[self.current_pos]
        
        # Remove smaller digits from stack if we can
        while self.stack and self.remove_count < self.total_to_remove and self.stack[-1] < ch:
            self.stack.pop()
            self.remove_count += 1
        
        self.stack.append(ch)
        self.current_pos += 1

    def toggle_play(self):
        if not self.lines:
            return
            
        if not self.is_playing:
            self.is_playing = True
            self.play_btn.setText("⏸ Pause")
            self.timer.start(self.speed)
        else:
            self.is_playing = False
            self.play_btn.setText("▶ Play")
            self.timer.stop()

    def _tick(self):
        self.step_forward()
        if self.current_line_idx >= len(self.lines):
            self.is_playing = False
            self.timer.stop()
            self.play_btn.setText("▶ Play")

    def reset(self):
        self.timer.stop()
        self.is_playing = False
        self.lines = []
        self.current_line_idx = 0
        self.current_step = 0
        self.line_results = []
        self.total_sum = 0
        self.play_btn.setText("▶ Play")
        self._update_ui()

    def _update_ui(self):
        # Update part buttons
        if self.current_part == 1:
            self.part1_btn.setStyleSheet("background:#1976d2; color:white;")
            self.part2_btn.setStyleSheet("")
            self.desc.setText("Part 1: Find the highest two-digit number by pairing each digit with the maximum digit to its right.")
        else:
            self.part2_btn.setStyleSheet("background:#6a1b9a; color:white;")
            self.part1_btn.setStyleSheet("")
            self.desc.setText("Part 2: Remove digits to keep 12 digits that form the maximum possible number (greedy algorithm).")

        # Update line label
        if self.lines and self.current_line_idx < len(self.lines):
            self.line_label.setText(f"Line: {self.current_line_idx + 1} / {len(self.lines)}")
        else:
            self.line_label.setText("Line: -")

        # Update visualization
        self.visual_box.setPlainText(self._generate_visualization())

        # Update current result
        if self.current_part == 1 and self.best >= 0:
            self.current_result_label.setText(str(self.best))
        elif self.current_part == 2 and self.stack:
            result_str = "".join(self.stack[:12])
            self.current_result_label.setText(result_str if result_str else "-")
        else:
            self.current_result_label.setText("-")

        # Update total
        self.total_label.setText(str(self.total_sum))

        # Update results list
        results_text = "\n".join(f"Line {i+1}: {r}" for i, r in enumerate(self.line_results))
        self.results_list.setPlainText(results_text)

        # Enable/disable buttons
        has_lines = bool(self.lines)
        not_finished = self.current_line_idx < len(self.lines)
        self.play_btn.setEnabled(has_lines and not_finished)
        self.step_btn.setEnabled(has_lines and not_finished and not self.is_playing)

    def _generate_visualization(self):
        if not self.lines or self.current_line_idx >= len(self.lines):
            return "No data to visualize"

        s = self.current_string
        viz = []

        if self.current_part == 1:
            # Part 1 visualization
            viz.append("String: " + s)
            viz.append("")
            
            if self.current_pos >= 0:
                # Show current position
                pointer = " " * 8 + " " * self.current_pos + "^"
                viz.append(pointer)
                viz.append("")
                viz.append(f"Current digit: {s[self.current_pos]}")
                viz.append(f"Max right: {self.max_right if self.max_right >= 0 else 'None'}")
                viz.append(f"Best so far: {self.best if self.best >= 0 else 'None'}")
                
                if self.max_right >= 0:
                    d = int(s[self.current_pos])
                    pair = d * 10 + self.max_right
                    viz.append(f"Current pair: {d}{self.max_right} = {pair}")
            else:
                viz.append("✓ Completed!")
                viz.append(f"Result: {self.best}")

        else:
            # Part 2 visualization
            viz.append("String: " + s)
            viz.append("")
            
            if self.current_pos < len(s):
                # Show current position
                pointer = " " * 8 + " " * self.current_pos + "^"
                viz.append(pointer)
                viz.append("")
                viz.append(f"Current char: {s[self.current_pos]}")
                viz.append(f"Stack: {''.join(self.stack)}")
                viz.append(f"Removed: {self.remove_count} / {self.total_to_remove}")
                viz.append(f"Stack size: {len(self.stack)}")
            else:
                viz.append("✓ Completed!")
                result = "".join(self.stack[:12])
                viz.append(f"Final stack: {''.join(self.stack)}")
                viz.append(f"Result (first 12): {result}")

        return "\n".join(viz)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Day3Visualizer()
    window.show()
    sys.exit(app.exec())
