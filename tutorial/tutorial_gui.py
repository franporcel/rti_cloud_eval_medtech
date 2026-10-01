#!/usr/bin/env python3
"""Guided-tutorial GUI, driven by digital-or-tutorial.json.

Renders each step (title/body/openFiles/terminals/highlights/tryThis/links/...) with
Previous/Next navigation, "Open File" buttons (via VS Code CLI, falling back to `open`),
and "Run in Terminal" buttons (opens a new macOS Terminal window with the commands).

Usage:
    python3 tutorial_gui.py
"""
from __future__ import annotations

import errno
import json
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PySide6.QtCore import Qt, QSocketNotifier, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
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
APP_PORTS = {"ArmController": 8091, "Orchestrator": 8090, "Arm": 8092, "PatientMonitor": 8093}


def app_running(port: int) -> bool | None:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{port}/api/state", timeout=0.15):
            return True
    except urllib.error.HTTPError:
        return True
    except urllib.error.URLError as exc:
        return False if getattr(exc.reason, "errno", None) == errno.ECONNREFUSED else None
    except OSError:
        return None


def load_tutorial() -> dict:
    with JSON_PATH.open() as f:
        return json.load(f)


def open_file(path: str) -> None:
    full_path = (REPO_ROOT / path).resolve()
    if os.environ.get("MEDTECH_CLOUD") == "1":
        subprocess.run([
            "/app/code-server/bin/code-server", "--user-data-dir",
            os.environ.get("MEDTECH_CODE_SERVER_DATA", "/config/data"),
            "--reuse-window", str(full_path),
        ], check=False)
    elif shutil.which("code"):
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

        self.app_buttons = {}
        self.restarted_apps: dict[str, subprocess.Popen] = {}
        self.startup_deadline = time.monotonic() + 15 if os.environ.get("MEDTECH_DEMO_STARTING") else 0
        self.seen_apps: set[str] = set()
        if os.environ.get("MEDTECH_UI_MODE", "--vscode") == "--vscode":
            restore_layout = QGridLayout()
            for index, (name, port) in enumerate(APP_PORTS.items()):
                button = QPushButton(f"Restore {name}")
                button.setToolTip(f"Restart {name} and reopen its tab after the app stops")
                button.clicked.connect(lambda _checked=False, app=name: self.restore_app(app))
                restore_layout.addWidget(button, index // 2, index % 2)
                self.app_buttons[name] = button
            right_layout.addLayout(restore_layout)

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
        if self.app_buttons:
            self.status_timer = QTimer(self)
            self.status_timer.timeout.connect(self.update_app_buttons)
            self.status_timer.start(1500)
            self.update_app_buttons()

    def update_app_buttons(self) -> None:
        for name, port in APP_PORTS.items():
            running = app_running(port)
            if running is True:
                self.seen_apps.add(name)
            starting = self.restarted_apps.get(name)
            pending = starting is not None and starting.poll() is None and not running
            booting = name not in self.seen_apps and time.monotonic() < self.startup_deadline
            self.app_buttons[name].setEnabled(
                not pending and not booting and running is False
            )

    def restore_app(self, name: str) -> None:
        port = APP_PORTS[name]
        running = app_running(port)
        if running is not False:
            self.update_app_buttons()
            return
        starting = self.restarted_apps.get(name)
        if starting is not None and starting.poll() is None:
            return
        try:
            arguments = [str(TUTORIAL_DIR / "run_digital_or.sh"), "--launch-only", name, "--vscode"]
            if os.environ.get("MEDTECH_SECURITY") == "1":
                arguments.append("--secure")
            self.restarted_apps[name] = subprocess.Popen(
                arguments,
                cwd=TUTORIAL_DIR.parent,
                start_new_session=True,
            )
        except OSError as exc:
            QMessageBox.warning(self, "Unable to restore app", str(exc))
        self.update_app_buttons()

    def closeEvent(self, event) -> None:
        for process in self.restarted_apps.values():
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        super().closeEvent(event)

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
    read_signal, write_signal = socket.socketpair()
    write_signal.setblocking(False)
    previous_wakeup = signal.set_wakeup_fd(write_signal.fileno())
    previous_handler = signal.signal(signal.SIGTERM, lambda _signum, _frame: None)
    notifier = QSocketNotifier(read_signal.fileno(), QSocketNotifier.Read, window)
    notifier.activated.connect(lambda _fd: window.close())
    window.show()
    try:
        exit_code = app.exec()
    finally:
        signal.set_wakeup_fd(previous_wakeup)
        signal.signal(signal.SIGTERM, previous_handler)
        read_signal.close()
        write_signal.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
