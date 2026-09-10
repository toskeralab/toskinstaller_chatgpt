from pathlib import Path
import shutil
import zipfile


def safe_relative(base: Path, candidate: Path) -> Path:
    base = base.resolve()
    candidate = candidate.resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError("Path escapes package root")
    return candidate.relative_to(base)


def create_portable_package(executable: Path, destination: Path, product_name: str) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    payload = destination / "payload"
    payload.mkdir(exist_ok=True)
    target = payload / executable.name
    shutil.copy2(executable, target)
    archive = destination / f"{product_name}-portable.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(target, arcname=executable.name)
    return archive
