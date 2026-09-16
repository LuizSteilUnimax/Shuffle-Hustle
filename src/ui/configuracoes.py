import pygame
from .botao import Botao
from ..cores import BRANCO, PRETO

class Configuracoes:
    def __init__(self, jogo):
        self.jogo = jogo
        self.fonte = pygame.font.Font(None, 40)
        self.volume = 100
        self.voltar = Botao("Voltar", (jogo.largura//2-150, 430, 300, 55), self.fonte)

    def tratar_evento(self, evento):
        if self.voltar.clicado(evento): self.jogo.trocar_tela("menu")

    def atualizar(self, dt): pass

    def desenhar(self, tela):
        tela.fill(BRANCO)
        titulo = self.fonte.render(f"Configurações | Volume: {self.volume}%", True, PRETO)
        tela.blit(titulo, titulo.get_rect(center=(self.jogo.largura//2, 100)))
        self.voltar.desenhar(tela)
