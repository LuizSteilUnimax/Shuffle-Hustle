from .coringa import contar_coringas

def validar_sequencia(cartas) -> bool:
    if len(cartas) < 3 or contar_coringas(cartas) > 1:
        return False
    normais = sorted((c for c in cartas if not c.coringa), key=lambda c: c.ordem)
    if not normais or len({c.naipe for c in normais}) != 1:
        return False
    faltantes = sum(max(0, b.ordem - a.ordem - 1) for a, b in zip(normais, normais[1:]))
    repetidas = len({c.ordem for c in normais}) != len(normais)
    return not repetidas and faltantes <= contar_coringas(cartas)
