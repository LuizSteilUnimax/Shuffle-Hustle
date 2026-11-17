import pygame

from . import desenho, tema
from .botao import Botao


class Configuracoes:
    def __init__(self, jogo):
        self.jogo = jogo
        self.volume = getattr(jogo, "volume", 100)
        self.brilho = getattr(jogo, "brilho", 100)
        self.num_bots = getattr(jogo, "num_bots", 2)
        self.slider_ativo = None

        cx = jogo.largura // 2
        self.painel = pygame.Rect(cx - 260, 160, 520, 420)
        self.trilha_volume = pygame.Rect(cx - 200, 238, 340, 18)
        self.trilha_brilho = pygame.Rect(cx - 200, 324, 340, 18)
        self.botoes_bots = {
            quantidade: Botao(str(quantidade), (cx - 200 + i * 84, 412, 72, 44))
            for i, quantidade in enumerate((1, 2, 3))
        }
        self._marcar_bots()
        self.voltar = Botao("Voltar", (cx - 120, 498, 240, 52))

    def _marcar_bots(self):
        for quantidade, botao in self.botoes_bots.items():
            botao.papel = "primario" if quantidade == self.num_bots else "secundario"

    def _atualizar_slider(self, slider, posicao_x):
        inicio = slider.x
        valor = max(0, min(100, ((posicao_x - inicio) / max(1, slider.width)) * 100))
        return int(valor)

    def _aplicar_configuracoes(self):
        self.jogo.volume = self.volume
        self.jogo.brilho = self.brilho
        self.jogo.num_bots = self.num_bots
        audio = getattr(self.jogo, "audio", None)
        if audio is not None:
            audio.definir_volume(self.volume)

    def _selecionar_slider(self, posicao):
        for nome, trilha in (("volume", self.trilha_volume), ("brilho", self.trilha_brilho)):
            if trilha.collidepoint(posicao):
                self.slider_ativo = (nome, trilha)
                setattr(self, nome, self._atualizar_slider(trilha, posicao[0]))
                self._aplicar_configuracoes()
                return

    def tratar_evento(self, evento):
        if self.voltar.clicado(evento):
            self.jogo.trocar_tela("menu")
            return
        for quantidade, botao in self.botoes_bots.items():
            if botao.clicado(evento):
                self.num_bots = quantidade
                self._marcar_bots()
                self._aplicar_configuracoes()
                return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self._selecionar_slider(evento.pos)
        elif evento.type == pygame.MOUSEMOTION and self.slider_ativo is not None:
            nome, trilha = self.slider_ativo
            setattr(self, nome, self._atualizar_slider(trilha, evento.pos[0]))
            self._aplicar_configuracoes()
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.slider_ativo = None

    def atualizar(self, dt):
        pass

    def _rotulo(self, tela, texto, y):
        desenho.texto(tela, texto, tema.fonte("seminegrito", 13), tema.TEXTO_SUAVE,
                      topleft=(self.trilha_brilho.x, y))

    def _desenhar_slider(self, tela, trilha, valor):
        faixa = pygame.Rect(trilha.x, trilha.centery - 4, trilha.width, 8)
        preenchida = pygame.Rect(faixa.x, faixa.y, round(faixa.width * valor / 100), faixa.height)
        pygame.draw.rect(tela, tema.escurecer(tema.SUPERFICIE, 0.3), faixa, border_radius=4)
        pygame.draw.rect(tela, tema.ACENTO, preenchida, border_radius=4)

        centro = (preenchida.right, faixa.centery)
        desenho.sombra(tela, (centro[0] - 11, centro[1] - 11, 22, 22), 11, (0, 2), desfoque=3)
        pygame.draw.circle(tela, tema.COR_CARTA, centro, 11)
        desenho.texto(tela, f"{valor}%", tema.fonte("seminegrito", 16), tema.TEXTO,
                      midleft=(trilha.right + 20, trilha.centery))

    def desenhar(self, tela):
        tema.desenhar_fundo(tela)
        cx = self.jogo.largura // 2
        desenho.texto(tela, "Configurações", tema.fonte("negrito", tema.TAMANHO_TITULO), tema.ACENTO,
                      center=(cx, 100))
        desenho.painel_rebaixado(tela, self.painel)

        self._rotulo(tela, "VOLUME", 200)
        self._desenhar_slider(tela, self.trilha_volume, self.volume)

        self._rotulo(tela, "BRILHO", 286)
        self._desenhar_slider(tela, self.trilha_brilho, self.brilho)

        self._rotulo(tela, "OPONENTES (BOTS)", 376)
        for botao in self.botoes_bots.values():
            botao.desenhar(tela)
        if getattr(self.jogo, "tem_partida_em_andamento", lambda: False)():
            desenho.texto(tela, "Vale a partir da próxima partida.", tema.fonte("regular", 13),
                          tema.TEXTO_INATIVO, midleft=(self.botoes_bots[3].rect.right + 20,
                                                       self.botoes_bots[3].rect.centery))

        self.voltar.desenhar(tela)
