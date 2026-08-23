"""Headless Qt smoke and behavior tests used by the CI gate."""

from queue import Queue

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget

from model.assert_env import AssertEnvWindow
from model.public_types import VerifyStatus
from model.qt_thread import WatchResultThread
from static.ui.main_ui import Ui_MainWindow
from utils.public_func import resize_window


def test_generated_main_ui_builds_with_essential_controls(qapp):
    window = QMainWindow()
    ui = Ui_MainWindow()

    ui.setupUi(window)

    assert ui.shareListTable.columnCount() == 6
    assert ui.downloadListTable.columnCount() == 3
    assert ui.createShareButton.isEnabled()


def test_resize_window_respects_minimum_layout_on_small_screen(qapp):
    widget = QWidget()

    resize_window(widget, (1066, 600), (1280, 720))

    assert widget.size().width() == 1066
    assert widget.size().height() == 600


def test_environment_check_window_renders_status_messages(qapp):
    window = AssertEnvWindow()

    window._append_text_edit((VerifyStatus.INFO, "configuration loaded"))
    window._append_text_edit((VerifyStatus.WARN, "network fallback"))

    assert "configuration loaded" in window.text_edit.toPlainText()
    assert "network fallback" in window.text_edit.toPlainText()


def test_environment_check_done_signal_is_delivered_by_event_loop(qtbot):
    window = AssertEnvWindow()
    qtbot.addWidget(window)
    window.assert_thread = type("StoppedThread", (), {"quit": lambda self: None})()

    with qtbot.waitSignal(window.all_safe, timeout=1000):
        window._enter_mainWindow()


def test_menu_button_click_changes_stacked_page_and_emits_qt_events(qtbot):
    from main import MainWindow

    window = MainWindow()
    window.closeEvent = lambda event: event.accept()
    qtbot.addWidget(window)
    window.show()

    qtbot.mouseClick(window.ui.serverButton, Qt.LeftButton)
    qtbot.waitUntil(lambda: window.ui.stackedWidget.currentWidget() is window.ui.server)
    assert window._ui_function._clicked_menu_name == "serverButton"

    qtbot.mouseClick(window.ui.clientButton, Qt.LeftButton)
    qtbot.waitUntil(lambda: window.ui.stackedWidget.currentWidget() is window.ui.client)
    assert window._ui_function._clicked_menu_name == "clientButton"


def test_watch_thread_signal_crosses_thread_boundary_and_stops_cleanly(qtbot):
    output_queue = Queue()
    thread = WatchResultThread(output_queue)

    with qtbot.waitSignal(thread.signal, timeout=1000) as blocker:
        thread.start()
        output_queue.put("h-share-id")

    assert blocker.args == ["h-share-id"]
    thread.run_flag = False
    output_queue.put("shutdown")
    assert thread.wait(1000)
