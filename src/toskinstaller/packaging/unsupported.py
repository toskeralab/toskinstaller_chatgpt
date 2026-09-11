from __future__ import annotations

from pathlib import Path

from .base import PackageArtifact, PackagingBackend


class UnsupportedBackend(PackagingBackend):
    """Explicit placeholder used until an external installer engine is ready."""

    def __init__(self, format_name: str, guidance: str, log=None):
        super().__init__(log)
        self.format_name = format_name
        self.guidance = guidance

    def package(self, executable: Path, output_dir: Path, product_name: str) -> PackageArtifact:
        message = f"{self.format_name} backend is not ready. {self.guidance}"
        self.log(message)
        return PackageArtifact(False, None, message)
