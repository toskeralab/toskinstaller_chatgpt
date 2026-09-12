from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import sys

from ...core.process_runner import find_command, run_command
from ...core.build_result import BuildResult


@dataclass(slots=True)
class PyInstallerToolchain:
    project_root: Path
    entrypoint: Path
    output_dir: Path
    log: Callable[[str], None]

    def _command(self) -> list[str]:
        executable = find_command("pyinstaller", "pyinstaller.exe")
        if executable:
            return [executable]
        try:
            import importlib.util
            if importlib.util.find_spec("PyInstaller") is not None:
                return [sys.executable, "-m", "PyInstaller"]
        except (ImportError, ModuleNotFoundError):
            pass
        raise RuntimeError(
            "PyInstaller is not installed. Install it in the Python environment "
            "used by TOSKINSTALLER with: python -m pip install pyinstaller"
        )

    def build(self) -> BuildResult:
        command = self._command() + [
            "--noconfirm", "--clean", "--onefile",
            "--name", self.project_root.name,
            "--distpath", str(self.output_dir / "dist"),
            "--workpath", str(self.output_dir / "build"),
            "--specpath", str(self.output_dir / "spec"),
            str(self.entrypoint),
        ]
        result = run_command(command, self.project_root, self.log)
        exe = self.output_dir / "dist" / f"{self.project_root.name}.exe"
        return BuildResult(
            result.returncode == 0 and exe.is_file(),
            exe if exe.is_file() else None,
            self.output_dir,
            result.stdout + ("\n" + result.stderr if result.stderr else ""),
        )
