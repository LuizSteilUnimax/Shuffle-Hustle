import math
import pygame

from . import desenho, tema
from .botao import Botao
from .carta_sprite import CartaSprite
from ..entidades.carta import Carta

# Leque decorativo de cartas acima dos botões.
CARTAS_LEQUE = (("10", "Espadas"), ("J", "Ouros"), ("A", "Copas"), ("Q", "Paus"), ("K", "Copas"))


class Menu:
    def __init__(self, jogo):
        self.jogo = jogo
        self.t = 0.0

        cx = jogo.largura // 2
        self.botoes = {
            "jogar": Botao("Jogar", (cx - 140, 400, 280, 56), papel="primario"),
            "config": Botao("Configurações", (cx - 140, 470, 280, 56)),
            "sair": Botao("Sair", (cx - 140, 540, 280, 56)),
        }
        self.leque = self._criar_leque()

    def _criar_leque(self):
        """Cartas giradas em leque; cada uma já leva a própria sombra."""
        cartas = []
        margem = 14
        for i, (valor, naipe) in enumerate(CARTAS_LEQUE):
            angulo = (i - 2) * 13
            base = pygame.Surface(
                (CartaSprite.LARGURA + margem * 2, CartaSprite.ALTURA + margem * 2), pygame.SRCALPHA
            )
            rect = pygame.Rect(margem, margem, CartaSprite.LARGURA, CartaSprite.ALTURA)
            desenho.sombra(base, rect, tema.RAIO_CARTA, (2, 5), desfoque=6, alpha=110)
            base.blit(CartaSprite.superficie(Carta(valor, naipe)), rect)
            girada = pygame.transform.rotozoom(base, -angulo, 1.0)
            raio = 280
            centro = (
                math.sin(math.radians(angulo)) * raio,
                -math.cos(math.radians(angulo)) * raio + raio,
            )
            cartas.append((girada, centro))
        return cartas

    def tratar_evento(self, evento):
        if self.botoes["jogar"].clicado(evento):
            self.jogo.trocar_tela("gameplay")
        elif self.botoes["config"].clicado(evento):
            self.jogo.trocar_tela("configuracoes")
        elif self.botoes["sair"].clicado(evento):
            self.jogo.rodando = False

    def atualizar(self, dt):
        self.t += dt

    def desenhar(self, tela):
        tema.desenhar_fundo(tela)
        cx = self.jogo.largura // 2

        flutuacao = math.sin(self.t * 1.6) * 4
        for imagem, (dx, dy) in self.leque:
            tela.blit(imagem, imagem.get_rect(center=(cx + dx, 262 + dy + flutuacao)))

        fonte_titulo = tema.fonte("negrito", 72)
        desenho.texto(tela, "Mexe-Mexe", fonte_titulo, tema.escurecer(tema.FELTRO_BORDA, 0.4),
                      center=(cx + 3, 92 + 4))
        desenho.texto(tela, "Mexe-Mexe", fonte_titulo, tema.ACENTO, center=(cx, 92))
        desenho.texto(tela, "JOGO DE CARTAS", tema.fonte("seminegrito", 14), tema.TEXTO_SUAVE,
                      center=(cx, 148))

        for botao in self.botoes.values():
            botao.desenhar(tela)
