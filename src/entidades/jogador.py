class Jogador:
    def __init__(self, nome: str):
        self.nome = nome
        self.mao = []
        self.pontos = 0

    def receber(self, carta) -> None:
        if carta is not None:
            self.mao.append(carta)

    def remover_cartas(self, cartas) -> None:
        for carta in cartas:
            self.mao.remove(carta)

    def ordenar_mao(self) -> None:
        self.mao.sort(key=lambda carta: (carta.coringa, carta.naipe, carta.ordem))

    def venceu(self) -> bool:
        return not self.mao
