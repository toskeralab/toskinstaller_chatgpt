from __future__ import annotations

from pathlib import Path
import shutil

from .base import PackageArtifact, PackagingBackend


class PortableZipBackend(PackagingBackend):
    """Portable baseline: a clean payload archive.

    A true self-extracting EXE is intentionally a separate backend; this class
    never mislabels a ZIP as an executable installer.
    """

    format_name = "portable-zip"

    def package(self, executable: Path, output_dir: Path, product_name: str) -> PackageArtifact:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = output_dir / "payload"
        payload.mkdir(parents=True, exist_ok=True)
        target = payload / executable.name
        shutil.copy2(executable, target)
        archive_base = output_dir / f"{product_name}-portable"
        archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=payload))
        self.log(f"Portable package created: {archive}")
        return PackageArtifact(True, archive)
