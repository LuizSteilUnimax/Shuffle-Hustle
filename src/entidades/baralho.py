import random
from .carta import Carta

class Baralho:
    NAIPES = ("Copas", "Ouros", "Paus", "Espadas")
    VALORES = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")

    def __init__(self, quantidade_baralhos: int = 2, coringas_por_baralho: int = 2):
        self.cartas = []
        for _ in range(quantidade_baralhos):
            self.cartas.extend(Carta(valor, naipe) for naipe in self.NAIPES for valor in self.VALORES)
            #self.cartas.extend(Carta("CORINGA", "Sem naipe", True) for _ in range(coringas_por_baralho))
        self.embaralhar()

    def embaralhar(self) -> None:
        random.shuffle(self.cartas)

    def comprar(self):
        return self.cartas.pop() if self.cartas else None

    def __len__(self) -> int:
        return len(self.cartas)
