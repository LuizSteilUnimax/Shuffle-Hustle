import pygame

from . import desenho, tema


class Botao:
    """Botão com papel visual ("primario" ou "secundario") e estados de hover,
    pressionado e inativo."""

    def __init__(self, texto, rect, fonte=None, papel="secundario"):
        self.texto = texto
        self.rect = pygame.Rect(rect)
        self.fonte = fonte or tema.fonte("seminegrito", tema.TAMANHO_BOTAO)
        self.papel = papel
        self.ativo = True

    def clicado(self, evento) -> bool:
        return (
            self.ativo
            and evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        )

    def desenhar(self, tela) -> None:
        if not self.ativo:
            pygame.draw.rect(tela, tema.BOTAO_INATIVO, self.rect, border_radius=tema.RAIO_BOTAO)
            desenho.texto(tela, self.texto, self.fonte, tema.TEXTO_INATIVO, center=self.rect.center)
            return

        cores = tema.BOTOES[self.papel]
        sobre = self.rect.collidepoint(pygame.mouse.get_pos())
        pressionado = sobre and pygame.mouse.get_pressed()[0]
        rect = self.rect.move(0, 2) if pressionado else self.rect
        if not pressionado:
            desenho.sombra(tela, rect, tema.RAIO_BOTAO, (0, 3), desfoque=4, alpha=100)

        cor = cores["hover"] if sobre else cores["base"]
        pygame.draw.rect(tela, cor, rect, border_radius=tema.RAIO_BOTAO)
        pygame.draw.rect(tela, tema.clarear(cor, 0.18), rect, 1, border_radius=tema.RAIO_BOTAO)
        desenho.texto(tela, self.texto, self.fonte, cores["texto"], center=rect.center)
