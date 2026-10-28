from itertools import combinations

from .jogador import Jogador
from ..regras.validacao import validar_jogo


def melhor_jogo_na_mao(mao):
    """Maior trinca ou sequência que pode ser formada só com cartas da mão."""
    candidatos = []

    por_valor = {}
    for carta in mao:
        por_valor.setdefault(carta.valor, []).append(carta)
    candidatos.extend(cartas for cartas in por_valor.values() if len(cartas) >= 3)

    por_naipe = {}
    for carta in mao:
        por_naipe.setdefault(carta.naipe, {}).setdefault(carta.ordem, carta)
    for unicas in por_naipe.values():
        if 1 in unicas:
            unicas[14] = unicas[1]
        sequencia = []
        for ordem in sorted(unicas) + [None]:
            if sequencia and ordem == sequencia[-1] + 1:
                sequencia.append(ordem)
                continue
            if 1 in sequencia and 14 in sequencia:
                sequencia.remove(14)
            if len(sequencia) >= 3:
                candidatos.append([unicas[o] for o in sequencia])
            sequencia = [ordem]

    return max(candidatos, key=len, default=None)


class Bot(Jogador):
    """Jogador automático guloso: baixa o que conseguir e, se nada, compra."""

    eh_bot = True

    def jogar_turno(self, partida) -> int:
        """Joga um turno completo. Retorna quantas cartas baixou (0 = comprou)."""
        while (
            self._baixar_jogo_da_mao(partida)
            or self._encaixar_carta(partida)
            or self._completar_com_mesa(partida)
        ):
            pass

        baixadas = len(partida.cartas_baixadas())
        if partida.pode_finalizar():
            partida.finalizar_turno()
            return baixadas
        partida.desfazer_turno()
        partida.comprar()
        return 0

    def _baixar_jogo_da_mao(self, partida) -> bool:
        jogo = melhor_jogo_na_mao(self.mao)
        return jogo is not None and partida.mover_para_novo_jogo(jogo)

    def _encaixar_carta(self, partida) -> bool:
        for carta in list(self.mao):
            for indice, jogo in enumerate(partida.mesa.jogos):
                if validar_jogo([*jogo, carta]):
                    return partida.mover_carta(carta, indice)
        return False

    def _completar_com_mesa(self, partida) -> bool:
        """Usa duas cartas da mão e uma carta que sobra em um jogo da mesa."""
        livres = [
            carta
            for jogo in partida.mesa.jogos
            if len(jogo) > 3
            for carta in jogo
            if validar_jogo([outra for outra in jogo if outra is not carta])
        ]
        for primeira, segunda in combinations(self.mao, 2):
            for carta in livres:
                if validar_jogo([primeira, segunda, carta]):
                    return partida.mover_para_novo_jogo([primeira, segunda, carta])
        return False
