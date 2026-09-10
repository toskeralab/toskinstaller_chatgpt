from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QComboBox, QLineEdit, QTextEdit
from PySide6.QtCore import Qt
from pathlib import Path

from ..core.project_detector import detect_project
from ..core.build_manager import BuildManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TOSKINSTALLER")
        self.resize(860, 620)
        self.project: Path | None = None
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(QLabel("TOSKINSTALLER — Project → Executable → Package"))
        self.project_label = QLabel("No project selected")
        layout.addWidget(self.project_label)
        select = QPushButton("Select project folder")
        select.clicked.connect(self.select_project)
        layout.addWidget(select)
        self.info = QLabel("Project detection: waiting")
        layout.addWidget(self.info)
        self.format = QComboBox()
        self.format.addItems(["EXE installer", "MSI installer", "Portable"])
        layout.addWidget(self.format)
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Product name")
        layout.addWidget(self.product_name)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log, 1)
        build = QPushButton("Build")
        build.clicked.connect(self.build)
        layout.addWidget(build)
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
            self.log.append("Select a project first.")
            return
        try:
            info = detect_project(self.project)
            out = self.project / ".toskinstaller" / "build"
            manager = BuildManager(self.log.append)
            result = manager.build(info, out)
            if result.success:
                self.log.append(f"Executable created: {result.executable}")
                if self.format.currentText() == "Portable":
                    from ..packaging.portable import create_portable_package
                    archive = create_portable_package(result.executable, out / "package", self.product_name.text() or self.project.name)
                    self.log.append(f"Portable archive created: {archive}")
            else:
                self.log.append("Build failed. Review the log above.")
        except Exception as exc:
            self.log.append(f"ERROR: {exc}")
