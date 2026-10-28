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
        # SCALED mantém a resolução lógica e estica a imagem para a janela,
        # convertendo também as posições do mouse.
        try:
            self.tela = pygame.display.set_mode(
                (self.largura, self.altura), pygame.SCALED | pygame.RESIZABLE
            )
        except pygame.error:
            self.tela = pygame.display.set_mode((self.largura, self.altura))
        pygame.display.set_caption(TITULO)
        self.relogio = pygame.time.Clock()
        self.rodando = True
        self.telas = {}
        self.volume = 100
        self.brilho = 80
        self.num_bots = 2
        self.audio = Audio()
        self.audio.definir_volume(self.volume)
        self.trocar_tela("menu")

    def trocar_tela(self, nome):
        classes = {"menu": Menu, "configuracoes": Configuracoes, "gameplay": Gameplay}
        self.tela_atual = classes[nome](self)
        if nome == "gameplay":
            self.audio.tocar_partida()
        else:
            self.audio.tocar_menu()

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
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                else:
                    self.tela_atual.tratar_evento(evento)
            self.tela_atual.atualizar(dt)
            self.tela_atual.desenhar(self.tela)
            self.aplicar_brilho()
            pygame.display.flip()
        pygame.quit()
