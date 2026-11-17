import json

import pygame
import pytest

from src import persistencia
from src.entidades.bot import Bot
from src.entidades.jogador import Jogador
from src.entidades.partida import NOVO_JOGO, Partida


def clique(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)


def assinatura(cartas):
    return [(c.valor, c.naipe) for c in cartas]


@pytest.fixture
def jogo(monkeypatch, tmp_path):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    import src.audio as audio

    monkeypatch.setattr(audio, "caminho_asset", lambda *partes: tmp_path.joinpath("sem_som", *partes))
    from src.jogo import Jogo

    criados = []

    def criar():
        criados.append(Jogo())
        return criados[-1]

    yield criar
    pygame.quit()


# --- Partida salva --------------------------------------------------------------

def test_partida_salva_no_meio_do_turno_volta_identica():
    partida = Partida([Jogador("Você"), Bot("Bot 1"), Bot("Bot 2")])
    partida.iniciar()
    partida.comprar()
    partida.jogadores[1].jogar_turno(partida)
    partida.jogadores[2].jogar_turno(partida)
    humano = partida.jogador_atual
    baixada = humano.mao[0]
    partida.mover_carta(baixada, NOVO_JOGO)

    copia = Partida.de_dict(json.loads(json.dumps(partida.para_dict())))

    assert copia.indice_atual == partida.indice_atual
    assert copia.rodada == partida.rodada == 2
    assert [j.eh_bot for j in copia.jogadores] == [False, True, True]
    for original, restaurado in zip(partida.jogadores, copia.jogadores):
        assert assinatura(restaurado.mao) == assinatura(original.mao)
    assert [assinatura(j) for j in copia.mesa.jogos] == [assinatura(j) for j in partida.mesa.jogos]
    assert assinatura(copia.baralho.cartas) == assinatura(partida.baralho.cartas)
    # O turno em curso também volta: a carta baixada ainda pode ser desfeita.
    assert assinatura(copia.cartas_baixadas()) == [(baixada.valor, baixada.naipe)]
    copia.desfazer_turno()
    assert len(copia.jogador_atual.mao) == len(humano.mao) + 1
    total = len(copia.baralho) + sum(len(j.mao) for j in copia.jogadores)
    assert total + sum(map(len, copia.mesa.jogos)) == 104


def test_arquivo_de_sessao_invalido_e_ignorado(pasta_dados_temporaria):
    pasta_dados_temporaria.mkdir(parents=True)
    (pasta_dados_temporaria / persistencia.ARQUIVO_SESSAO).write_text("{ quebrado")
    assert persistencia.carregar_sessao() is None
    (pasta_dados_temporaria / persistencia.ARQUIVO_SESSAO).write_text('{"versao": 1, "cartas": []}')
    assert persistencia.carregar_sessao() is None


# --- Placar ---------------------------------------------------------------------

def _partida_encerrada(pontos_humano, pontos_bots):
    from src.entidades.carta import Carta

    jogadores = [Jogador("Você")] + [Bot(f"Bot {i + 1}") for i in range(len(pontos_bots))]
    partida = Partida(jogadores, cartas_iniciais=0)
    for jogador, pontos in zip(jogadores, [pontos_humano, *pontos_bots]):
        jogador.mao = [Carta(str(pontos), "Copas")] if pontos else []
    partida._encerrar()
    return partida


def test_placar_registra_resultados_e_resume():
    persistencia.registrar_resultado(_partida_encerrada(0, [5, 9]))
    persistencia.registrar_resultado(_partida_encerrada(7, [3]))
    persistencia.registrar_resultado(_partida_encerrada(4, [4, 9]))
    persistencia.registrar_resultado(_partida_encerrada(2, [8]))

    placar = persistencia.carregar_placar()
    assert [persistencia.resultado_humano(r) for r in placar] == ["vitoria", "empate", "derrota", "vitoria"]
    assert [persistencia.colocacao(r) for r in placar] == [1, 1, 2, 1]
    assert persistencia.resumo(placar) == {
        "partidas": 4, "vitorias": 2, "empates": 1, "derrotas": 1,
        "aproveitamento": 50, "maior_sequencia": 1,
    }


# --- Fluxo do jogo ------------------------------------------------------------------

