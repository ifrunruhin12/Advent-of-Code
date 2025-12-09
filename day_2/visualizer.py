import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QListWidget, QSlider, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

class PyQtInvalidIDVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Day 2 — Invalid ID Visualizer (PyQt6)")
        self.resize(800, 640)

        # state
        self.current_part = 1
        self.range_start = None
        self.range_end = None
        self.current_id = None
        self.invalid_ids = []
        self.total_sum = 0
        self.is_playing = False

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        # default speed in ms
        self.speed = 500

        self._build_ui()
        self._update_ui()

    # ---------- algorithm checks ----------
    def check_invalid_part1(self, id_):
        s = str(id_)
        if len(s) % 2 != 0:
            return False
        half = len(s) // 2
        return s[:half] == s[half:]

    def check_invalid_part2(self, id_):
        s = str(id_)
        doubled = s + s
        substring = doubled[1:-1]
        return s in substring

    def is_invalid(self, id_):
        return self.check_invalid_part1(id_) if self.current_part == 1 else self.check_invalid_part2(id_)

    # ---------- UI build ----------
    def _build_ui(self):
        main = QVBoxLayout()
        title = QLabel("<h2>Day 2 — Invalid ID Visualizer</h2>")
        main.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # part buttons
        parts = QHBoxLayout()
        self.part1_btn = QPushButton("Part 1")
        self.part1_btn.clicked.connect(self._set_part1)
        self.part2_btn = QPushButton("Part 2")
        self.part2_btn.clicked.connect(self._set_part2)
        parts.addWidget(self.part1_btn)
        parts.addWidget(self.part2_btn)
        main.addLayout(parts)

        # description
        self.desc = QLabel("")
        self.desc.setWordWrap(True)
        main.addWidget(self.desc)

        # range input + start
        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("Range:"))
        self.range_edit = QLineEdit("11-25")
        self.range_edit.setPlaceholderText("start-end (e.g. 11-25)")
        range_row.addWidget(self.range_edit)
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_range)
        range_row.addWidget(self.start_btn)
        main.addLayout(range_row)

        # control buttons: play / step / reset
        ctrl = QHBoxLayout()
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        self.step_btn = QPushButton("→ Step")
        self.step_btn.clicked.connect(self.step_forward)
        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.clicked.connect(self.reset)
        ctrl.addWidget(self.play_btn)
        ctrl.addWidget(self.step_btn)
        ctrl.addWidget(self.reset_btn)

        # speed slider
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

        # current check + visualization
        self.current_label = QLabel("Checking: -")
        main.addWidget(self.current_label)

        vis_row = QHBoxLayout()

        self.visual_box = QTextEdit()
        self.visual_box.setReadOnly(True)
        self.visual_box.setFixedHeight(200)
        vis_row.addWidget(self.visual_box, stretch=2)

        right_col = QVBoxLayout()
        # results (count + sum)
        results_box = QHBoxLayout()
        results_box.addWidget(QLabel("Invalid Count:"))
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("color: red; font-weight: bold;")
        results_box.addWidget(self.count_label)
        results_box.addStretch(1)
        results_box.addWidget(QLabel("Sum:"))
        self.sum_label = QLabel("0")
        self.sum_label.setStyleSheet("color: green; font-weight: bold;")
        results_box.addWidget(self.sum_label)
        right_col.addLayout(results_box)

        # invalid list
        right_col.addWidget(QLabel("Invalid IDs:"))
        self.invalid_list = QListWidget()
        right_col.addWidget(self.invalid_list)

        vis_row.addLayout(right_col, stretch=1)
        main.addLayout(vis_row)

        # examples
        examples = QLabel("<b>Examples</b><br>"
                          "Part1: 1212 (invalid), 1234 (valid).<br>"
                          "Part2: 123 (invalid if in doubled middle), 125 (valid).")
        examples.setWordWrap(True)
        main.addWidget(examples)

        self.setLayout(main)

    # ---------- UI helpers ----------
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

    def _update_ui(self):
        # part button styles
        if self.current_part == 1:
            self.part1_btn.setStyleSheet("background:#1976d2; color:white;")
            self.part2_btn.setStyleSheet("")
            self.desc.setText("An ID is invalid if it has an even number of digits and the first half equals the second half.")
        else:
            self.part2_btn.setStyleSheet("background:#6a1b9a; color:white;")
            self.part1_btn.setStyleSheet("")
            self.desc.setText("An ID is invalid if it appears as a substring in the doubled ID (excluding first and last char).")

        # labels
        self.current_label.setText(f"Checking: {self.current_id}" if self.current_id is not None else "Checking: -")
        self.visual_box.setPlainText(self._visualize_current())
        self.count_label.setText(str(len(self.invalid_ids)))
        self.sum_label.setText(str(self.total_sum))
        self.invalid_list.clear()
        for id_ in self.invalid_ids:
            self.invalid_list.addItem(str(id_))

        # enable/disable buttons
        self.play_btn.setEnabled(self.current_id is not None and not (self.current_id > (self.range_end or -1)))
        self.step_btn.setEnabled(not self.is_playing and self.current_id is not None and not (self.current_id > (self.range_end or -1)))

    # ---------- range / start / reset ----------
    def start_range(self):
        txt = self.range_edit.text().strip()
        if "-" not in txt:
            QMessageBox.warning(self, "Range error", "Please provide range as start-end (e.g. 11-25).")
            return
        try:
            a, b = txt.split("-", 1)
            s = int(a.strip())
            e = int(b.strip())
        except Exception:
            QMessageBox.warning(self, "Range error", "Invalid numbers in range.")
            return

        if s > e:
            QMessageBox.warning(self, "Range error", "Start must be <= end.")
            return

        self.range_start = s
        self.range_end = e
        self.current_id = s
        self.invalid_ids = []
        self.total_sum = 0
        self.is_playing = False
        self.timer.stop()
        self.timer.setInterval(self.speed)
        self._update_ui()

    def reset(self):
        self.timer.stop()
        self.is_playing = False
        self.current_id = None
        self.invalid_ids = []
        self.total_sum = 0
        self._update_ui()

    # ---------- stepping / playing ----------
    def step_forward(self):
        if self.current_id is None:
            return
        if self.current_id > self.range_end:
            self.is_playing = False
            self.timer.stop()
            return

        # do check
        if self.is_invalid(self.current_id):
            self.invalid_ids.append(self.current_id)
            self.total_sum += self.current_id

        # move next
        self.current_id += 1
        self._update_ui()

    def toggle_play(self):
        if self.current_id is None:
            return
        if not self.is_playing:
            self.is_playing = True
            self.play_btn.setText("⏸ Pause")
            self.timer.start(self.speed)
        else:
            self.is_playing = False
            self.play_btn.setText("▶ Play")
            self.timer.stop()

        self._update_ui()

    def _tick(self):
        # one tick -> perform a step
        self.step_forward()
        # stop if reached end
        if self.current_id is None or self.current_id > self.range_end:
            self.is_playing = False
            self.timer.stop()
            self.play_btn.setText("▶ Play")
        self._update_ui()

    # ---------- visualization text ----------
    def _visualize_current(self):
        if self.current_id is None or self.current_id > (self.range_end or -1):
            return ""

        s = str(self.current_id)
        if self.current_part == 1:
            if len(s) % 2 != 0:
                return f"{s}\n\nOdd length → VALID"
            half = len(s) // 2
            left = s[:half]
            right = s[half:]
            return (f"{s}\n\nLeft:  {left}\nRight: {right}\n"
                    + ("MATCH → INVALID" if left == right else "DIFFERENT → VALID"))
        else:
            doubled = s + s
            substring = doubled[1:-1]
            found = s in substring
            return (f"Original:  {s}\nDoubled:   {doubled}\nSubstring: {substring}\n\n"
                    + ("FOUND → INVALID" if found else "NOT FOUND → VALID"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PyQtInvalidIDVisualizer()
    w.show()
    sys.exit(app.exec())

