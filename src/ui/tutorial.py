"""Tela "Como jogar": as regras em páginas, cada uma com exemplos desenhados
com as próprias cartas do jogo."""
import pygame

from . import desenho, tema
from .botao import Botao
from .carta_sprite import CartaSprite
from ..entidades.carta import Carta
from ..regras.validacao import ordenar_jogo, validar_jogo

NAIPES = {"c": "Copas", "o": "Ouros", "p": "Paus", "e": "Espadas"}
PASSO_GRUPO = 30


def cartas(texto):
    """"7c 7p 8e" -> cartas; a última letra de cada item é o naipe."""
    return [Carta(item[:-1], NAIPES[item[-1]]) for item in texto.split()]


# --- Demonstrações ---------------------------------------------------------
# Cada uma recebe a tela e o retângulo da área de exemplos.

def _grupo(tela, lista, x, y, ordenar=True, destaques=(), legenda=None, valido=None):
    """Um jogo da mesa como no gameplay, com contorno e legenda opcionais."""
    if ordenar:
        lista = ordenar_jogo(lista)
    largura = CartaSprite.LARGURA + PASSO_GRUPO * (len(lista) - 1)
    rect = pygame.Rect(x, y, largura, CartaSprite.ALTURA).inflate(12, 12)
    desenho.painel(tela, rect, (255, 255, 255), raio=10, alpha=14)
    if valido is None:
        valido = validar_jogo(lista)
    cor = tema.COR_JOGO_VALIDO if valido else tema.COR_JOGO_INVALIDO
    if not valido:
        desenho.contorno_brilhante(tela, rect, cor, 10)
    for i, carta in enumerate(lista):
        destaque = tema.COR_DESTAQUE if any(carta is d for d in destaques) else None
        CartaSprite.desenhar(tela, carta, x + i * PASSO_GRUPO, y, destaque=destaque)
    if legenda is not None:
        marca = "VÁLIDO" if valido else "INVÁLIDO"
        desenho.texto(tela, marca, tema.fonte("seminegrito", 12), cor,
                      topleft=(rect.x + 4, rect.bottom + 8))
        desenho.texto(tela, legenda, tema.fonte("regular", 13), tema.TEXTO_SUAVE,
                      topleft=(rect.x + 4, rect.bottom + 26))
    return rect


def _rotulo(tela, texto, **ancora):
    desenho.texto(tela, texto, tema.fonte("seminegrito", 12), tema.TEXTO_INATIVO, **ancora)


