"""Shared fixtures for the pytest test suite."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Provide the single QApplication instance required by Qt widgets."""
    app = QApplication.instance() or QApplication([])
    yield app
