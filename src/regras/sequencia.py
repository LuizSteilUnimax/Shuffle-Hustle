def _consecutivas(cartas, ordem) -> bool:
    return all(
        ordem(atual) == ordem(anterior) + 1
        for anterior, atual in zip(cartas, cartas[1:])
    )


def _ordem_as_alto(carta) -> int:
    return 14 if carta.valor == "A" else carta.ordem


def ordem_sequencia(cartas):
    """Retorna as cartas na ordem da sequência, ou None se não formarem uma.

    O ás pode ser baixo (A, 2, 3) ou alto (Q, K, A), mas não dá a volta (K, A, 2).
    """
    if len(cartas) < 3 or len({carta.naipe for carta in cartas}) != 1:
        return None
    for ordem in (lambda carta: carta.ordem, _ordem_as_alto):
        ordenadas = sorted(cartas, key=ordem)
        if _consecutivas(ordenadas, ordem):
            return ordenadas
    return None


def validar_sequencia(cartas) -> bool:
    return ordem_sequencia(cartas) is not None
