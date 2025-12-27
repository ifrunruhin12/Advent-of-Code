import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSlider, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

class RangeVisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ranges = []
        self.numbers = []
        self.current_number = None
        self.highlighted_ranges = []
        self.merged_ranges = []
        self.current_part = 1
        self.setMinimumHeight(400)

    def update_data(self, ranges, numbers, current_number=None, highlighted_ranges=None, merged_ranges=None, part=1):
        self.ranges = ranges
        self.numbers = numbers
        self.current_number = current_number
        self.highlighted_ranges = highlighted_ranges or []
        self.merged_ranges = merged_ranges or []
        self.current_part = part
        self.update()

    def paintEvent(self, event) -> None:
        if not self.ranges:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate scale
        all_nums = []
        for r in self.ranges:
            all_nums.extend(r)
        if self.numbers:
            all_nums.extend(self.numbers)

        if not all_nums:
            return

        min_val = min(all_nums)
        max_val = max(all_nums)
        range_span = max_val - min_val
        if range_span == 0:
            range_span = 1

        width = self.width() - 60
        height = self.height() - 60
        margin_left = 30
        margin_top = 30

        def scale_x(val):
            return margin_left + (val - min_val) / range_span * width

        # Draw axis
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(margin_left, margin_top + height, margin_left + width, margin_top + height)

        # Draw tick marks
        num_ticks = 10
        for i in range(num_ticks + 1):
            val = min_val + (range_span * i / num_ticks)
            x = scale_x(val)
            painter.drawLine(int(x), margin_top + height - 5, int(x), margin_top + height + 5)
            painter.drawText(int(x - 20), margin_top + height + 20, f"{int(val)}")

        # Part 1: Draw ranges and numbers
        if self.current_part == 1:
            # Draw ranges
            y_offset = margin_top + 20
            for idx, (start, end) in enumerate(self.ranges):
                x1 = scale_x(start)
                x2 = scale_x(end)
                
                if idx in self.highlighted_ranges:
                    color = QColor(100, 200, 100, 180)
                else:
                    color = QColor(100, 150, 255, 150)

                painter.fillRect(int(x1), y_offset, int(x2 - x1), 30, color)
                painter.setPen(QPen(QColor(50, 50, 150), 2))
                painter.drawRect(int(x1), y_offset, int(x2 - x1), 30)
                
                # Range label
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.drawText(int(x1 + 5), y_offset + 20, f"{start}-{end}")

                y_offset += 40

            # Draw numbers
            if self.numbers:
                y_numbers = margin_top + height - 50
                for num in self.numbers:
                    x = scale_x(num)
                    
                    if num == self.current_number:
                        color = QColor(255, 100, 100)
                        size = 10
                    else:
                        color = QColor(200, 100, 50)
                        size = 6

                    painter.setBrush(color)
                    painter.setPen(QPen(color, 2))
                    painter.drawEllipse(int(x - size/2), int(y_numbers - size/2), int(size), int(size))
                    
                    if num == self.current_number:
                        painter.setPen(QPen(QColor(0, 0, 0), 1))
                        painter.drawText(int(x - 15), y_numbers - 15, str(num))

        # Part 2: Draw merged ranges
        else:
            y_offset = margin_top + 20
            
            # Draw original ranges
            for start, end in self.ranges:
                x1 = scale_x(start)
                x2 = scale_x(end)
                
                color = QColor(200, 200, 200, 150)
                painter.fillRect(int(x1), y_offset, int(x2 - x1), 25, color)
                painter.setPen(QPen(QColor(150, 150, 150), 1))
                painter.drawRect(int(x1), y_offset, int(x2 - x1), 25)

            y_offset += 35

            # Draw merged ranges
            if self.merged_ranges:
                painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                for start, end in self.merged_ranges:
                    x1 = scale_x(start)
                    x2 = scale_x(end)
                    
                    color = QColor(100, 200, 100, 200)
                    painter.fillRect(int(x1), y_offset, int(x2 - x1), 35, color)
                    painter.setPen(QPen(QColor(50, 150, 50), 3))
                    painter.drawRect(int(x1), y_offset, int(x2 - x1), 35)
                    
                    # Range label
                    painter.setPen(QPen(QColor(0, 0, 0), 1))
                    painter.drawText(int(x1 + 5), y_offset + 22, f"{start}-{end}")

                y_offset += 45

        # Legend
        legend_y = 10
        if self.current_part == 1:
            painter.fillRect(10, legend_y, 20, 15, QColor(100, 150, 255, 150))
            painter.drawText(35, legend_y + 12, "Ranges")
            painter.fillRect(10, legend_y + 20, 20, 15, QColor(100, 200, 100, 180))
            painter.drawText(35, legend_y + 32, "Matching Range")
        else:
            painter.fillRect(10, legend_y, 20, 15, QColor(200, 200, 200, 150))
            painter.drawText(35, legend_y + 12, "Original")
            painter.fillRect(10, legend_y + 20, 20, 15, QColor(100, 200, 100, 200))
            painter.drawText(35, legend_y + 32, "Merged")


