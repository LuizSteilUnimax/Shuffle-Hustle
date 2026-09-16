import pygame
from .botao import Botao
from .carta_sprite import CartaSprite
from .hud import desenhar_hud
from ..cores import VERDE_MESA, BRANCO
from ..entidades.partida import Partida

class Gameplay:
    def __init__(self, jogo):
        self.jogo = jogo
        self.partida = Partida()
        self.partida.iniciar()
        fonte = pygame.font.Font(None, 30)
        self.comprar = Botao("Comprar", (20, jogo.altura-70, 140, 45), fonte)
        self.menu = Botao("Menu", (jogo.largura-140, 15, 120, 40), fonte)

    def tratar_evento(self, evento):
        if self.menu.clicado(evento): self.jogo.trocar_tela("menu")
        elif self.comprar.clicado(evento):
            self.partida.comprar()
            self.partida.proximo_turno()

    def atualizar(self, dt): pass

    def desenhar(self, tela):
        tela.fill(VERDE_MESA)
        desenhar_hud(tela, self.partida)
        self.comprar.desenhar(tela)
        self.menu.desenhar(tela)
        mao = self.partida.jogadores[0].mao
        inicio = max(180, (self.jogo.largura - (len(mao)-1)*38 - 70)//2)
        for i, carta in enumerate(mao):
            CartaSprite.desenhar(tela, carta, inicio + i*38, self.jogo.altura-125)
        aviso = pygame.font.Font(None, 25).render("Base do gameplay: compra, turno, mão e mesa", True, BRANCO)
        tela.blit(aviso, aviso.get_rect(center=(self.jogo.largura//2, self.jogo.altura//2)))
