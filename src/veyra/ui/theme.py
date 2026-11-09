"""VEYRA visual theme helpers."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication


DARK_STYLESHEET = """
QWidget { color: #e8f7fa; font-family: 'Segoe UI'; font-size: 10pt; }
QMainWindow, QDialog, QWizard { background: #111820; }
QFrame#card, QFrame#sidebar, QFrame#titlebar { background: #18242d; border: 1px solid #2d414c; border-radius: 14px; }
QLabel#brand { color: #67e8f9; font-size: 20pt; font-weight: 700; letter-spacing: 2px; }
QLabel#tagline, QLabel#muted { color: #8ca5ae; }
QLabel#section { color: #67e8f9; font-size: 9pt; font-weight: 700; letter-spacing: 1px; }
QLabel#status { color: #8ff0c4; font-weight: 600; }
QPushButton { background: #22343e; border: 1px solid #39525e; border-radius: 8px; padding: 8px 12px; }
QPushButton:hover { background: #2b4652; border-color: #67e8f9; }
QPushButton#primary { background: #0e8c9f; border-color: #67e8f9; color: white; font-weight: 700; }
QPushButton#danger { background: #7b2d3a; border-color: #c96a78; }
QPushButton#nav { text-align: left; border: none; background: transparent; padding: 10px; }
QPushButton#nav:checked, QPushButton#nav:hover { background: #223b47; color: #67e8f9; }
QSlider::groove:horizontal { height: 5px; background: #314650; border-radius: 2px; }
QSlider::handle:horizontal { width: 15px; margin: -5px 0; background: #67e8f9; border-radius: 7px; }
QComboBox { background: #22343e; border: 1px solid #39525e; border-radius: 6px; padding: 6px; }
QWizardPage { background: #111820; }
"""

LIGHT_STYLESHEET = """
QWidget { color: #1c2a30; font-family: 'Segoe UI'; font-size: 10pt; }
QMainWindow, QDialog, QWizard { background: #eef7f8; }
QFrame#card, QFrame#sidebar, QFrame#titlebar { background: #ffffff; border: 1px solid #bfd6da; border-radius: 14px; }
QLabel#brand { color: #087d8e; font-size: 20pt; font-weight: 700; letter-spacing: 2px; }
QLabel#tagline, QLabel#muted { color: #587178; }
QLabel#section { color: #087d8e; font-size: 9pt; font-weight: 700; letter-spacing: 1px; }
QLabel#status { color: #19734c; font-weight: 600; }
QPushButton { background: #e1eff1; border: 1px solid #a9c5ca; border-radius: 8px; padding: 8px 12px; }
QPushButton:hover { background: #cfe7ea; border-color: #087d8e; }
QPushButton#primary { background: #0e8c9f; border-color: #087d8e; color: white; font-weight: 700; }
QPushButton#danger { background: #f5dfe2; border-color: #c96a78; }
QPushButton#nav { text-align: left; border: none; background: transparent; padding: 10px; }
QPushButton#nav:checked, QPushButton#nav:hover { background: #d9eef0; color: #087d8e; }
QSlider::groove:horizontal { height: 5px; background: #b9d0d4; border-radius: 2px; }
QSlider::handle:horizontal { width: 15px; margin: -5px 0; background: #087d8e; border-radius: 7px; }
QComboBox { background: #ffffff; border: 1px solid #a9c5ca; border-radius: 6px; padding: 6px; }
QWizardPage { background: #eef7f8; }
"""


def apply_theme(application: QApplication, theme: str) -> None:
    application.setStyleSheet(LIGHT_STYLESHEET if theme == "light" else DARK_STYLESHEET)
