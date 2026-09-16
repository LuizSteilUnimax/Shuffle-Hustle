import pygame
from ..cores import BRANCO, PRETO, VERMELHO

class CartaSprite:
    LARGURA, ALTURA = 70, 100

    @staticmethod
    def desenhar(tela, carta, x, y, selecionada=False):
        rect = pygame.Rect(x, y - (12 if selecionada else 0), CartaSprite.LARGURA, CartaSprite.ALTURA)
        pygame.draw.rect(tela, BRANCO, rect, border_radius=7)
        pygame.draw.rect(tela, PRETO, rect, 2, border_radius=7)
        cor = VERMELHO if carta.naipe in ("Copas", "Ouros") else PRETO
        texto = pygame.font.Font(None, 24).render("JK" if carta.coringa else carta.valor, True, cor)
        tela.blit(texto, (rect.x + 7, rect.y + 7))
        return rect
