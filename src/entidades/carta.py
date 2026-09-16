from dataclasses import dataclass

@dataclass(frozen=True)
class Carta:
    valor: str
    naipe: str
    coringa: bool = False

    ORDEM = {"A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
             "7": 7, "8": 8, "9": 9, "10": 10, "J": 11,
             "Q": 12, "K": 13}

    @property
    def ordem(self) -> int:
        return 0 if self.coringa else self.ORDEM[self.valor]

    def __str__(self) -> str:
        return "Coringa" if self.coringa else f"{self.valor} de {self.naipe}"
