def validar_trinca(cartas) -> bool:
    if len(cartas) < 3:
        return False
    return len({carta.valor for carta in cartas}) == 1
