from src.entidades.baralho import Baralho
from src.entidades.bot import Bot, melhor_jogo_na_mao
from src.entidades.carta import Carta
from src.entidades.jogador import Jogador
from src.entidades.partida import MAO, NOVO_JOGO, Partida
from src.regras.validacao import ordenar_jogo, validar_jogo


def baralho_com(cartas):
    baralho = Baralho()
    baralho.cartas = list(cartas)
    return baralho


def partida_preparada(maos, mesa=(), monte=(), bots=()):
    """Partida com mãos, mesa e monte definidos, já no turno do primeiro jogador."""
    jogadores = [
        (Bot if i in bots else Jogador)(f"J{i + 1}") for i in range(len(maos))
    ]
    partida = Partida(jogadores, cartas_iniciais=0, baralho=baralho_com(monte))
    for jogador, mao in zip(jogadores, maos):
        jogador.mao = list(mao)
    partida.mesa.jogos = [list(jogo) for jogo in mesa]
    partida.iniciar()
    return partida


def test_trinca_allows_repeated_suits_and_sequences_need_same_suit():
    assert validar_jogo([Carta("8", "Copas"), Carta("8", "Copas"), Carta("8", "Paus")])
    assert validar_jogo([Carta("4", "Espadas"), Carta("5", "Espadas"), Carta("6", "Espadas")])
    assert not validar_jogo([Carta("4", "Espadas"), Carta("6", "Espadas"), Carta("7", "Espadas")])
    assert not validar_jogo([Carta("4", "Espadas"), Carta("5", "Copas"), Carta("6", "Espadas")])


def test_ace_can_be_low_or_high_but_does_not_wrap():
    def seq(*valores):
        return [Carta(valor, "Ouros") for valor in valores]

    assert validar_jogo(seq("A", "2", "3"))
    assert validar_jogo(seq("Q", "K", "A"))
    assert not validar_jogo(seq("K", "A", "2"))
    assert not validar_jogo(seq("5", "5", "6"))
    assert [c.valor for c in ordenar_jogo(seq("A", "Q", "K"))] == ["Q", "K", "A"]


def test_deal_gives_nine_cards_to_each_player():
    partida = Partida([Jogador("A"), Jogador("B"), Jogador("C")])
    partida.iniciar()
    assert all(len(jogador.mao) == 9 for jogador in partida.jogadores)
    assert len(partida.baralho) == 104 - 27


def test_card_points():
    pontos = {v: Carta(v, "Paus").pontos for v in ("2", "10", "J", "Q", "K", "A")}
    assert pontos == {"2": 2, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}


def test_turn_needs_a_hand_card_and_a_valid_table():
    mao = [Carta("8", "Copas"), Carta("8", "Paus"), Carta("8", "Ouros"), Carta("2", "Paus")]
    partida = partida_preparada([mao, [Carta("3", "Paus")]])

    assert not partida.pode_finalizar()
    partida.mover_carta(mao[0], NOVO_JOGO)
    partida.mover_carta(mao[1], 0)
    assert partida.motivo_bloqueio() is not None
    assert not partida.finalizar_turno()

    partida.mover_carta(mao[2], 0)
    assert partida.finalizar_turno()
    assert partida.jogador_atual is partida.jogadores[1]
    assert partida.jogadores[0].mao == [mao[3]]


def test_free_rearrangement_splits_a_sequence():
    copas = [Carta(v, "Copas") for v in ("3", "4", "5", "6", "7", "8")]
    mao = [Carta("6", "Paus"), Carta("6", "Ouros"), Carta("K", "Paus")]
    partida = partida_preparada([mao, [Carta("2", "Paus")]], mesa=[copas])

    # Tira o 6 do meio: a mesa fica inválida até completar os novos jogos.
    partida.mover_para_novo_jogo([mao[0], mao[1], copas[3]])
    partida.mover_carta(copas[4], 0)
    assert not partida.pode_finalizar()
    partida.desfazer_turno()
    assert partida.mesa.jogos == [copas]
    assert len(partida.jogador_atual.mao) == 3

    partida.mover_para_novo_jogo([mao[0], mao[1], copas[3]])
    partida.mover_para_novo_jogo([copas[4], copas[5]])
    assert not partida.pode_finalizar()  # 7-8 sozinhos ainda não formam jogo
    partida.mover_carta(copas[4], 0)
    partida.mover_carta(copas[5], 0)
    assert not partida.pode_finalizar()  # 3-4-5-7-8 não é sequência


def test_only_cards_from_own_hand_return_to_hand():
    trinca = [Carta("9", "Copas"), Carta("9", "Paus"), Carta("9", "Ouros"), Carta("9", "Espadas")]
    carta = Carta("9", "Copas")
    partida = partida_preparada([[carta], [Carta("2", "Paus")]], mesa=[trinca])

    assert not partida.mover_carta(trinca[0], MAO)
    assert partida.mover_carta(carta, 0)
    assert partida.mover_carta(carta, MAO)
    assert partida.jogador_atual.mao == [carta]


