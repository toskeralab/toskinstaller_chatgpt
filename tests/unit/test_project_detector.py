import pytest
from toskinstaller.core.project_detector import detect_project


def test_detect_python_project(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / "main.py").write_text("print('ok')\n")
    info = detect_project(tmp_path)
    assert info.language == "python"
    assert info.entrypoint.name == "main.py"


def test_reject_unknown_project(tmp_path):
    with pytest.raises(ValueError):
        detect_project(tmp_path)
