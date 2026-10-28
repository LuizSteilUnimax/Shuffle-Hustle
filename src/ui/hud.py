import math

import pygame

from . import desenho, tema
from .carta_sprite import CartaSprite

LARGURA_ASSENTO, ALTURA_ASSENTO = 196, 56
TAMANHO_MINIATURA = (22, 31)
MAX_MINIATURAS = 5

_leques = {}


def cartas(quantidade: int) -> str:
    return f"{quantidade} carta" if quantidade == 1 else f"{quantidade} cartas"


def rects_assentos(partida):
    """Um assento por jogador, lado a lado no topo da tela."""
    return [
        pygame.Rect(20 + i * (LARGURA_ASSENTO + 12), 10, LARGURA_ASSENTO, ALTURA_ASSENTO)
        for i in range(len(partida.jogadores))
    ]


def _leque(quantidade):
    """Miniaturas de versos abertas em leque, uma para cada carta (até 5)."""
    quantidade = min(quantidade, MAX_MINIATURAS)
    if quantidade not in _leques:
        superficie = pygame.Surface((64, 48), pygame.SRCALPHA)
        verso = pygame.transform.smoothscale(CartaSprite.superficie_verso(), TAMANHO_MINIATURA)
        for i in range(quantidade):
            angulo = (i - (quantidade - 1) / 2) * 14
            girado = pygame.transform.rotozoom(verso, -angulo, 1.0)
            centro = (32 + math.sin(math.radians(angulo)) * 30, 50 - math.cos(math.radians(angulo)) * 30)
            superficie.blit(girado, girado.get_rect(center=centro))
        _leques[quantidade] = superficie
    return _leques[quantidade]


def limpar_cache() -> None:
    _leques.clear()


def desenhar_assentos(tela, partida, tempo):
    """Assento de cada jogador: leque de cartas, nome e quantidade.

    O assento de quem joga tem um contorno dourado que pulsa devagar.
    """
    for jogador, rect in zip(partida.jogadores, rects_assentos(partida)):
        da_vez = jogador is partida.jogador_atual and not partida.encerrada
        desenho.painel(tela, rect, tema.SUPERFICIE, raio=14, alpha=225)
        if da_vez:
            # Poucos níveis de intensidade para aproveitar o cache de brilhos.
            nivel = round((1 + math.sin(tempo * 3.2)) * 2)
            desenho.brilho(tela, rect, tema.ACENTO, 14, alpha=80 + nivel * 35)
            pygame.draw.rect(tela, tema.ACENTO, rect, 2, border_radius=14)
        else:
            pygame.draw.rect(tela, tema.clarear(tema.SUPERFICIE, 0.12), rect, 1, border_radius=14)

        if jogador.mao:
            tela.blit(_leque(len(jogador.mao)), (rect.x + 6, rect.y + 4))
        cor_nome = tema.ACENTO if da_vez else tema.TEXTO
        desenho.texto(tela, jogador.nome, tema.fonte("seminegrito", 15), cor_nome,
                      bottomleft=(rect.x + 78, rect.centery + 3))
        desenho.texto(tela, cartas(len(jogador.mao)), tema.fonte("regular", 13), tema.TEXTO_SUAVE,
                      topleft=(rect.x + 78, rect.centery + 1))
