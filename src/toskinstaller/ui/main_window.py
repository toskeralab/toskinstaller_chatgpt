from __future__ import annotations

from pathlib import Path

from ..core.project_detector import detect_project
from ..core.build_manager import BuildManager
from ..packaging import get_backend

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QTextEdit, QVBoxLayout, QWidget,
)


class BuildThread(QThread):
    message = Signal(str)
    finished_result = Signal(object)

    def __init__(self, project: Path, product_name: str, output_format: str):
        super().__init__()
        self.project = project
        self.product_name = product_name
        self.output_format = output_format

    def run(self) -> None:
        try:
            info = detect_project(self.project)
            out = self.project / ".toskinstaller" / "build"
            manager = BuildManager(self.message.emit)
            result = manager.build(info, out)
            if not result.success or not result.executable:
                self.finished_result.emit(result)
                return
            backend = get_backend(self.output_format, self.message.emit)
            artifact = backend.package(result.executable, out / "package", self.product_name or self.project.name)
            self.finished_result.emit(artifact)
        except Exception as exc:
            self.finished_result.emit(exc)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TOSKINSTALLER")
        self.resize(900, 650)
        self.project: Path | None = None
        self.thread: BuildThread | None = None
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(QLabel("TOSKINSTALLER — Project → Build → Package"))
        self.project_label = QLabel("No project selected")
        layout.addWidget(self.project_label)
        select = QPushButton("Select project folder")
        select.clicked.connect(self.select_project)
        layout.addWidget(select)
        self.info = QLabel("Project detection: waiting")
        layout.addWidget(self.info)
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Product name")
        layout.addWidget(self.product_name)
        self.format = QComboBox()
        self.format.addItem("Portable (ZIP baseline)", "portable")
        self.format.addItem("EXE installer (engine required)", "exe")
        self.format.addItem("MSI installer (WiX required)", "msi")
        layout.addWidget(self.format)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)
        self.build_button = QPushButton("Build")
        self.build_button.clicked.connect(self.build)
        layout.addWidget(self.build_button)
        self.setCentralWidget(root)

    def select_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Select project")
        if not folder:
            return
        self.project = Path(folder)
        self.project_label.setText(str(self.project))
        try:
            info = detect_project(self.project)
            entry = info.entrypoint.name if info.entrypoint else "not found"
            self.info.setText(f"Detected: {info.language} | entrypoint: {entry}")
            self.product_name.setText(self.project.name)
        except Exception as exc:
            self.info.setText(f"Detection error: {exc}")

    def build(self):
        if not self.project:
            QMessageBox.warning(self, "TOSKINSTALLER", "Select a project first.")
            return
        self.log.clear()
        self.log.append("Starting build pipeline...")
        self.build_button.setEnabled(False)
        self.thread = BuildThread(
            self.project,
            self.product_name.text().strip(),
            self.format.currentData(),
        )
        self.thread.message.connect(self.log.append)
        self.thread.finished_result.connect(self._finished)
        self.thread.start()

    def _finished(self, result):
        self.build_button.setEnabled(True)
        if isinstance(result, Exception):
            self.log.append(f"ERROR: {result}")
            return
        if getattr(result, "success", False):
            self.log.append(f"Package created: {getattr(result, 'path', None)}")
        else:
            self.log.append(f"FAILED: {getattr(result, 'message', 'Build failed. Review the log.')}")
