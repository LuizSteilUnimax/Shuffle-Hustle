import pygame
from .botao import Botao
from ..cores import BRANCO, PRETO


class Configuracoes:
    def __init__(self, jogo):
        self.jogo = jogo
        self.fonte = pygame.font.Font(None, 40)
        self.fonte_label = pygame.font.Font(None, 28)
        self.volume = getattr(jogo, "volume", 100)
        self.brilho = getattr(jogo, "brilho", 80)
        self.slider_ativo = None
        self.trilha_volume = pygame.Rect(jogo.largura // 2 - 180, 180, 360, 18)
        self.trilha_brilho = pygame.Rect(jogo.largura // 2 - 180, 290, 360, 18)
        self.voltar = Botao("Voltar", (jogo.largura // 2 - 150, 430, 300, 55), self.fonte)

    def _atualizar_slider(self, slider, posicao_x):
        inicio = slider.x
        valor = max(0, min(100, ((posicao_x - inicio) / max(1, slider.width)) * 100))
        return int(valor)

    def _aplicar_configuracoes(self):
        self.jogo.volume = self.volume
        self.jogo.brilho = self.brilho
        if hasattr(self.jogo, "audio") and self.jogo.audio is not None:
            self.jogo.audio.definir_volume(self.volume)

    def _selecionar_slider(self, posicao):
        if self.trilha_volume.collidepoint(posicao):
            self.slider_ativo = ("volume", self.trilha_volume)
            self.volume = self._atualizar_slider(self.trilha_volume, posicao[0])
            self._aplicar_configuracoes()
        elif self.trilha_brilho.collidepoint(posicao):
            self.slider_ativo = ("brilho", self.trilha_brilho)
            self.brilho = self._atualizar_slider(self.trilha_brilho, posicao[0])
            self._aplicar_configuracoes()

    def tratar_evento(self, evento):
        if self.voltar.clicado(evento):
            self.jogo.trocar_tela("menu")
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self._selecionar_slider(evento.pos)
        elif evento.type == pygame.MOUSEMOTION and self.slider_ativo is not None:
            nome, trilha = self.slider_ativo
            if nome == "volume":
                self.volume = self._atualizar_slider(trilha, evento.pos[0])
            elif nome == "brilho":
                self.brilho = self._atualizar_slider(trilha, evento.pos[0])
            self._aplicar_configuracoes()
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.slider_ativo = None

    def atualizar(self, dt):
        pass

    def _desenhar_slider(self, tela, trilha, valor, label):
        pygame.draw.rect(tela, (200, 200, 200), trilha, border_radius=10)
        pygame.draw.rect(tela, PRETO, trilha, 2, border_radius=10)

        knob_size = 22
        pos_x = trilha.x + (valor / 100) * trilha.width
        knob_rect = pygame.Rect(pos_x - knob_size // 2, trilha.centery - knob_size // 2, knob_size, knob_size)
        pygame.draw.circle(tela, PRETO, knob_rect.center, knob_size // 2)

        texto_label = self.fonte_label.render(f"{label}", True, PRETO)
        texto_valor = self.fonte_label.render(f"{valor}%", True, PRETO)

        tela.blit(texto_label, (trilha.x, trilha.y - 35))
        tela.blit(texto_valor, (trilha.x + trilha.width + 18, trilha.y - 8))

    def desenhar(self, tela):
        tela.fill(BRANCO)
        titulo = self.fonte.render("Configurações", True, PRETO)
        tela.blit(titulo, titulo.get_rect(center=(self.jogo.largura // 2, 80)))

        self._desenhar_slider(tela, self.trilha_volume, self.volume, "Volume")
        self._desenhar_slider(tela, self.trilha_brilho, self.brilho, "Brilho")

        self.voltar.desenhar(tela)
