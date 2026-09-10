from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ProjectInfo:
    root: Path
    language: str
    entrypoint: Path | None = None
    build_files: list[Path] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


PYTHON_MARKERS = ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile")


def _python_entrypoint(root: Path) -> Path | None:
    candidates = [root / "main.py", root / f"{root.name}.py", root / "app.py"]
    candidates += [p for p in root.glob("*.py") if p.name not in {"setup.py"}]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def detect_project(root: str | Path) -> ProjectInfo:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")

    files = {p.name.lower(): p for p in root.iterdir() if p.is_file()}
    python_hits = [name for name in PYTHON_MARKERS if name.lower() in files]
    py_files = list(root.glob("*.py"))
    if python_hits or py_files:
        return ProjectInfo(
            root=root,
            language="python",
            entrypoint=_python_entrypoint(root),
            build_files=[files[name.lower()] for name in python_hits],
            evidence={"markers": python_hits, "python_files": [p.name for p in py_files]},
        )

    if (root / "package.json").is_file():
        return ProjectInfo(root=root, language="node", build_files=[root / "package.json"])
    if list(root.glob("*.csproj")):
        return ProjectInfo(root=root, language="dotnet", build_files=list(root.glob("*.csproj")))
    if list(root.glob("*.sln")):
        return ProjectInfo(root=root, language="dotnet", build_files=list(root.glob("*.sln")))

    raise ValueError("Unsupported or undetected project. No supported project markers were found.")
