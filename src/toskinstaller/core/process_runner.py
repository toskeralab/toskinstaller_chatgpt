import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(slots=True)
class ToolResult:
    returncode: int
    stdout: str
    stderr: str


def find_command(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def run_command(command: list[str], cwd: Path, log: Callable[[str], None]) -> ToolResult:
    process = subprocess.run(command, cwd=cwd, text=True, capture_output=True, encoding="utf-8", errors="replace")
    for line in (process.stdout + "\n" + process.stderr).splitlines():
        if line.strip():
            log(line)
    return ToolResult(process.returncode, process.stdout, process.stderr)
