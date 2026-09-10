from pathlib import Path
from .process_runner import find_command


def required_tool_message(tool: str, install_hint: str) -> RuntimeError:
    return RuntimeError(
        f"Required build tool '{tool}' was not found. Install it, then run TOSKINSTALLER again. "
        f"Suggested command: {install_hint}"
    )


def ensure_directory(path: str | Path) -> Path:
    result = Path(path).expanduser().resolve()
    result.mkdir(parents=True, exist_ok=True)
    return result
