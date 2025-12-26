import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QSlider, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QScrollArea

class GridWidget(QWidget):
    def __init__(self, grid=None, highlights=None):
        super().__init__()
        self.grid = grid or []
        self.highlights = highlights or {}
        self.cell_size = 15

        if self.grid:
            self.setMinimumSize(
                len(self.grid[0]) * self.cell_size + 20,
                len(self.grid) * self.cell_size + 20
            )
        else:
            self.setMinimumSize(200, 200)

    def update_grid(self, grid, highlights=None):
        self.grid = grid
        self.highlights = highlights or {}

        if grid:
            self.setMinimumSize(
                len(grid[0]) * self.cell_size + 20,
                len(grid) * self.cell_size + 20
            )

        self.update()

    def paintEvent(self, event):
        if not self.grid:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rows = len(self.grid)
        cols = len(self.grid[0])
        cell_size = self.cell_size

        for r in range(rows):
            for c in range(cols):
                x = c * cell_size + 10
                y = r * cell_size + 10

                # Determine cell color
                if (r, c) in self.highlights:
                    color = self.highlights[(r, c)]
                elif self.grid[r][c] == '@':
                    color = QColor(100, 100, 100)  # Gray for @
                else:
                    color = QColor(240, 240, 240)  # Light gray for .

                painter.fillRect(x, y, cell_size, cell_size, color)
                painter.setPen(QPen(QColor(200, 200, 200), 1))
                painter.drawRect(x, y, cell_size, cell_size)


