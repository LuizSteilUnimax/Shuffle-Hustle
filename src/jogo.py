import pygame
from .audio import Audio
from .config import LARGURA, ALTURA, FPS, TITULO
from .ui.menu import Menu
from .ui.configuracoes import Configuracoes
from .ui.gameplay import Gameplay


class Jogo:
    def __init__(self):
        pygame.init()
        self.largura, self.altura = LARGURA, ALTURA
        self.tela = pygame.display.set_mode((self.largura, self.altura))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.telas = {}
        self.volume = 100
        self.brilho = 80
        self.audio = Audio()
        self.audio.definir_volume(self.volume)
        self.trocar_tela("menu")

    def trocar_tela(self, nome):
        classes = {"menu": Menu, "configuracoes": Configuracoes, "gameplay": Gameplay}
        self.tela_atual = classes[nome](self)

    def aplicar_brilho(self):
        alpha = int((100 - self.brilho) * 2.55)
        if alpha <= 0:
            return
        overlay = pygame.Surface(self.tela.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        self.tela.blit(overlay, (0, 0))

    def executar(self):
        while self.rodando:
            dt = self.relogio.tick(FPS) / 1000
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                else:
                    self.tela_atual.tratar_evento(evento)
            self.tela_atual.atualizar(dt)
            self.tela_atual.desenhar(self.tela)
            self.aplicar_brilho()
            pygame.display.flip()
        pygame.quit()
