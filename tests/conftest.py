import pytest

from src.ui import desenho, hud, tema
from src.ui.carta_sprite import CartaSprite


@pytest.fixture(autouse=True)
def pasta_dados_temporaria(tmp_path, monkeypatch):
    # Partidas salvas e placar dos testes nunca tocam a pasta real do usuário.
    monkeypatch.setenv("MEXE_MEXE_DADOS", str(tmp_path / "dados"))
    return tmp_path / "dados"


@pytest.fixture(autouse=True)
def limpar_caches_graficos():
    # Os testes chamam pygame.quit(), que invalida fontes e imagens em cache.
    tema.limpar_cache()
    desenho.limpar_cache()
    hud.limpar_cache()
    CartaSprite.limpar_cache()
    yield
