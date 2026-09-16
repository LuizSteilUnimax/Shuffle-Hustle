from .baralho import Baralho
from .jogador import Jogador
from ..mundo.mesa import Mesa

class Partida:
    def __init__(self, nomes=("Jogador 1", "Jogador 2"), cartas_iniciais=11):
        self.baralho = Baralho()
        self.mesa = Mesa()
        self.jogadores = [Jogador(nome) for nome in nomes]
        self.indice_turno = 0
        self.vencedor = None
        self.cartas_iniciais = cartas_iniciais

    @property
    def jogador_atual(self):
        return self.jogadores[self.indice_turno]

    def iniciar(self) -> None:
        for _ in range(self.cartas_iniciais):
            for jogador in self.jogadores:
                jogador.receber(self.baralho.comprar())
        for jogador in self.jogadores:
            jogador.ordenar_mao()

    def comprar(self):
        carta = self.baralho.comprar()
        self.jogador_atual.receber(carta)
        self.jogador_atual.ordenar_mao()
        return carta

    def proximo_turno(self) -> None:
        if self.jogador_atual.venceu():
            self.vencedor = self.jogador_atual
            return
        self.indice_turno = (self.indice_turno + 1) % len(self.jogadores)
