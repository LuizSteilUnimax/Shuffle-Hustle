import math
import pygame

from . import desenho, tema
from .botao import Botao
from .carta_sprite import CartaSprite
from ..entidades.carta import Carta

# Leque decorativo de cartas acima dos botões.
CARTAS_LEQUE = (("10", "Espadas"), ("J", "Ouros"), ("A", "Copas"), ("Q", "Paus"), ("K", "Copas"))


ALTURA_BOTAO, PASSO_BOTAO, Y_BOTOES = 48, 58, 342
Y_TITULO, Y_LEQUE = 78, 222


class Menu:
    def __init__(self, jogo):
        self.jogo = jogo
        self.t = 0.0
        self.confirmando = False
        self.em_andamento = getattr(jogo, "tem_partida_em_andamento", lambda: False)()

        cx = jogo.largura // 2
        itens = [("novo", "Novo jogo"), ("tutorial", "Como jogar"), ("placar", "Placar"),
                 ("config", "Configurações"), ("sair", "Sair")]
        if self.em_andamento:
            itens.insert(0, ("continuar", "Continuar"))
        self.botoes = {
            chave: Botao(
                texto,
                (cx - 140, Y_BOTOES + i * PASSO_BOTAO, 280, ALTURA_BOTAO),
                papel="primario" if i == 0 else "secundario",
            )
            for i, (chave, texto) in enumerate(itens)
        }

        self.dialogo = pygame.Rect(0, 0, 500, 210)
        self.dialogo.center = (cx, jogo.altura // 2)
        self.confirmar_novo = Botao(
            "Novo jogo", (cx - 200, self.dialogo.bottom - 76, 190, 48), papel="primario"
        )
        self.cancelar_novo = Botao("Cancelar", (cx + 10, self.dialogo.bottom - 76, 190, 48))
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

    def _novo_jogo(self):
        nova = getattr(self.jogo, "nova_partida", None)
        if nova is not None:
            nova()
        else:
            self.jogo.trocar_tela("gameplay")

    def tratar_evento(self, evento):
        if self.confirmando:
            if self.confirmar_novo.clicado(evento):
                self._novo_jogo()
            elif self.cancelar_novo.clicado(evento) or (
                evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE
            ):
                self.confirmando = False
            return

        clicado = next((chave for chave, b in self.botoes.items() if b.clicado(evento)), None)
        if clicado == "continuar":
            self.jogo.trocar_tela("gameplay")
        elif clicado == "novo":
            if self.em_andamento:
                self.confirmando = True
            else:
                self._novo_jogo()
        elif clicado == "tutorial":
            self.jogo.trocar_tela("tutorial")
        elif clicado == "placar":
            self.jogo.trocar_tela("placar")
        elif clicado == "config":
            self.jogo.trocar_tela("configuracoes")
        elif clicado == "sair":
            self.jogo.rodando = False

    def atualizar(self, dt):
        self.t += dt

    def _desenhar_confirmacao(self, tela):
        sombra = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 165))
        tela.blit(sombra, (0, 0))
        painel = self.dialogo
        desenho.sombra(tela, painel, 20, (0, 10), desfoque=16, alpha=150)
        desenho.painel(tela, painel, tema.SUPERFICIE, raio=20, borda=tema.escurecer(tema.ACENTO, 0.3))
        desenho.texto(tela, "Começar um novo jogo?", tema.fonte("negrito", 26), tema.ACENTO,
                      midtop=(painel.centerx, painel.y + 26))
        desenho.texto(tela, "A partida em andamento será descartada.",
                      tema.fonte("regular", tema.TAMANHO_PEQUENO), tema.TEXTO_SUAVE,
                      midtop=(painel.centerx, painel.y + 72))
        self.confirmar_novo.desenhar(tela)
        self.cancelar_novo.desenhar(tela)

    def desenhar(self, tela):
        tema.desenhar_fundo(tela)
        cx = self.jogo.largura // 2

        flutuacao = math.sin(self.t * 1.6) * 4
        for imagem, (dx, dy) in self.leque:
            tela.blit(imagem, imagem.get_rect(center=(cx + dx, Y_LEQUE + dy + flutuacao)))

        fonte_titulo = tema.fonte("negrito", 72)
        desenho.texto(tela, "Mexe-Mexe", fonte_titulo, tema.escurecer(tema.FELTRO_BORDA, 0.4),
                      center=(cx + 3, Y_TITULO + 4))
        desenho.texto(tela, "Mexe-Mexe", fonte_titulo, tema.ACENTO, center=(cx, Y_TITULO))
        desenho.texto(tela, "JOGO DE CARTAS", tema.fonte("seminegrito", 14), tema.TEXTO_SUAVE,
                      center=(cx, Y_TITULO + 56))

        for botao in self.botoes.values():
            botao.desenhar(tela)
        if self.confirmando:
            self._desenhar_confirmacao(tela)
