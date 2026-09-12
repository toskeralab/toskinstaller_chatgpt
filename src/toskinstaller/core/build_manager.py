from __future__ import annotations

from pathlib import Path
from typing import Callable

from .build_result import BuildResult
from .project_detector import ProjectInfo
from ..toolchains.python.pyinstaller import PyInstallerToolchain


class BuildManager:
    def __init__(self, log_callback: Callable[[str], None] | None = None):
        self.log_callback = log_callback or (lambda _: None)

    def build(self, project: ProjectInfo, output_dir: str | Path) -> BuildResult:
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        if project.language != "python":
            raise NotImplementedError(f"No build backend implemented yet for {project.language!r}")
        if project.entrypoint is None:
            raise ValueError("Python project detected, but no entrypoint .py file was found.")
        tool = PyInstallerToolchain(project.root, project.entrypoint, output, self.log_callback)
        return tool.build()
