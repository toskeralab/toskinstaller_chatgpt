from pathlib import Path

from toskinstaller.packaging import get_backend


def test_portable_backend_is_available(tmp_path):
    backend = get_backend("portable")
    executable = tmp_path / "demo.exe"
    executable.write_bytes(b"MZ")

    artifact = backend.package(executable, tmp_path / "out", "Demo")

    assert artifact.success is True
    assert artifact.path is not None
    assert artifact.path.suffix == ".zip"
    assert artifact.path.is_file()


def test_exe_backend_reports_install_engine_guidance(tmp_path):
    messages = []
    backend = get_backend("exe", messages.append)
    artifact = backend.package(Path("demo.exe"), tmp_path / "out", "Demo")

    assert artifact.success is False
    assert artifact.path is None
    assert "Inno Setup or NSIS" in artifact.message
    assert messages == [artifact.message]


def test_msi_backend_reports_wix_guidance(tmp_path):
    backend = get_backend("msi")
    artifact = backend.package(Path("demo.exe"), tmp_path / "out", "Demo")

    assert artifact.success is False
    assert artifact.path is None
    assert "WiX Toolset" in artifact.message


def test_unknown_backend_is_rejected():
    try:
        get_backend("unknown")
    except ValueError as exc:
        assert "Unknown packaging format" in str(exc)
    else:
        raise AssertionError("unknown packaging format should fail")
