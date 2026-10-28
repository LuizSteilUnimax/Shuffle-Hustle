from dataclasses import dataclass

@dataclass(frozen=True)
class Carta:
    valor: str
    naipe: str

    ORDEM = {"A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
             "7": 7, "8": 8, "9": 9, "10": 10, "J": 11,
             "Q": 12, "K": 13}

    @property
    def ordem(self) -> int:
        return self.ORDEM[self.valor]

    @property
    def pontos(self) -> int:
        """Valor da carta na contagem final: face, J=11, Q=12, K=13, A=14."""
        return 14 if self.valor == "A" else self.ordem

    def __str__(self) -> str:
        return f"{self.valor} de {self.naipe}"
