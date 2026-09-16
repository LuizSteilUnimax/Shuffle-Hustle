import pygame
from .botao import Botao
from ..cores import BRANCO

class Menu:
    def __init__(self, jogo):
        self.jogo = jogo
        fonte = pygame.font.Font(None, 45)
        cx = jogo.largura // 2
        self.botoes = {
            "jogar": Botao("Jogar", (cx-150, 170, 300, 70), fonte),
            "config": Botao("Configurações", (cx-150, 260, 300, 70), fonte),
            "sair": Botao("Sair", (cx-150, 350, 300, 70), fonte),
        }

    def tratar_evento(self, evento):
        if self.botoes["jogar"].clicado(evento): self.jogo.trocar_tela("gameplay")
        elif self.botoes["config"].clicado(evento): self.jogo.trocar_tela("configuracoes")
        elif self.botoes["sair"].clicado(evento): self.jogo.rodando = False

    def atualizar(self, dt): pass

    def desenhar(self, tela):
        tela.fill(BRANCO)
        for botao in self.botoes.values(): botao.desenhar(tela)
