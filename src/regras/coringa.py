def contar_coringas(cartas) -> int:
    return sum(1 for carta in cartas if carta.coringa)