def test_voltar_ao_menu_mantem_a_partida_e_ela_sobrevive_ao_reinicio(jogo):
    primeiro = jogo()
    assert not primeiro.tem_partida_em_andamento()
    assert "continuar" not in primeiro.tela_atual.botoes

    primeiro.tela_atual.tratar_evento(clique(primeiro.tela_atual.botoes["novo"].rect.center))
    sessao = primeiro.tela_atual
    mao = assinatura(sessao.humano.mao)
    sessao.atualizar(0.016)
    sessao.tratar_evento(clique(sessao.menu.rect.center))
    assert primeiro.tela_atual is not sessao
    assert "continuar" in primeiro.tela_atual.botoes

    primeiro.tela_atual.tratar_evento(clique(primeiro.tela_atual.botoes["continuar"].rect.center))
    assert primeiro.tela_atual is sessao

    segundo = jogo()  # como se o jogo tivesse sido fechado e aberto de novo
    assert segundo.tem_partida_em_andamento()
    assert assinatura(segundo.sessao.humano.mao) == mao


def test_novo_jogo_com_partida_em_andamento_pede_confirmacao(jogo):
    j = jogo()
    j.nova_partida()
    antiga = j.sessao
    j.trocar_tela("menu")
    menu = j.tela_atual

    menu.tratar_evento(clique(menu.botoes["novo"].rect.center))
    assert menu.confirmando and j.tela_atual is menu
    menu.tratar_evento(clique(menu.cancelar_novo.rect.center))
    assert not menu.confirmando and j.sessao is antiga

    menu.tratar_evento(clique(menu.botoes["novo"].rect.center))
    menu.tratar_evento(clique(menu.confirmar_novo.rect.center))
    assert j.sessao is not antiga and j.tela_atual is j.sessao


def test_partida_encerrada_vai_para_o_placar_uma_vez_e_apaga_a_sessao(jogo, pasta_dados_temporaria):
    j = jogo()
    j.nova_partida()
    assert (pasta_dados_temporaria / persistencia.ARQUIVO_SESSAO).exists()

    j.sessao.partida._encerrar()
    j.sessao.atualizar(0.016)
    j.sessao.atualizar(0.016)

    assert len(persistencia.carregar_placar()) == 1
    assert not (pasta_dados_temporaria / persistencia.ARQUIVO_SESSAO).exists()
    j.trocar_tela("menu")
    assert "continuar" not in j.tela_atual.botoes


def test_troca_de_turno_salva_a_sessao(jogo):
    j = jogo()
    j.nova_partida()
    j.sessao.atualizar(0.016)
    j.sessao.tratar_evento(clique(j.sessao.comprar.rect.center))
    j.sessao.atualizar(0.016)
    salva = persistencia.carregar_sessao()
    assert salva.jogadas == 1
    assert len(salva.jogadores[0].mao) == 10


def test_musica_comeca_uma_vez_e_continua_entre_telas(jogo, monkeypatch):
    j = jogo()
    chamadas = []
    monkeypatch.setattr(pygame.mixer.music, "play", lambda *a, **k: chamadas.append(a))
    monkeypatch.setattr(pygame.mixer.music, "stop", lambda: chamadas.append("stop"))
    for nome in ("gameplay", "menu", "tutorial", "placar", "configuracoes", "gameplay"):
        j.trocar_tela(nome)
        j.audio.tocar_musica()
    assert chamadas == []


# --- Telas novas --------------------------------------------------------------------

def test_tutorial_percorre_todas_as_paginas(jogo):
    from src.ui.tutorial import PAGINAS

    j = jogo()
    j.trocar_tela("tutorial")
    tutorial = j.tela_atual
    for pagina in range(len(PAGINAS)):
        assert tutorial.pagina == pagina
        tutorial.desenhar(j.tela)
        tutorial.tratar_evento(clique(tutorial.proxima.rect.center))
    assert j.tela_atual is j.sessao  # "Jogar" na última página começa a partida


def test_placar_desenha_vazio_e_com_muitas_partidas(jogo):
    from src.ui.placar import LINHAS_VISIVEIS

    j = jogo()
    j.trocar_tela("placar")
    j.tela_atual.desenhar(j.tela)

    for pontos in range(12):
        persistencia.registrar_resultado(_partida_encerrada(pontos % 9 + 2, [5]))
    j.trocar_tela("placar")
    placar = j.tela_atual
    assert placar.resumo["partidas"] == 12
    placar.tratar_evento(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-10))
    assert placar.inicio == 12 - LINHAS_VISIVEIS
    placar.desenhar(j.tela)
