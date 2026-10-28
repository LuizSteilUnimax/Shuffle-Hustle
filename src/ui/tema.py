"""Tema visual: cores, fontes, medidas e imagens opcionais.

Todo o estilo do jogo sai daqui, então um novo visual começa por este arquivo.

Para trocar a arte, coloque arquivos em `assets/`:

- `assets/cards/<valor>_<naipe>.png` — frente de cada carta, por exemplo
  `A_copas.png`, `10_espadas.png`, `K_ouros.png`, `7_paus.png`;
- `assets/cards/verso.png` — verso das cartas;
- `assets/backgrounds/mesa.png` — fundo das telas;
- `assets/fonts/` — fontes listadas em ARQUIVOS_FONTE.

As imagens são redimensionadas para os tamanhos abaixo. Arquivos ausentes usam
o desenho padrão, então a arte pode ser adicionada aos poucos.
"""
import pygame

from ..util import caminho_asset


def misturar(cor_a, cor_b, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(cor_a, cor_b))


def clarear(cor, t):
    return misturar(cor, (255, 255, 255), t)


def escurecer(cor, t):
    return misturar(cor, (0, 0, 0), t)


# --- Medidas -------------------------------------------------------------

CARTA_LARGURA, CARTA_ALTURA = 75, 105
RAIO_CARTA = 7
RAIO_PAINEL = 18
RAIO_BOTAO = 12
ELEVACAO_SELECAO = 15
ELEVACAO_HOVER = 12

# --- Cores ---------------------------------------------------------------

FELTRO_CENTRO = (34, 118, 80)
FELTRO_BORDA = (9, 46, 31)

SUPERFICIE = (20, 66, 46)
TEXTO = (246, 243, 233)
TEXTO_SUAVE = (172, 202, 184)
TEXTO_INATIVO = (112, 145, 128)

ACENTO = (234, 192, 96)
COR_DESTAQUE = ACENTO
COR_DESTAQUE_BOT = (110, 200, 255)
COR_JOGO_INVALIDO = (236, 92, 80)

COR_CARTA = (251, 248, 241)
COR_CARTA_BORDA = (208, 202, 190)
COR_NAIPE_VERMELHO = (196, 38, 52)
COR_NAIPE_PRETO = (30, 30, 38)
COR_VERSO = (27, 50, 108)
COR_VERSO_DETALHE = (214, 184, 112)

BOTOES = {
    "primario": {"base": ACENTO, "hover": clarear(ACENTO, 0.2), "texto": (46, 34, 12)},
    "secundario": {"base": (40, 102, 73), "hover": (52, 122, 89), "texto": TEXTO},
}
BOTAO_INATIVO = (27, 62, 46)

# --- Tipografia ----------------------------------------------------------

ARQUIVOS_FONTE = {
    "regular": "Poppins-Regular.ttf",
    "seminegrito": "Poppins-SemiBold.ttf",
    "negrito": "Poppins-Bold.ttf",
    "indice": "BarlowCondensed-Bold.ttf",
}
# Usadas se o arquivo não existir. DejaVu Sans também é a única com os quatro
# naipes (♥♦♣♠) bem desenhados, por isso "naipe" não tem arquivo próprio.
FONTES_SISTEMA = {
    "indice": "liberationsansnarrow,dejavusanscondensed,arialnarrow",
    "naipe": "dejavusans",
}

TAMANHO_TITULO = 40
TAMANHO_TEXTO = 18
TAMANHO_BOTAO = 18
TAMANHO_PEQUENO = 14

_fontes = {}


def fonte(estilo="regular", tamanho=TAMANHO_TEXTO):
    chave = (estilo, tamanho)
    if chave not in _fontes:
        if not pygame.font.get_init():
            pygame.font.init()
        arquivo = ARQUIVOS_FONTE.get(estilo)
        caminho = caminho_asset("fonts", arquivo) if arquivo else None
        if caminho is not None and caminho.exists():
            _fontes[chave] = pygame.font.Font(str(caminho), tamanho)
        else:
            nomes = FONTES_SISTEMA.get(estilo, "dejavusans")
            _fontes[chave] = pygame.font.SysFont(nomes, tamanho, bold=estilo != "regular")
    return _fontes[chave]


# --- Imagens -------------------------------------------------------------

_imagens = {}


def _carregar(caminho, tamanho):
    chave = (caminho, tamanho)
    if chave not in _imagens:
        imagem = None
        if caminho.exists():
            try:
                imagem = pygame.image.load(str(caminho))
                if pygame.display.get_surface() is not None:
                    imagem = imagem.convert_alpha()
                imagem = pygame.transform.smoothscale(imagem, tamanho)
            except (pygame.error, ValueError):
                imagem = None
        _imagens[chave] = imagem
    return _imagens[chave]


def imagem_carta(carta):
    nome = f"{carta.valor}_{carta.naipe.lower()}.png"
    return _carregar(caminho_asset("cards", nome), (CARTA_LARGURA, CARTA_ALTURA))


def imagem_verso():
    return _carregar(caminho_asset("cards", "verso.png"), (CARTA_LARGURA, CARTA_ALTURA))


def _feltro(tamanho):
    """Gradiente radial com vinheta, gerado em baixa resolução e ampliado."""
    largura, altura = tamanho
    pequena = pygame.Surface((max(2, largura // 10), max(2, altura // 10)))
    cx, cy = pequena.get_width() / 2, pequena.get_height() / 2
    for y in range(pequena.get_height()):
        for x in range(pequena.get_width()):
            distancia = (((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2) ** 0.5 / 1.42
            pequena.set_at((x, y), misturar(FELTRO_CENTRO, FELTRO_BORDA, min(1.0, distancia ** 1.6)))
    return pygame.transform.smoothscale(pequena, tamanho)


def desenhar_fundo(tela) -> None:
    tamanho = tela.get_size()
    imagem = _carregar(caminho_asset("backgrounds", "mesa.png"), tamanho)
    if imagem is None:
        chave = ("feltro", tamanho)
        if chave not in _imagens:
            _imagens[chave] = _feltro(tamanho)
        imagem = _imagens[chave]
    tela.blit(imagem, (0, 0))


def limpar_cache() -> None:
    """Descarta fontes e imagens carregadas (necessário após pygame.quit())."""
    _fontes.clear()
    _imagens.clear()
