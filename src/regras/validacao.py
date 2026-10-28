from .sequencia import ordem_sequencia, validar_sequencia
from .trinca import validar_trinca

def validar_jogo(cartas) -> bool:
    return validar_sequencia(cartas) or validar_trinca(cartas)

def validar_mesa(jogos) -> bool:
    return all(validar_jogo(jogo) for jogo in jogos)

def ordenar_jogo(cartas):
    """Ordem de exibição: sequências em ordem crescente, trincas por naipe."""
    sequencia = ordem_sequencia(cartas)
    if sequencia is not None:
        return sequencia
    if validar_trinca(cartas):
        return sorted(cartas, key=lambda carta: carta.naipe)
    return list(cartas)
