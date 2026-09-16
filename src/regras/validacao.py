from .sequencia import validar_sequencia
from .trinca import validar_trinca

def validar_jogo(cartas) -> bool:
    return validar_sequencia(cartas) or validar_trinca(cartas)

def validar_mesa(jogos) -> bool:
    return bool(jogos) and all(validar_jogo(jogo) for jogo in jogos)
