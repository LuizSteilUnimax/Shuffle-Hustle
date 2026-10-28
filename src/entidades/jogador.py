class Jogador:
    eh_bot = False

    def __init__(self, nome: str):
        self.nome = nome
        self.mao = []
        self.pontos = 0

    def receber(self, carta) -> None:
        if carta is not None:
            self.mao.append(carta)

    def remover_cartas(self, cartas) -> None:
        indices = []
        disponiveis = list(self.mao)
        for carta in cartas:
            indice = next((i for i, atual in enumerate(disponiveis) if atual is carta), None)
            if indice is None:
                raise ValueError("A carta não está na mão do jogador.")
            indices.append(indice)
            disponiveis[indice] = None
        for indice in sorted(indices, reverse=True):
            del self.mao[indice]

    def mover_na_mao(self, carta, indice: int) -> None:
        self.remover_cartas([carta])
        self.mao.insert(max(0, min(indice, len(self.mao))), carta)

    def ordenar_mao(self) -> None:
        self.mao.sort(key=lambda carta: (carta.naipe, carta.ordem))

    def pontos_na_mao(self) -> int:
        return sum(carta.pontos for carta in self.mao)

    def venceu(self) -> bool:
        return not self.mao
