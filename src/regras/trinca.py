from .coringa import contar_coringas

def validar_trinca(cartas) -> bool:
    if len(cartas) < 3 or contar_coringas(cartas) > 0:
        return False
    valores = {carta.valor for carta in cartas}
    naipes = [carta.naipe for carta in cartas]
    return len(valores) == 1 and len(naipes) == len(set(naipes))
