from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BuildResult:
    success: bool
    executable: Path | None
    output_dir: Path
    log: str
