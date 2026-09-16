from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"

def caminho_asset(*partes) -> Path:
    return ASSETS.joinpath(*partes)
