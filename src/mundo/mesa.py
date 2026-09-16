from copy import deepcopy
from ..regras.validacao import validar_mesa

class Mesa:
    def __init__(self):
        self.jogos = []

    def adicionar_jogo(self, cartas) -> None:
        self.jogos.append(list(cartas))

    def snapshot(self):
        return deepcopy(self.jogos)

    def restaurar(self, estado) -> None:
        self.jogos = deepcopy(estado)

    def esta_valida(self) -> bool:
        return validar_mesa(self.jogos)
