import pygame
from . import persistencia
from .audio import Audio
from .config import LARGURA, ALTURA, FPS, TITULO
from .ui.menu import Menu
from .ui.configuracoes import Configuracoes
from .ui.gameplay import Gameplay
from .ui.placar import Placar
from .ui.tutorial import Tutorial


class Jogo:
    """Loop principal, troca de telas e a partida em andamento (a sessão).

    A sessão sobrevive à volta ao menu e é salva em disco, então pode ser
    continuada depois de fechar o jogo. Partidas encerradas vão para o placar.
    """

    TELAS = {"menu": Menu, "configuracoes": Configuracoes, "tutorial": Tutorial, "placar": Placar}

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
        self.volume = 100
        self.brilho = 100
        self.num_bots = 2
        self.audio = Audio()
        self.audio.definir_volume(self.volume)
        self.audio.tocar_musica()

        partida = persistencia.carregar_sessao()
        self.sessao = Gameplay(self, partida) if partida is not None else None
        self.tela_atual = None
        self.trocar_tela("menu")

    # --- Sessão --------------------------------------------------------------

    def tem_partida_em_andamento(self) -> bool:
        return self.sessao is not None and not self.sessao.partida.encerrada

    def nova_partida(self) -> None:
        self.sessao = Gameplay(self)
        self.tela_atual = self.sessao
        self.salvar_sessao()

    def continuar_partida(self) -> None:
        self.sessao.retomar()
        self.tela_atual = self.sessao

    def salvar_sessao(self) -> None:
        if self.sessao is None:
            return
        if self.sessao.partida.encerrada:
            persistencia.apagar_sessao()
        else:
            persistencia.salvar_sessao(self.sessao.partida)

    def registrar_fim(self, partida) -> None:
        persistencia.registrar_resultado(partida)
        persistencia.apagar_sessao()

    # --- Telas ---------------------------------------------------------------

    def trocar_tela(self, nome):
        if self.tela_atual is not None and self.tela_atual is self.sessao:
            self.salvar_sessao()
        if nome == "gameplay":
            if self.tem_partida_em_andamento():
                self.continuar_partida()
            else:
                self.nova_partida()
        else:
            self.tela_atual = self.TELAS[nome](self)

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
            self.audio.atualizar()
            self.tela_atual.atualizar(dt)
            self.tela_atual.desenhar(self.tela)
            self.aplicar_brilho()
            pygame.display.flip()
        self.salvar_sessao()
        pygame.quit()
