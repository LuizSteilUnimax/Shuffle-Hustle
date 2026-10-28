"""Cartas voando entre posições na tela.

As animações são só visuais: a lógica da partida já mudou quando um voo começa.
Enquanto voa, a carta é desenhada pelo voo e escondida no lugar de destino.
"""

DURACAO_VOO = 0.3


def suavizar(t: float) -> float:
    """Desaceleração cúbica: rápido no início, suave na chegada."""
    return 1 - (1 - t) ** 3


class Voo:
    def __init__(self, carta, origem, destino=None, duracao=DURACAO_VOO, atraso=0.0):
        """`carta` None voa como verso. `destino` None segue a posição atual da carta."""
        self.carta = carta
        self.origem = origem
        self.destino = destino
        self.duracao = duracao
        self.t = -atraso

    @property
    def iniciado(self) -> bool:
        return self.t >= 0

    def posicao(self, destino):
        p = suavizar(max(0.0, min(1.0, self.t / self.duracao)))
        return (
            round(self.origem[0] + (destino[0] - self.origem[0]) * p),
            round(self.origem[1] + (destino[1] - self.origem[1]) * p),
        )


class Animacoes:
    def __init__(self):
        self.voos = []

    @property
    def ativas(self) -> bool:
        return bool(self.voos)

    def adicionar(self, voo) -> None:
        if voo.carta is not None:
            self.cancelar(voo.carta)
        self.voos.append(voo)

    def cancelar(self, carta) -> None:
        self.voos = [voo for voo in self.voos if voo.carta is not carta]

    def voo_de(self, carta):
        return next((voo for voo in self.voos if voo.carta is carta), None)

    def atualizar(self, dt) -> None:
        for voo in self.voos:
            voo.t += dt
        self.voos = [voo for voo in self.voos if voo.t < voo.duracao]
