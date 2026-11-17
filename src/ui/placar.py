"""Tela de placar: resumo das partidas encerradas e as mais recentes."""
from datetime import datetime

import pygame

from . import desenho, tema
from .botao import Botao
from .. import persistencia

LINHAS_VISIVEIS = 7
ALTURA_LINHA = 38

RESULTADOS = {
    "vitoria": ("Vitória", tema.ACENTO),
    "empate": ("Empate", tema.TEXTO),
    "derrota": ("Derrota", tema.COR_JOGO_INVALIDO),
}


def _data(texto):
    try:
        return datetime.fromisoformat(texto).strftime("%d/%m/%Y  %H:%M")
    except (TypeError, ValueError):
        return "-"


def _como_terminou(registro):
    if registro.get("monte_esgotado"):
        return "Monte esgotado"
    vencedores = registro.get("vencedores") or ["-"]
    humano = persistencia.humano(registro)
    if humano is not None and vencedores[0] == humano["nome"]:
        return "Você bateu"
    return f"{vencedores[0]} bateu"


class Placar:
    def __init__(self, jogo):
        self.jogo = jogo
        self.registros = persistencia.carregar_placar()
        self.resumo = persistencia.resumo(self.registros)
        self.inicio = 0  # primeira linha visível da tabela

        largura = jogo.largura
        self.tabela = pygame.Rect(140, 268, largura - 280, 88 + LINHAS_VISIVEIS * ALTURA_LINHA)
        self.voltar = Botao("Voltar", (largura // 2 - 120, self.tabela.bottom + 22, 240, 48))
        # Colunas: (título, âncora, x)
        x, d = self.tabela.x, self.tabela.right
        self.colunas = (
            ("DATA", "midleft", x + 28),
            ("OPONENTES", "midleft", x + 230),
            ("COMO TERMINOU", "midleft", x + 380),
            ("RESULTADO", "midleft", x + 580),
            ("POSIÇÃO", "center", x + 760),
            ("SEUS PONTOS", "midright", d - 28),
        )

    def tratar_evento(self, evento):
        if self.voltar.clicado(evento) or (
            evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE
        ):
            self.jogo.trocar_tela("menu")
        elif evento.type == pygame.MOUSEWHEEL:
            maximo = max(0, len(self.registros) - LINHAS_VISIVEIS)
            self.inicio = max(0, min(maximo, self.inicio - evento.y))

    def atualizar(self, dt):
        pass

    def _desenhar_resumo(self, tela):
        r = self.resumo
        blocos = (
            ("PARTIDAS", str(r["partidas"])),
            ("VITÓRIAS", str(r["vitorias"])),
            ("APROVEITAMENTO", f"{r['aproveitamento']}%"),
            ("MAIOR SEQUÊNCIA", f"{r['maior_sequencia']} vitória" + ("" if r["maior_sequencia"] == 1 else "s")),
        )
        espaco = 20
        largura = (self.tabela.width - espaco * (len(blocos) - 1)) // len(blocos)
        for i, (rotulo, valor) in enumerate(blocos):
            rect = pygame.Rect(self.tabela.x + i * (largura + espaco), 112, largura, 124)
            desenho.painel(tela, rect, tema.SUPERFICIE, raio=16, alpha=225,
                           borda=tema.clarear(tema.SUPERFICIE, 0.12))
            desenho.texto(tela, rotulo, tema.fonte("seminegrito", 12), tema.TEXTO_SUAVE,
                          midtop=(rect.centerx, rect.y + 22))
            cor = tema.ACENTO if i == 0 or r["partidas"] else tema.TEXTO_INATIVO
            desenho.texto(tela, valor, tema.fonte("negrito", 36), cor,
                          midtop=(rect.centerx, rect.y + 46))

    def _desenhar_tabela(self, tela):
        desenho.painel_rebaixado(tela, self.tabela)
        cabecalho = tema.fonte("seminegrito", 12)
        y = self.tabela.y + 30
        for titulo, ancora, x in self.colunas:
            desenho.texto(tela, titulo, cabecalho, tema.TEXTO_INATIVO, **{ancora: (x, y)})

        if not self.registros:
            desenho.texto(tela, "Nenhuma partida encerrada ainda.", tema.fonte("seminegrito", 18),
                          tema.TEXTO_SUAVE, center=(self.tabela.centerx, self.tabela.centery))
            desenho.texto(tela, "Termine uma partida para ela aparecer aqui.",
                          tema.fonte("regular", tema.TAMANHO_PEQUENO), tema.TEXTO_INATIVO,
                          center=(self.tabela.centerx, self.tabela.centery + 30))
            return

        fonte = tema.fonte("regular", 16)
        visiveis = self.registros[self.inicio:self.inicio + LINHAS_VISIVEIS]
        for i, registro in enumerate(visiveis):
            y = self.tabela.y + 60 + i * ALTURA_LINHA + ALTURA_LINHA // 2
            if i % 2 == 0:
                faixa = pygame.Rect(self.tabela.x + 12, y - ALTURA_LINHA // 2, self.tabela.width - 24, ALTURA_LINHA)
                desenho.painel(tela, faixa, (255, 255, 255), raio=8, alpha=10)

            humano = persistencia.humano(registro) or {"pontos": 0, "cartas": 0}
            texto_resultado, cor_resultado = RESULTADOS[persistencia.resultado_humano(registro)]
            bots = len(registro["jogadores"]) - 1
            valores = (
                (_data(registro.get("data")), tema.TEXTO_SUAVE),
                (f"{bots} bot" + ("" if bots == 1 else "s"), tema.TEXTO),
                (_como_terminou(registro), tema.TEXTO),
                (texto_resultado, cor_resultado),
                (f"{persistencia.colocacao(registro)}º de {len(registro['jogadores'])}", tema.TEXTO),
                (f"{humano['pontos']} pts", tema.TEXTO),
            )
            for (texto, cor), (_, ancora, x) in zip(valores, self.colunas):
                desenho.texto(tela, texto, fonte, cor, **{ancora: (x, y)})

        if len(self.registros) > LINHAS_VISIVEIS:
            fim = self.inicio + len(visiveis)
            desenho.texto(tela, f"{self.inicio + 1}–{fim} de {len(self.registros)}  ·  role para ver mais",
                          tema.fonte("regular", 12), tema.TEXTO_INATIVO,
                          midbottom=(self.tabela.centerx, self.tabela.bottom - 8))

    def desenhar(self, tela):
        tema.desenhar_fundo(tela)
        desenho.texto(tela, "Placar", tema.fonte("negrito", tema.TAMANHO_TITULO), tema.ACENTO,
                      center=(self.jogo.largura // 2, 60))
        self._desenhar_resumo(tela)
        self._desenhar_tabela(tela)
        self.voltar.desenhar(tela)
