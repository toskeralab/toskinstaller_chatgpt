from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(slots=True)
class PackageArtifact:
    success: bool
    path: Path | None
    message: str = ""


class PackagingBackend(ABC):
    """Contract implemented by every final-output packaging backend."""

    format_name: str

    def __init__(self, log: Callable[[str], None] | None = None):
        self.log = log or (lambda _message: None)

    @abstractmethod
    def package(self, executable: Path, output_dir: Path, product_name: str) -> PackageArtifact:
        raise NotImplementedError
