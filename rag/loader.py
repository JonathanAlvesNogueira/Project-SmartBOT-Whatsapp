import json
from pathlib import Path


def carregar_base(caminho: str | Path | None = None):
    if caminho is None:
        caminho = Path(__file__).resolve().parent.parent / "data" / "fitlife_knowledge.json"

    with Path(caminho).open("r", encoding="utf-8") as f:
        return json.load(f)
