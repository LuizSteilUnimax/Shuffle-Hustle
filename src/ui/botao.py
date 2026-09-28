import pygame
from ..cores import VERDE_MESA, PRETO, BRANCO


class Botao:
    def __init__(self, texto, rect, fonte):
        self.texto = texto
        self.rect = pygame.Rect(rect)
        self.fonte = fonte

        r, g, b = VERDE_MESA
        # lighter base and slightly darker hover variant
        self.base = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
        self.hover = (max(0, r - 10), max(0, g - 20), max(0, b - 10))
        self.text_color = BRANCO

    def clicado(self, evento) -> bool:
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)

    def desenhar(self, tela) -> None:
        pos = pygame.mouse.get_pos()
        cor = self.hover if self.rect.collidepoint(pos) else self.base
        pygame.draw.rect(tela, cor, self.rect, border_radius=10)
        pygame.draw.rect(tela, PRETO, self.rect, 2, border_radius=10)
        imagem = self.fonte.render(self.texto, True, self.text_color)
        tela.blit(imagem, imagem.get_rect(center=self.rect.center))
