import errno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import tutorial_gui as gui


class RestoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = gui.QApplication.instance() or gui.QApplication([])

    def setUp(self):
        self.start_patch(patch.dict(os.environ, {"MEDTECH_UI_MODE": "--vscode"}))
        self.health = self.start_patch(patch.object(gui, "app_running", return_value=True))
        self.spawn = self.start_patch(patch.object(gui.subprocess, "Popen"))
        self.window = gui.TutorialWindow(gui.load_tutorial())
        self.window.startup_deadline = 0
        self.addCleanup(self.window.close)

    def start_patch(self, patcher):
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def test_running_app_does_not_open_or_launch(self):
        for name, button in self.window.app_buttons.items():
            self.assertFalse(button.isEnabled())
            button.click()
            self.window.restore_app(name)
        self.spawn.assert_not_called()

    def test_restore_buttons_match_grid(self):
        parent_layout = self.window.app_buttons["ArmController"].parentWidget().layout()
        layout = next(
            parent_layout.itemAt(index).layout()
            for index in range(parent_layout.count())
            if isinstance(parent_layout.itemAt(index).layout(), gui.QGridLayout)
        )
        expected = (("ArmController", "Orchestrator"), ("Arm", "PatientMonitor"))
        for row, names in enumerate(expected):
            for column, name in enumerate(names):
                self.assertIs(layout.itemAtPosition(row, column).widget(), self.window.app_buttons[name])

    def test_stopping_then_restored_app(self):
        self.window.update_app_buttons()
        self.assertFalse(self.window.app_buttons["Arm"].isEnabled())
        self.window.restore_app("Arm")
        self.spawn.assert_not_called()
        self.health.return_value = False
        self.spawn.return_value.poll.return_value = None
        self.window.update_app_buttons()
        self.assertTrue(self.window.app_buttons["Arm"].isEnabled())
        self.window.app_buttons["Arm"].click()
        self.spawn.assert_called_once()
        self.assertIn("Arm", self.spawn.call_args.args[0])
        self.health.return_value = True
        self.window.update_app_buttons()
        self.assertFalse(self.window.app_buttons["Arm"].isEnabled())
        self.spawn.return_value.poll.return_value = 0

    def test_unknown_health_does_not_launch(self):
        self.health.return_value = None
        self.window.update_app_buttons()
        self.assertFalse(self.window.app_buttons["Arm"].isEnabled())
        self.window.restore_app("Arm")
        self.spawn.assert_not_called()

    def test_stopped_app_launches_only_once_while_starting(self):
        self.health.return_value = False
        self.spawn.return_value.poll.return_value = None
        self.window.update_app_buttons()
        self.assertTrue(self.window.app_buttons["Arm"].isEnabled())
        self.window.app_buttons["Arm"].click()
        self.window.restore_app("Arm")
        self.assertFalse(self.window.app_buttons["Arm"].isEnabled())
        self.spawn.assert_called_once()
        self.spawn.return_value.poll.return_value = 0


class HealthTests(unittest.TestCase):
    def test_real_http_listener_and_stopped_listener(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        port = server.server_port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.assertIs(gui.app_running(port), True)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
        self.assertIs(gui.app_running(port), False)

    def test_only_refused_connections_mean_stopped(self):
        errors = [
            (urllib.error.URLError(ConnectionRefusedError(errno.ECONNREFUSED, "refused")), False),
            (urllib.error.URLError(TimeoutError()), None),
            (TimeoutError(), None),
            (urllib.error.HTTPError("http://localhost", 503, "busy", {}, None), True),
        ]
        for error, expected in errors:
            with self.subTest(error=error), patch.object(gui.urllib.request, "build_opener") as factory:
                factory.return_value.open.side_effect = error
                self.assertIs(gui.app_running(8092), expected)


@unittest.skipIf(os.name == "nt", "Process groups use POSIX signals")
class SignalCleanupTests(unittest.TestCase):
    def test_sigterm_closes_gui_and_stops_restored_app(self):
        script = """import subprocess, sys
sys.path.insert(0, sys.argv[1])
import tutorial_gui as gui
class TestWindow(gui.TutorialWindow):
    def __init__(self, tutorial):
        super().__init__(tutorial)
        self.child = subprocess.Popen(
            [sys.executable, '-c', 'import signal, time; signal.signal(signal.SIGINT, signal.SIG_IGN); time.sleep(120)'],
            start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.restarted_apps['Arm'] = self.child
    def show(self):
        super().show()
        print(self.child.pid, flush=True)
gui.TutorialWindow = TestWindow
sys.argv = [sys.argv[0]]
gui.main()
"""
        env = dict(os.environ, QT_QPA_PLATFORM="offscreen", MEDTECH_UI_MODE="--native")
        process = subprocess.Popen(
            [sys.executable, "-c", script, str(Path(__file__).resolve().parent)],
            env=env, stdout=subprocess.PIPE, text=True,
        )
        child_pid = None
        try:
            child_pid = int(process.stdout.readline())
            os.kill(process.pid, signal.SIGTERM)
            self.assertEqual(process.wait(timeout=8), 0)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.01)
            else:
                self.fail("Restored app survived tutorial SIGTERM")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            if child_pid is not None:
                try:
                    os.killpg(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass


if __name__ == "__main__":
    unittest.main()