class Day5Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Day 5 — Range Checker Visualizer")
        self.resize(1000, 700)

        # State
        self.current_part = 1
        self.ranges = []
        self.numbers = []
        self.current_number_idx = 0
        self.count = 0
        self.is_playing = False
        self.speed = 500

        # Part 2 state
        self.merged_ranges = []
        self.total_count = 0

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        self._build_ui()
        self._update_ui()

    def _build_ui(self):
        main = QVBoxLayout()

        title = QLabel("<h2>Day 5 — Range Checker Visualizer</h2>")
        main.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Part buttons
        parts = QHBoxLayout()
        self.part1_btn = QPushButton("Part 1: Count Numbers in Ranges")
        self.part1_btn.clicked.connect(self._set_part1)
        self.part2_btn = QPushButton("Part 2: Merge Ranges")
        self.part2_btn.clicked.connect(self._set_part2)
        parts.addWidget(self.part1_btn)
        parts.addWidget(self.part2_btn)
        main.addLayout(parts)

        # Description
        self.desc = QLabel("")
        self.desc.setWordWrap(True)
        main.addWidget(self.desc)

        # Load button
        load_row = QHBoxLayout()
        self.load_btn = QPushButton("Load from File")
        self.load_btn.clicked.connect(self._load_file)
        load_row.addWidget(self.load_btn)
        load_row.addStretch()
        main.addLayout(load_row)

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

        # Status
        self.status_label = QLabel("Status: Idle")
        main.addWidget(self.status_label)

        # Visualizer widget
        self.viz_widget = RangeVisualizerWidget()
        scroll = QScrollArea()
        scroll.setWidget(self.viz_widget)
        scroll.setWidgetResizable(True)
        main.addWidget(scroll, stretch=1)

        # Results
        results = QHBoxLayout()
        results.addWidget(QLabel("Result:"))
        self.result_label = QLabel("0")
        self.result_label.setStyleSheet("color: green; font-weight: bold; font-size: 16pt;")
        results.addWidget(self.result_label)
        results.addStretch()
        main.addLayout(results)

        # Info box
        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setMaximumHeight(80)
        main.addWidget(self.info_box)

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
            with open("input.txt", "r") as f:
                content = f.read().strip()
                parts = content.split("\n\n")
                
                self.ranges = []
                for line in parts[0].splitlines():
                    start, end = map(int, line.split('-'))
                    self.ranges.append((start, end))
                
                if len(parts) > 1:
                    self.numbers = list(map(int, parts[1].splitlines()))
                else:
                    self.numbers = []
                
                QMessageBox.information(self, "Success", 
                    f"Loaded {len(self.ranges)} ranges and {len(self.numbers)} numbers")
                self._update_ui()
        except FileNotFoundError:
            QMessageBox.warning(self, "File Error", "Could not find example_in.txt")

    def start_processing(self):
        if not self.ranges:
            QMessageBox.warning(self, "Input Error", "Please load data first")
            return

        self.current_number_idx = 0
        self.count = 0
        self.total_count = 0
        self.merged_ranges = []

        if self.current_part == 2:
            self._merge_ranges()
        
        self._update_ui()

    def step_forward(self):
        if self.current_part == 1:
            self._step_part1()
        else:
            # Part 2 is instant
            pass
        
        self._update_ui()

    def _step_part1(self):
        if self.current_number_idx >= len(self.numbers):
            self.is_playing = False
            self.timer.stop()
            return

        num = self.numbers[self.current_number_idx]
        
        # Check which ranges contain this number
        highlighted = []
        found = False
        for idx, (start, end) in enumerate(self.ranges):
            if start <= num <= end:
                highlighted.append(idx)
                if not found:
                    self.count += 1
                    found = True
        
        self.viz_widget.update_data(
            self.ranges, 
            self.numbers, 
            num, 
            highlighted, 
            None,
            1
        )
        
        self.current_number_idx += 1

    def _merge_ranges(self):
        if not self.ranges:
            return
        
        sorted_ranges = sorted(self.ranges)
        merged = []
        current_start, current_end = sorted_ranges[0]
        
        for start, end in sorted_ranges[1:]:
            if start <= current_end + 1:
                current_end = max(current_end, end)
            else:
                merged.append((current_start, current_end))
                self.total_count += current_end - current_start + 1
                current_start, current_end = start, end
        
        merged.append((current_start, current_end))
        self.total_count += current_end - current_start + 1
        
        self.merged_ranges = merged
        self.viz_widget.update_data(
            self.ranges,
            [],
            None,
            None,
            merged,
            2
        )

    def toggle_play(self):
        if self.current_part == 2:
            return  # Part 2 doesn't need animation
        
        if not self.numbers:
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
        if self.current_number_idx >= len(self.numbers):
            self.is_playing = False
            self.timer.stop()
            self.play_btn.setText("▶ Play")

    def reset(self):
        self.timer.stop()
        self.is_playing = False
        self.current_number_idx = 0
        self.count = 0
        self.total_count = 0
        self.merged_ranges = []
        self.play_btn.setText("▶ Play")
        
        if self.ranges:
            self.viz_widget.update_data(self.ranges, self.numbers, None, None, None, self.current_part)
        
        self._update_ui()

    def _update_ui(self):
        # Update part buttons
        if self.current_part == 1:
            self.part1_btn.setStyleSheet("background:#1976d2; color:white;")
            self.part2_btn.setStyleSheet("")
            self.desc.setText("Part 1: Check how many numbers fall within the given ranges.")
        else:
            self.part2_btn.setStyleSheet("background:#6a1b9a; color:white;")
            self.part1_btn.setStyleSheet("")
            self.desc.setText("Part 2: Merge overlapping ranges and count total numbers covered.")

        # Update status
        if self.current_part == 1:
            if self.current_number_idx < len(self.numbers):
                self.status_label.setText(f"Status: Checking number {self.current_number_idx + 1} / {len(self.numbers)}")
            elif self.numbers:
                self.status_label.setText("Status: Complete")
            else:
                self.status_label.setText("Status: Idle")
        else:
            if self.merged_ranges:
                self.status_label.setText("Status: Ranges merged")
            else:
                self.status_label.setText("Status: Idle")

        # Update result
        if self.current_part == 1:
            self.result_label.setText(str(self.count))
        else:
            self.result_label.setText(str(self.total_count))

        # Update info box
        info_lines = []
        if self.current_part == 1:
            if self.current_number_idx > 0 and self.current_number_idx <= len(self.numbers):
                num = self.numbers[self.current_number_idx - 1]
                info_lines.append(f"Checking number: {num}")
                
                in_range = False
                for start, end in self.ranges:
                    if start <= num <= end:
                        info_lines.append(f"✓ Found in range {start}-{end}")
                        in_range = True
                        break
                
                if not in_range:
                    info_lines.append("✗ Not in any range")
        else:
            if self.merged_ranges:
                info_lines.append(f"Merged {len(self.ranges)} ranges into {len(self.merged_ranges)} ranges")
                info_lines.append(f"Total numbers covered: {self.total_count}")

        self.info_box.setPlainText("\n".join(info_lines))

        # Enable/disable buttons
        has_data = bool(self.ranges)
        can_play = self.current_part == 1 and has_data and len(self.numbers) > 0 and self.current_number_idx < len(self.numbers)
 
        self.play_btn.setEnabled(can_play)
        self.step_btn.setEnabled(can_play and not self.is_playing)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Day5Visualizer()
    window.show()
    sys.exit(app.exec())
