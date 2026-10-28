"""Primitivas do estilo padrão: sombras, brilhos, painéis, texto e contornos."""
import pygame

from . import tema

_cache = {}


def _desfocado(tamanho, raio, cor, desfoque, espessura=0):
    """Retângulo arredondado desfocado, com margem para o desfoque."""
    chave = (tamanho, raio, cor, desfoque, espessura)
    if chave not in _cache:
        margem = desfoque * 2
        superficie = pygame.Surface(
            (tamanho[0] + margem * 2, tamanho[1] + margem * 2), pygame.SRCALPHA
        )
        pygame.draw.rect(
            superficie, cor, (margem, margem, *tamanho), espessura, border_radius=raio
        )
        _cache[chave] = (pygame.transform.gaussian_blur(superficie, desfoque), margem)
    return _cache[chave]


def sombra(tela, rect, raio, deslocamento=(0, 3), desfoque=4, alpha=110):
    imagem, margem = _desfocado(pygame.Rect(rect).size, raio, (0, 0, 0, alpha), desfoque)
    tela.blit(imagem, (rect[0] - margem + deslocamento[0], rect[1] - margem + deslocamento[1]))


def brilho(tela, rect, cor, raio, desfoque=6, alpha=170):
    imagem, margem = _desfocado(pygame.Rect(rect).size, raio, (*cor, alpha), desfoque, 4)
    tela.blit(imagem, (rect[0] - margem, rect[1] - margem))


def contorno_brilhante(tela, rect, cor, raio):
    brilho(tela, rect, cor, raio)
    pygame.draw.rect(tela, cor, rect, 2, border_radius=raio)


def painel(tela, rect, cor, raio=tema.RAIO_PAINEL, alpha=255, borda=None):
    rect = pygame.Rect(rect)
    if alpha >= 255:
        pygame.draw.rect(tela, cor, rect, border_radius=raio)
    else:
        superficie = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(superficie, (*cor, alpha), superficie.get_rect(), border_radius=raio)
        tela.blit(superficie, rect)
    if borda is not None:
        pygame.draw.rect(tela, borda, rect, 1, border_radius=raio)


def painel_rebaixado(tela, rect, raio=tema.RAIO_PAINEL):
    """Área afundada no feltro: escurecida, com sombra interna e um fio de luz."""
    rect = pygame.Rect(rect)
    chave = ("rebaixado", rect.size, raio)
    if chave not in _cache:
        superficie = pygame.Surface(rect.size, pygame.SRCALPHA)
        area = superficie.get_rect()
        pygame.draw.rect(superficie, (0, 0, 0, 70), area, border_radius=raio)
        interna = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(interna, (0, 0, 0, 150), area, 10, border_radius=raio)
        superficie.blit(pygame.transform.gaussian_blur(interna, 8), (0, 0))
        mascara = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), area, border_radius=raio)
        superficie.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(superficie, (255, 255, 255, 26), area, 1, border_radius=raio)
        _cache[chave] = superficie
    tela.blit(_cache[chave], rect)


def texto(tela, conteudo, fonte, cor, **ancora):
    """Escreve `conteudo` posicionado por uma âncora de Rect (center=, midleft=...)."""
    imagem = fonte.render(conteudo, True, cor)
    rect = imagem.get_rect(**ancora)
    tela.blit(imagem, rect)
    return rect


def contorno_tracejado(tela, cor, rect, traco=8, vao=6, largura=2):
    rect = pygame.Rect(rect)
    lados = (
        (rect.topleft, rect.topright),
        (rect.topright, rect.bottomright),
        (rect.bottomright, rect.bottomleft),
        (rect.bottomleft, rect.topleft),
    )
    for (x1, y1), (x2, y2) in lados:
        comprimento = max(abs(x2 - x1), abs(y2 - y1))
        dx, dy = (x2 - x1) / comprimento, (y2 - y1) / comprimento
        for inicio in range(0, comprimento, traco + vao):
            fim = min(inicio + traco, comprimento)
            pygame.draw.line(
                tela, cor, (x1 + dx * inicio, y1 + dy * inicio), (x1 + dx * fim, y1 + dy * fim), largura
            )


def limpar_cache() -> None:
    _cache.clear()
