from __future__ import annotations

from pathlib import Path

from .base import PackagingBackend
from .portable import PortableZipBackend
from .unsupported import UnsupportedBackend


def get_backend(format_name: str, log=None) -> PackagingBackend:
    normalized = format_name.strip().lower().replace(" ", "-")
    if normalized in {"portable", "portable-zip"}:
        return PortableZipBackend(log)
    if normalized in {"exe", "exe-installer"}:
        return UnsupportedBackend(
            "EXE installer",
            "Configure an external Windows installer engine (Inno Setup or NSIS) before packaging.",
            log,
        )
    if normalized in {"msi", "msi-installer"}:
        return UnsupportedBackend(
            "MSI installer",
            "Configure WiX Toolset before packaging. MSI is not produced by renaming an EXE.",
            log,
        )
    if normalized == "both":
        raise ValueError("The 'both' output requires explicit EXE and MSI backend execution.")
    raise ValueError(f"Unknown packaging format: {format_name}")
