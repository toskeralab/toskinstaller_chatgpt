import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PartnerApp:
    name: str
    installer: str
    arguments: list[str] = field(default_factory=list)
    required: bool = False


@dataclass(slots=True)
class PackageConfig:
    schema_version: int = 1
    product_name: str = "My Application"
    version: str = "1.0.0"
    publisher: str = "ToskeraLAB ART/TECH House"
    output_format: str = "portable"
    architecture: str = "x64"
    language: str = "pt-BR"
    install_scope: str = "user"
    create_desktop_shortcut: bool = True
    create_start_menu_shortcut: bool = True
    logo: str | None = None
    license_file: str | None = None
    progress_style: str = "bar"
    theme: dict = field(default_factory=lambda: {"accent": "#3B82F6", "background": "#111827"})
    partners: list[PartnerApp] = field(default_factory=list)

    def save(self, path: str | Path) -> None:
        payload = asdict(self)
        Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "PackageConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        partners = [PartnerApp(**item) for item in data.pop("partners", [])]
        return cls(partners=partners, **data)
