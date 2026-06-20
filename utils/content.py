from pathlib import Path
import yaml

CONTENT_FILE = Path(__file__).parent.parent / "content" / "site.yaml"


def load() -> dict:
    if not CONTENT_FILE.exists():
        return {}
    with open(CONTENT_FILE) as f:
        return yaml.safe_load(f) or {}


def save(data: dict) -> None:
    CONTENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONTENT_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