def demo_objetivo(tela, area):
    x_monte, y = area.x + 30, area.y + 120
    for camada in range(3, -1, -1):
        CartaSprite.desenhar_verso(tela, x_monte, y - camada * 2)
    _rotulo(tela, "MONTE", midtop=(x_monte + CartaSprite.LARGURA // 2, y + CartaSprite.ALTURA + 12))

    mao = cartas("Ac 9c Qc Kc 2e Je 5o 4p 6p")
    passo = 52
    x = area.right - 30 - CartaSprite.LARGURA - passo * (len(mao) - 1)
    for i, carta in enumerate(mao):
        CartaSprite.desenhar(tela, carta, x + i * passo, y)
    centro = x + (passo * (len(mao) - 1) + CartaSprite.LARGURA) // 2
    _rotulo(tela, "SUA MÃO: 9 CARTAS", midtop=(centro, y + CartaSprite.ALTURA + 12))

    desenho.texto(tela, "104 cartas  ·  2 baralhos  ·  sem coringas", tema.fonte("seminegrito", 16),
                  tema.ACENTO, center=(area.centerx, area.y + 330))


def demo_trincas(tela, area):
    x1, x2 = area.x + 40, area.centerx + 30
    y1, y2 = area.y + 40, area.y + 240
    _grupo(tela, cartas("7c 7p 7e"), x1, y1, legenda="Três cartas de mesmo valor")
    _grupo(tela, cartas("Ko Ko Ke Kp"), x2, y1, legenda="Naipes podem se repetir")
    _grupo(tela, cartas("7c 7p 8e"), x1, y2, legenda="Valores diferentes")
    _grupo(tela, cartas("9c 9p"), x2, y2, legenda="Precisa de pelo menos três")


def demo_sequencias(tela, area):
    xs = [area.x + 20 + coluna * 228 for coluna in range(3)]
    y1, y2 = area.y + 40, area.y + 240
    _grupo(tela, cartas("4e 5e 6e 7e"), xs[0], y1, legenda="Seguidas e do mesmo naipe")
    _grupo(tela, cartas("Ac 2c 3c"), xs[1], y1, legenda="Ás baixo: A, 2, 3")
    _grupo(tela, cartas("Qo Ko Ao"), xs[2], y1, legenda="Ás alto: Q, K, A")
    _grupo(tela, cartas("4e 5c 6e"), xs[0], y2, ordenar=False, legenda="Naipes diferentes")
    _grupo(tela, cartas("Kp Ap 2p"), xs[1], y2, ordenar=False, legenda="Não dá a volta")
    _grupo(tela, cartas("8o 9o Jo"), xs[2], y2, legenda="Falta o 10")


def demo_mesa(tela, area):
    _rotulo(tela, "ANTES", topleft=(area.x + 40, area.y + 10))
    mesa = cartas("3c 4c 5c 6c 7c")
    da_mao = cartas("5c")[0]
    _grupo(tela, mesa, area.x + 40, area.y + 40)
    x_mao = area.x + 360
    CartaSprite.desenhar(tela, da_mao, x_mao, area.y + 40)
    _rotulo(tela, "NA SUA MÃO", midtop=(x_mao + CartaSprite.LARGURA // 2, area.y + 158))

    seta_x, seta_y = area.x + 160, area.y + 200
    pygame.draw.line(tela, tema.ACENTO, (seta_x, seta_y), (seta_x, seta_y + 40), 3)
    pygame.draw.polygon(tela, tema.ACENTO, [(seta_x - 9, seta_y + 34), (seta_x + 9, seta_y + 34),
                                            (seta_x, seta_y + 48)])
    desenho.texto(tela, "Divida a sequência e use o 5 da mão", tema.fonte("regular", 14),
                  tema.TEXTO_SUAVE, midleft=(seta_x + 24, seta_y + 24))

    _rotulo(tela, "DEPOIS", topleft=(area.x + 40, area.y + 262))
    y = area.y + 292
    primeiro = _grupo(tela, [*mesa[:2], da_mao], area.x + 40, y, destaques=[da_mao])
    _grupo(tela, mesa[2:], primeiro.right + 30, y)
    desenho.texto(tela, "Dourado = carta que saiu da sua mão neste turno", tema.fonte("regular", 13),
                  tema.ACENTO, topleft=(area.x + 40, y + CartaSprite.ALTURA + 20))


def demo_turno(tela, area):
    _rotulo(tela, "BOTÕES DO TURNO", topleft=(area.x + 40, area.y + 10))
    x, y = area.x + 40, area.y + 40
    for texto, largura, papel, explicacao in (
        ("Comprar", 130, "secundario", "Pega uma carta e passa a vez"),
        ("Desfazer", 130, "secundario", "Volta ao início do turno"),
        ("Finalizar jogada", 190, "primario", "Confirma o que você baixou"),
    ):
        botao = Botao(texto, (x, y, largura, 40), papel=papel)
        botao.desenhar(tela)
        desenho.texto_quebrado(tela, explicacao, tema.fonte("regular", 13), tema.TEXTO_SUAVE,
                               (x, y + 52), largura)
        x += largura + 16

    _rotulo(tela, "SÓ DÁ PARA FINALIZAR COM A MESA TODA VÁLIDA", topleft=(area.x + 40, area.y + 170))
    y = area.y + 205
    _grupo(tela, cartas("8p 9p 10p"), area.x + 40, y, legenda="Pode finalizar")
    _grupo(tela, cartas("8p 9p"), area.centerx + 30, y, legenda="Contorno vermelho: corrija")


def demo_fim(tela, area):
    linhas = (
        ("Você", cartas("2e 5o 9p")),
        ("Bot 1", cartas("Ac Ke")),
    )
    fonte_nome = tema.fonte("seminegrito", 16)
    fonte_pontos = tema.fonte("seminegrito", 13)
    totais = [sum(c.pontos for c in mao) for _, mao in linhas]
    for indice, ((nome, mao), total) in enumerate(zip(linhas, totais)):
        y = area.y + 20 + indice * 190
        venceu = total == min(totais)
        cor = tema.ACENTO if venceu else tema.TEXTO
        desenho.texto(tela, nome, fonte_nome, cor, topleft=(area.x + 40, y))
        x = area.x + 40
        for carta in mao:
            CartaSprite.desenhar(tela, carta, x, y + 30)
            desenho.texto(tela, f"{carta.pontos} pts", fonte_pontos, tema.TEXTO_SUAVE,
                          midtop=(x + CartaSprite.LARGURA // 2, y + 30 + CartaSprite.ALTURA + 8))
            x += CartaSprite.LARGURA + 14
        resultado = f"= {total} pontos" + ("  ·  vence!" if venceu else "")
        desenho.texto(tela, resultado, tema.fonte("negrito", 22), cor,
                      midleft=(x + 16, y + 30 + CartaSprite.ALTURA // 2))


PAGINAS = (
    ("Objetivo", (
        "Seja o primeiro a ficar sem cartas na mão.",
        "São usados dois baralhos comuns (104 cartas), sem coringas.",
        "Você joga contra 1 a 3 bots; escolha quantos em Configurações.",
        "Cada jogador recebe 9 cartas. O restante forma o monte de compra.",
    ), demo_objetivo),
    ("Trincas", (
        "Uma trinca tem três ou mais cartas do mesmo valor.",
        "Os naipes podem se repetir: com dois baralhos, cada carta existe em dobro.",
    ), demo_trincas),
    ("Sequências", (
        "Uma sequência tem três ou mais cartas seguidas, todas do mesmo naipe.",
        "O ás pode ser baixo (A, 2, 3) ou alto (Q, K, A).",
        "A sequência não dá a volta: K, A, 2 não vale.",
    ), demo_sequencias),
    ("Mexa na mesa", (
        "No seu turno, a mesa inteira é sua área de trabalho.",
        "Arraste cartas da mão para um jogo da mesa ou para Novo jogo.",
        "Mova cartas entre jogos à vontade: divida sequências, junte cartas e monte jogos novos.",
        "Cartas que você baixou neste turno podem voltar para a mão. As que já estavam na mesa, não.",
    ), demo_mesa),
    ("Finalize ou compre", (
        "Para finalizar, baixe ao menos uma carta da mão e deixe todos os jogos da mesa válidos.",
        "Se não puder baixar nada, use Comprar: você recebe uma carta e a vez passa.",
        "Depois de baixar uma carta não dá mais para comprar; use Desfazer para recomeçar o turno.",
    ), demo_turno),
    ("Fim da partida", (
        "Vence quem finalizar uma jogada sem cartas na mão.",
        "Se a última carta do monte for comprada, a partida acaba e vence quem tiver menos pontos na mão. Empates são divididos.",
        "Pontos: cartas de 2 a 10 valem o próprio número; J vale 11, Q vale 12, K vale 13 e A vale 14.",
        "Cada partida encerrada vai para o Placar, no menu.",
    ), demo_fim),
)


class Tutorial:
    def __init__(self, jogo):
        self.jogo = jogo
        self.pagina = 0
        largura, altura = jogo.largura, jogo.altura
        self.painel = pygame.Rect(40, 104, largura - 80, altura - 196)
        self.area_texto = pygame.Rect(self.painel.x + 44, self.painel.y + 40, 470, self.painel.height - 80)
        self.area_demo = pygame.Rect(self.area_texto.right + 40, self.painel.y + 24,
                                     self.painel.right - self.area_texto.right - 70, self.painel.height - 48)
        y = self.painel.bottom + 20
        self.anterior = Botao("Anterior", (self.painel.x, y, 170, 48))
        self.proxima = Botao("Próxima", (self.painel.right - 170, y, 170, 48), papel="primario")
        self.menu = Botao("Menu", (largura - 120, 30, 100, 36))
        self._atualizar_botoes()

    def _atualizar_botoes(self):
        self.anterior.ativo = self.pagina > 0
        self.proxima.texto = "Jogar" if self.pagina == len(PAGINAS) - 1 else "Próxima"

    def _ir_para(self, pagina):
        self.pagina = max(0, min(len(PAGINAS) - 1, pagina))
        self._atualizar_botoes()

    def tratar_evento(self, evento):
        if self.menu.clicado(evento) or (
            evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE
        ):
            self.jogo.trocar_tela("menu")
        elif self.anterior.clicado(evento) or (
            evento.type == pygame.KEYDOWN and evento.key == pygame.K_LEFT
        ):
            self._ir_para(self.pagina - 1)
        elif self.proxima.clicado(evento):
            if self.pagina == len(PAGINAS) - 1:
                self.jogo.trocar_tela("gameplay")
            else:
                self._ir_para(self.pagina + 1)
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_RIGHT:
            self._ir_para(self.pagina + 1)

    def atualizar(self, dt):
        pass

    def _desenhar_indicador(self, tela):
        """Um ponto por página; o da página atual é alongado e dourado."""
        cx, y = self.painel.centerx, self.anterior.rect.centery
        larguras = [26 if i == self.pagina else 10 for i in range(len(PAGINAS))]
        x = cx - (sum(larguras) + 10 * (len(larguras) - 1)) // 2
        for i, largura in enumerate(larguras):
            cor = tema.ACENTO if i == self.pagina else tema.TEXTO_INATIVO
            pygame.draw.rect(tela, cor, (x, y - 5, largura, 10), border_radius=5)
            x += largura + 10

    def desenhar(self, tela):
        tema.desenhar_fundo(tela)
        desenho.texto(tela, "Como jogar", tema.fonte("negrito", tema.TAMANHO_TITULO), tema.ACENTO,
                      center=(self.jogo.largura // 2, 52))
        self.menu.desenhar(tela)
        desenho.painel_rebaixado(tela, self.painel)

        titulo, paragrafos, demo = PAGINAS[self.pagina]
        area = self.area_texto
        desenho.texto(tela, f"{self.pagina + 1} DE {len(PAGINAS)}", tema.fonte("seminegrito", 13),
                      tema.TEXTO_INATIVO, topleft=area.topleft)
        desenho.texto(tela, titulo, tema.fonte("negrito", 30), tema.ACENTO,
                      topleft=(area.x, area.y + 22))
        y = area.y + 84
        fonte = tema.fonte("regular", 17)
        for paragrafo in paragrafos:
            pygame.draw.circle(tela, tema.ACENTO, (area.x + 5, y + fonte.get_linesize() // 2 + 1), 4)
            y = desenho.texto_quebrado(tela, paragrafo, fonte, tema.TEXTO, (area.x + 22, y),
                                       area.width - 22) + 12

        pygame.draw.line(tela, tema.misturar(tema.FELTRO_BORDA, tema.TEXTO, 0.15),(self.area_demo.x - 20, self.painel.y + 30),
                         (self.area_demo.x - 20, self.painel.bottom - 30))
        demo(tela, self.area_demo)

        self.anterior.desenhar(tela)
        self.proxima.desenhar(tela)
        self._desenhar_indicador(tela)
