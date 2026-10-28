import pytest

from src.ui import desenho, hud, tema
from src.ui.carta_sprite import CartaSprite


@pytest.fixture(autouse=True)
def limpar_caches_graficos():
    # Os testes chamam pygame.quit(), que invalida fontes e imagens em cache.
    tema.limpar_cache()
    desenho.limpar_cache()
    hud.limpar_cache()
    CartaSprite.limpar_cache()
    yield