def test_draw_reverts_table_only_changes_and_passes_turn():
    trinca = [Carta("9", "Copas"), Carta("9", "Paus"), Carta("9", "Ouros"), Carta("9", "Espadas")]
    comprada = Carta("K", "Copas")
    partida = partida_preparada([[Carta("2", "Paus")], [Carta("3", "Paus")]], mesa=[trinca], monte=[Carta("Q", "Paus"), comprada])

    partida.mover_carta(trinca[0], NOVO_JOGO)
    assert partida.comprar() is comprada
    assert partida.mesa.jogos == [trinca]
    assert partida.jogadores[0].mao[-1] is comprada
    assert partida.jogador_atual is partida.jogadores[1]


def test_cannot_draw_after_laying_down_cards():
    trinca = [Carta("9", "Copas"), Carta("9", "Paus"), Carta("9", "Ouros")]
    carta = Carta("9", "Espadas")
    partida = partida_preparada([[carta, Carta("2", "Paus")], [Carta("3", "Paus")]], mesa=[trinca], monte=[Carta("K", "Copas")])

    partida.mover_carta(carta, 0)
    assert not partida.pode_comprar()
    assert partida.comprar() is None
    assert partida.jogador_atual is partida.jogadores[0]


def test_emptying_hand_wins():
    trinca = [Carta("9", "Copas"), Carta("9", "Paus"), Carta("9", "Ouros")]
    carta = Carta("9", "Espadas")
    partida = partida_preparada([[carta], [Carta("3", "Paus")]], mesa=[trinca])

    partida.mover_carta(carta, 0)
    assert partida.finalizar_turno()
    assert partida.encerrada
    assert partida.vencedor is partida.jogadores[0]


def test_drawing_last_card_ends_game_and_counts_it():
    ultima = Carta("3", "Copas")
    partida = partida_preparada(
        [
            [Carta("A", "Paus")],                       # 14 + 3 comprada = 17
            [Carta("5", "Copas"), Carta("4", "Paus")],  # 9
            [Carta("K", "Ouros"), Carta("2", "Paus")],  # 15
        ],
        monte=[ultima],
    )
    assert partida.comprar() is ultima
    assert partida.encerrada and partida.monte_esgotado
    assert partida.jogadores[0].mao[-1] is ultima
    assert partida.vencedores == [partida.jogadores[1]]
    assert [j.pontos for j in partida.resultado] == [9, 15, 17]


def test_game_continues_while_pile_has_cards():
    partida = partida_preparada(
        [[Carta("A", "Paus")], [Carta("2", "Paus")]],
        monte=[Carta("3", "Copas"), Carta("4", "Copas")],
    )
    partida.comprar()
    assert not partida.encerrada
    assert partida.jogador_atual is partida.jogadores[1]


def test_bot_finds_sets_and_runs_in_hand():
    mao = [Carta("Q", "Paus"), Carta("K", "Paus"), Carta("A", "Paus"), Carta("4", "Copas"), Carta("4", "Ouros")]
    assert sorted(c.valor for c in melhor_jogo_na_mao(mao)) == ["A", "K", "Q"]
    assert melhor_jogo_na_mao(mao[3:]) is None


def test_bot_plays_and_ends_turn():
    mao = [Carta("7", "Copas"), Carta("7", "Paus"), Carta("7", "Ouros"), Carta("8", "Espadas"), Carta("2", "Copas")]
    sequencia = [Carta("5", "Espadas"), Carta("6", "Espadas"), Carta("7", "Espadas")]
    partida = partida_preparada([mao, [Carta("3", "Paus")]], mesa=[sequencia], bots={0})

    assert partida.jogadores[0].jogar_turno(partida) == 4
    assert partida.jogadores[0].mao == [mao[4]]
    assert partida.mesa.esta_valida()
    assert partida.jogador_atual is partida.jogadores[1]


def test_bot_draws_when_it_cannot_play():
    comprada = Carta("K", "Copas")
    partida = partida_preparada([[Carta("2", "Paus")], [Carta("3", "Paus")]], monte=[comprada], bots={0})

    assert partida.jogadores[0].jogar_turno(partida) == 0
    assert partida.jogadores[0].mao[-1] is comprada


def test_bots_play_a_full_game_to_the_end():
    for _ in range(20):
        partida = Partida([Bot("A"), Bot("B"), Bot("C")])
        partida.iniciar()
        for _ in range(1000):
            if partida.encerrada:
                break
            partida.jogador_atual.jogar_turno(partida)
            assert partida.mesa.esta_valida()
        assert partida.encerrada
        total = len(partida.baralho) + sum(len(j.mao) for j in partida.jogadores)
        assert total + sum(len(jogo) for jogo in partida.mesa.jogos) == 104
