from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


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


def run_command(command: Sequence[str], cwd: Path, log: Callable[[str], None]) -> ToolResult:
    """Run a tool and stream its output to the application log."""
    process = subprocess.Popen(
        list(command),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        line = line.rstrip("\r\n")
        lines.append(line)
        if line.strip():
            log(line)
    returncode = process.wait()
    output = "\n".join(lines)
    return ToolResult(returncode, output, "" if returncode == 0 else output)