class Day4Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Day 4 — Grid Accessibility Visualizer")
        self.resize(1000, 800)

        # State
        self.current_part = 1
        self.original_grid = []
        self.grid = []
        self.current_row = 0
        self.current_col = 0
        self.is_playing = False
        self.speed = 100
        self.phase = "scanning"  # "scanning" or "removing"

        # Part 1 state
        self.accessible_count = 0

        # Part 2 state
        self.total_removed = 0
        self.iteration = 0
        self.to_remove = []

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

        self._build_ui()
        self._update_ui()

    def _build_ui(self):
        main = QVBoxLayout()

        title = QLabel("<h2>Day 4 — Grid Accessibility Visualizer</h2>")
        main.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Part buttons
        parts = QHBoxLayout()
        self.part1_btn = QPushButton("Part 1: Count Accessible")
        self.part1_btn.clicked.connect(self._set_part1)
        self.part2_btn = QPushButton("Part 2: Remove Until Stable")
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
        self.speed_slider.setRange(50, 500)
        self.speed_slider.setSingleStep(50)
        self.speed_slider.setValue(self.speed)
        self.speed_slider.valueChanged.connect(self._on_speed_change)
        ctrl.addWidget(self.speed_slider)
        self.speed_label = QLabel(f"{self.speed} ms")
        ctrl.addWidget(self.speed_label)
        main.addLayout(ctrl)

        # Status labels
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Idle")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.iteration_label = QLabel("Iteration: 0")
        status_layout.addWidget(self.iteration_label)

        main.addLayout(status_layout)

        # Grid widget
        self.grid_widget = GridWidget([])

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.grid_widget)

        main.addWidget(self.scroll_area, stretch=1)

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
        self.info_box.setMaximumHeight(100)
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
                content = f.read()
                self.original_grid = [list(line) for line in content.strip().splitlines()]
                self.grid = [row[:] for row in self.original_grid]
                self.grid_widget.update_grid(self.grid)
                QMessageBox.information(self, "Success", f"Loaded grid: {len(self.grid)}x{len(self.grid[0])}")
        except FileNotFoundError:
            QMessageBox.warning(self, "File Error", "Could not find example_in.txt")

    def start_processing(self):
        if not self.original_grid:
            QMessageBox.warning(self, "Input Error", "Please load a grid first")
            return

        self.grid = [row[:] for row in self.original_grid]
        self.current_row = 0
        self.current_col = 0
        self.accessible_count = 0
        self.total_removed = 0
        self.iteration = 0
        self.phase = "scanning"
        self.to_remove = []

        if self.current_part == 2:
            self.iteration = 1

        self._update_ui()

    def step_forward(self):
        if not self.grid:
            return

        if self.current_part == 1:
            self._step_part1()
        else:
            self._step_part2()

        self._update_ui()

    def _step_part1(self):
        rows, cols = len(self.grid), len(self.grid[0])

        # Find next @ cell
        while self.current_row < rows:
            while self.current_col < cols:
                if self.grid[self.current_row][self.current_col] == '@':
                    # Check neighbors
                    neighbors = self._count_neighbors(self.current_row, self.current_col)
                    
                    if neighbors < 4:
                        self.accessible_count += 1

                    self.current_col += 1
                    return
                self.current_col += 1

            self.current_row += 1
            self.current_col = 0

        # Finished
        self.phase = "complete"
        self.is_playing = False
        self.timer.stop()

    def _step_part2(self):
        rows, cols = len(self.grid), len(self.grid[0])

        if self.phase == "scanning":
            # Scan for cells to remove
            while self.current_row < rows:
                while self.current_col < cols:
                    if self.grid[self.current_row][self.current_col] == '@':
                        neighbors = self._count_neighbors(self.current_row, self.current_col)
                        
                        if neighbors < 4:
                            self.to_remove.append((self.current_row, self.current_col))

                    self.current_col += 1
                    return

                self.current_row += 1
                self.current_col = 0

            # Finished scanning
            if self.to_remove:
                self.phase = "removing"
                self.current_row = 0
            else:
                self.phase = "complete"
                self.is_playing = False
                self.timer.stop()

        elif self.phase == "removing":
            # Remove cells one by one
            if self.current_row < len(self.to_remove):
                r, c = self.to_remove[self.current_row]
                self.grid[r][c] = '.'
                self.total_removed += 1
                self.current_row += 1
            else:
                # Start next iteration
                self.phase = "scanning"
                self.current_row = 0
                self.current_col = 0
                self.to_remove = []
                self.iteration += 1

    def _count_neighbors(self, r, c):
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0), (1, 1)
        ]

        count = 0
        rows, cols = len(self.grid), len(self.grid[0])

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if self.grid[nr][nc] == '@':
                    count += 1

        return count

    def toggle_play(self):
        if not self.grid:
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

    def reset(self):
        self.timer.stop()
        self.is_playing = False
        if self.original_grid:
            self.grid = [row[:] for row in self.original_grid]
        self.current_row = 0
        self.current_col = 0
        self.accessible_count = 0
        self.total_removed = 0
        self.iteration = 0
        self.phase = "scanning"
        self.to_remove = []
        self.play_btn.setText("▶ Play")
        self._update_ui()

    def _update_ui(self):
        # Update part buttons
        if self.current_part == 1:
            self.part1_btn.setStyleSheet("background:#1976d2; color:white;")
            self.part2_btn.setStyleSheet("")
            self.desc.setText("Part 1: Count cells (@) with fewer than 4 neighbors. These cells are 'accessible'.")
        else:
            self.part2_btn.setStyleSheet("background:#6a1b9a; color:white;")
            self.part1_btn.setStyleSheet("")
            self.desc.setText("Part 2: Repeatedly remove accessible cells until no more can be removed.")

        # Update status
        if self.phase == "complete":
            self.status_label.setText("Status: Complete")
        elif self.phase == "scanning":
            if self.grid:
                self.status_label.setText(f"Status: Scanning ({self.current_row}, {self.current_col})")
            else:
                self.status_label.setText("Status: Idle")
        elif self.phase == "removing":
            self.status_label.setText(f"Status: Removing cells ({self.current_row}/{len(self.to_remove)})")

        # Update iteration label
        if self.current_part == 2:
            self.iteration_label.setText(f"Iteration: {self.iteration}")
        else:
            self.iteration_label.setText("")

        # Update result
        if self.current_part == 1:
            self.result_label.setText(str(self.accessible_count))
        else:
            self.result_label.setText(str(self.total_removed))

        # Update grid visualization
        highlights = {}
        if self.grid and self.phase == "scanning":
            if 0 <= self.current_row < len(self.grid) and 0 <= self.current_col < len(self.grid[0]):
                if self.grid[self.current_row][self.current_col] == '@':
                    neighbors = self._count_neighbors(self.current_row, self.current_col)
                    if neighbors < 4:
                        highlights[(self.current_row, self.current_col)] = QColor(255, 100, 100)  # Red
                    else:
                        highlights[(self.current_row, self.current_col)] = QColor(100, 255, 100)  # Green

        elif self.phase == "removing" and self.to_remove:
            for r, c in self.to_remove:
                if self.grid[r][c] == '@':
                    highlights[(r, c)] = QColor(255, 200, 0)  # Orange

        self.grid_widget.update_grid(self.grid, highlights)

        # Update info box
        info_lines = []
        if self.grid and 0 <= self.current_row < len(self.grid):
            if self.phase == "scanning" and 0 <= self.current_col < len(self.grid[0]):
                if self.grid[self.current_row][self.current_col] == '@':
                    neighbors = self._count_neighbors(self.current_row, self.current_col)
                    info_lines.append(f"Current cell: ({self.current_row}, {self.current_col})")
                    info_lines.append(f"Neighbors: {neighbors}/8")
                    info_lines.append(f"Accessible: {'Yes' if neighbors < 4 else 'No'}")
            elif self.phase == "removing" and self.to_remove:
                info_lines.append(f"Removing {len(self.to_remove)} cells this iteration")

        if self.phase == "complete":
            if self.current_part == 1:
                info_lines.append(f"✓ Scan complete! Found {self.accessible_count} accessible cells.")
            else:
                info_lines.append(f"✓ Process complete! Removed {self.total_removed} cells in {self.iteration} iterations.")

        self.info_box.setPlainText("\n".join(info_lines))

        # Enable/disable buttons
        has_grid = bool(self.grid)
        not_complete = self.phase != "complete"
        self.play_btn.setEnabled(has_grid and not_complete)
        self.step_btn.setEnabled(has_grid and not_complete and not self.is_playing)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Day4Visualizer()
    window.show()
    sys.exit(app.exec())
