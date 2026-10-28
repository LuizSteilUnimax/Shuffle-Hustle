from ..regras.validacao import validar_mesa

class Mesa:
    def __init__(self):
        self.jogos = []

    def adicionar_jogo(self, cartas) -> None:
        self.jogos.append(list(cartas))

    def snapshot(self):
        # Cópia rasa: as cartas são comparadas por identidade (há cartas
        # repetidas com dois baralhos), então o estado guarda os mesmos objetos.
        return [list(jogo) for jogo in self.jogos]

    def restaurar(self, estado) -> None:
        self.jogos = [list(jogo) for jogo in estado]

    def esta_valida(self) -> bool:
        return validar_mesa(self.jogos)
