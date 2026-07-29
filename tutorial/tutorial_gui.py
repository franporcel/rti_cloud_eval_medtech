#!/usr/bin/env python3
"""Super simple guided-tutorial GUI, driven entirely by digital-or-tutorial.json.

Renders each step (title/body/openFiles/terminals/highlights/tryThis/links/...) with
Previous/Next navigation, "Open File" buttons (via VS Code CLI, falling back to `open`),
and "Run in Terminal" buttons (opens a new macOS Terminal window with the commands).

Usage:
    python3 tutorial_gui.py
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

TUTORIAL_DIR = Path(__file__).resolve().parent
JSON_PATH = TUTORIAL_DIR / "digital-or-tutorial.json"
REPO_ROOT = TUTORIAL_DIR / ".." / "medtech-reference-architecture"


def load_tutorial() -> dict:
    with JSON_PATH.open() as f:
        return json.load(f)


def open_file(path: str) -> None:
    full_path = (REPO_ROOT / path).resolve()
    if shutil.which("code"):
        subprocess.run(["code", str(full_path)], check=False)
    else:
        opener = "open" if platform.system() == "Darwin" else "xdg-open"
        subprocess.run([opener, str(full_path)], check=False)


def run_in_terminal(commands: list[str]) -> None:
    script = " && ".join(commands)
    if platform.system() == "Darwin":
        escaped = script.replace('"', '\\"')
        osa = f'tell application "Terminal" to do script "cd {REPO_ROOT.resolve()} && {escaped}"'
        subprocess.run(["osascript", "-e", osa], check=False)
    else:
        QMessageBox.information(
            None,
            "Run manually",
            f"Run this in a terminal from {REPO_ROOT.resolve()}:\n\n{script}",
        )


class StepView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout_ = QVBoxLayout(self)
        self.layout_.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout_)

    def clear(self) -> None:
        while self.layout_.count():
            item = self.layout_.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_heading(self, text: str) -> None:
        label = QLabel(text)
        label.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 6px;")
        label.setWordWrap(True)
        self.layout_.addWidget(label)

    def add_subheading(self, text: str) -> None:
        label = QLabel(text)
        label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        label.setWordWrap(True)
        self.layout_.addWidget(label)

    def add_paragraph(self, text: str) -> None:
        label = QLabel(text)
        label.setWordWrap(True)
        self.layout_.addWidget(label)

    def add_bullets(self, items: list[str]) -> None:
        for item in items:
            label = QLabel(f"\u2022 {item}")
            label.setWordWrap(True)
            self.layout_.addWidget(label)

    def add_divider(self) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        self.layout_.addWidget(line)

    def add_file_button(self, path: str) -> None:
        btn = QPushButton(f"\U0001F4C4 Open {path}")
        btn.clicked.connect(lambda: open_file(path))
        self.layout_.addWidget(btn)

    def add_terminal_block(self, terminal: dict) -> None:
        self.add_subheading(f"Terminal: {terminal.get('name', '')}")
        for cmd in terminal.get("commands", []):
            label = QLabel(cmd)
            label.setStyleSheet(
                "font-family: monospace; background: #2b2b2b; color: #d4d4d4; padding: 4px;"
            )
            label.setWordWrap(True)
            self.layout_.addWidget(label)
        btn = QPushButton("\u25B6 Run in New Terminal")
        btn.clicked.connect(lambda: run_in_terminal(terminal.get("commands", [])))
        self.layout_.addWidget(btn)

    def render_step(self, step: dict) -> None:
        self.clear()
        self.add_heading(f"{step['number']}. {step['title']}")

        for para in step.get("body", []):
            self.add_paragraph(para)

        if "background" in step:
            self.add_subheading("Background")
            self.add_bullets(step["background"])

        if "whatWellBuild" in step:
            wwb = step["whatWellBuild"]
            self.add_subheading("What we'll build")
            self.add_paragraph(wwb.get("description", ""))
            self.add_bullets(wwb.get("items", []))

        if "note" in step:
            self.add_paragraph(f"Note: {step['note']}")

        if "openFiles" in step:
            self.add_subheading("Files to explore")
            for f in step["openFiles"]:
                self.add_file_button(f)

        if "highlights" in step:
            self.add_subheading("Highlights")
            self.add_bullets(step["highlights"])

        if "highlight" in step:
            self.add_paragraph(step["highlight"])

        if "terminals" in step:
            self.add_subheading("Build & Run")
            for terminal in step["terminals"]:
                self.add_terminal_block(terminal)

        if "expectedResult" in step:
            self.add_subheading("Expected result")
            self.add_paragraph(step["expectedResult"])

        if "tryThis" in step:
            self.add_subheading("Try this")
            self.add_bullets(step["tryThis"])

        if "actions" in step:
            self.add_subheading("Actions")
            self.add_bullets(step["actions"])

        if "cloudEvalNote" in step:
            self.add_paragraph(f"Cloud eval note: {step['cloudEvalNote']}")

        if "keyTakeaway" in step:
            self.add_divider()
            label = QLabel(f"\U0001F511 {step['keyTakeaway']}")
            label.setWordWrap(True)
            label.setStyleSheet("font-style: italic;")
            self.layout_.addWidget(label)

        if "links" in step:
            self.add_subheading("Next Steps")
            for link in step["links"]:
                self.add_paragraph(f"\u2022 {link['label']} \u2014 {link['description']}")

        if "callToAction" in step:
            self.add_paragraph(step["callToAction"])


class TutorialWindow(QMainWindow):
    def __init__(self, tutorial: dict) -> None:
        super().__init__()
        self.tutorial = tutorial
        self.steps = tutorial["steps"]
        self.current_index = 0

        self.setWindowTitle(tutorial.get("title", "Tutorial"))
        self.resize(900, 650)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)

        self.step_list = QListWidget()
        self.step_list.setFixedWidth(260)
        for step in self.steps:
            item = QListWidgetItem(f"{step['number']}. {step['title']}")
            self.step_list.addItem(item)
        self.step_list.currentRowChanged.connect(self.go_to_step)
        root_layout.addWidget(self.step_list)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        self.step_view = StepView()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.step_view)
        right_layout.addWidget(scroll)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("\u25C0 Previous")
        self.prev_btn.clicked.connect(self.go_previous)
        self.next_btn = QPushButton("Next \u25B6")
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        right_layout.addLayout(nav_layout)

        root_layout.addWidget(right_container)

        self.step_list.setCurrentRow(0)

    def go_to_step(self, index: int) -> None:
        if index < 0 or index >= len(self.steps):
            return
        self.current_index = index
        self.step_view.render_step(self.steps[index])
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.steps) - 1)

    def go_previous(self) -> None:
        self.step_list.setCurrentRow(self.current_index - 1)

    def go_next(self) -> None:
        self.step_list.setCurrentRow(self.current_index + 1)


def main() -> None:
    tutorial = load_tutorial()
    app = QApplication(sys.argv)
    window = TutorialWindow(tutorial)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
