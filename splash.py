#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QProgressBar,
    QLabel, QMainWindow
)
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        # Frameless, always‑on‑top window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 200)
        self._center_on_screen()

        # Layout: label + progress bar
        layout = QVBoxLayout(self)
        self.label = QLabel("Loading, please wait...", self, alignment=Qt.AlignCenter)
        layout.addWidget(self.label)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        # Timer to simulate loading
        self._value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(30)  # update every 30 ms

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _update(self):
        self._value += 1
        self.progress.setValue(self._value)
        if self._value >= 100:
            self.timer.stop()
            self.close()
            self._show_main()

    def _show_main(self):
        self.main = MainWindow()
        self.main.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")
        self.setGeometry(600, 300, 800, 600)
        lbl = QLabel("✅ Main App Loaded!", self, alignment=Qt.AlignCenter)
        self.setCentralWidget(lbl)

def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
