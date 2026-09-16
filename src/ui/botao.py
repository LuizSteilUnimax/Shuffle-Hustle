import pygame
from ..cores import CINZA, CINZA_ESCURO, PRETO

class Botao:
    def __init__(self, texto, rect, fonte):
        self.texto = texto
        self.rect = pygame.Rect(rect)
        self.fonte = fonte

    def clicado(self, evento) -> bool:
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)

    def desenhar(self, tela) -> None:
        cor = CINZA_ESCURO if self.rect.collidepoint(pygame.mouse.get_pos()) else CINZA
        pygame.draw.rect(tela, cor, self.rect, border_radius=10)
        imagem = self.fonte.render(self.texto, True, PRETO)
        tela.blit(imagem, imagem.get_rect(center=self.rect.center))
