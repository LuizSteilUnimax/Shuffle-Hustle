import pygame

from src.entidades.partida import Partida
from src.ui.gameplay import Gameplay


class JogoFake:
    largura = 1360
    altura = 720
    num_bots = 2

    def trocar_tela(self, nome):
        self.nome_da_tela = nome


def clique(tipo, pos):
    return pygame.event.Event(tipo, pos=pos, button=1)


def test_partida_inicia_com_estrutura_basica():
    partida = Partida()
    partida.iniciar()

    assert partida.jogador_atual.nome == "Jogador"
    assert partida.mesa is not None
    assert partida.vencedor is None


def test_gameplay_monta_partida_e_desenha():
    pygame.init()
    jogo = JogoFake()
    gameplay = Gameplay(jogo)

    assert isinstance(gameplay.partida, Partida)
    assert len(gameplay.partida.jogadores) == 3
    assert gameplay.partida.jogador_atual is gameplay.humano
    assert len(gameplay.humano.mao) == 9

    tela = pygame.Surface((jogo.largura, jogo.altura))
    gameplay.atualizar(0.016)
    gameplay.desenhar(tela)
    pygame.quit()


def test_arrastar_carta_para_novo_jogo_e_desfazer():
    pygame.init()
    gameplay = Gameplay(JogoFake())
    carta, rect = gameplay._layout_mao()[0]
    _, novo = gameplay._layout_mesa()

    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, rect.center))
    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONUP, novo.center))
    assert gameplay.partida.mesa.jogos == [[carta]]
    assert gameplay.partida.cartas_baixadas() == [carta]

    gameplay.atualizar(0.016)
    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, gameplay.desfazer.rect.center))
    assert gameplay.partida.mesa.jogos == []
    assert len(gameplay.humano.mao) == 9
    pygame.quit()


def test_comprar_passa_a_vez_e_bot_joga():
    pygame.init()
    gameplay = Gameplay(JogoFake())
    gameplay.atualizar(0.016)
    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, gameplay.comprar.rect.center))
    assert len(gameplay.humano.mao) == 10
    assert gameplay.partida.jogador_atual is not gameplay.humano

    gameplay.atualizar(5.0)
    gameplay.atualizar(5.0)
    assert gameplay.partida.jogador_atual is gameplay.humano or gameplay.partida.encerrada
    pygame.quit()


def test_configuracoes_atualiza_estado_global_do_jogo():
    pygame.init()

    class JogoComConfiguracao:
        largura = 960
        altura = 540
        brilho = 80
        num_bots = 2

        def trocar_tela(self, nome):
            self.tela = nome

    jogo = JogoComConfiguracao()
    from src.ui.configuracoes import Configuracoes

    config = Configuracoes(jogo)
    evento_brilho = clique(pygame.MOUSEBUTTONDOWN, config.trilha_brilho.center)
    config.tratar_evento(evento_brilho)
    assert jogo.brilho != 80

    config.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, config.botoes_bots[3].rect.center))
    assert jogo.num_bots == 3
    pygame.quit()


def test_cartas_baixadas_por_bot_ficam_destacadas_por_um_tempo():
    from src.entidades.carta import Carta
    from src.ui.gameplay import DURACAO_DESTAQUE_BOT

    pygame.init()
    jogo = JogoFake()
    jogo.num_bots = 1  # depois do bot a vez volta para o humano
    gameplay = Gameplay(jogo)
    partida = gameplay.partida
    bot = partida.jogadores[1]
    trinca = [Carta("7", "Copas"), Carta("7", "Paus"), Carta("7", "Ouros")]
    bot.mao = trinca + [Carta("2", "Espadas")]
    gameplay.atualizar(0.016)
    partida.comprar()  # passa a vez para o bot
    partida._iniciar_turno()

    gameplay.atualizar(5.0)
    assert len(gameplay.destaques_bot) == 3
    assert all(any(c is t for t in trinca) for c in gameplay.destaques_bot)

    tela = pygame.Surface((1360, 720))
    gameplay.desenhar(tela)
    gameplay.atualizar(DURACAO_DESTAQUE_BOT + 0.1)
    assert gameplay.destaques_bot == []
    pygame.quit()


def test_distribuicao_anima_e_bot_espera_as_animacoes():
    pygame.init()
    gameplay = Gameplay(JogoFake())
    assert len(gameplay.animacoes.voos) == 9

    gameplay.atualizar(0.016)
    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, gameplay.comprar.rect.center))
    comprada = gameplay.humano.mao[-1]
    assert gameplay.animacoes.voo_de(comprada) is not None

    # O bot só joga depois que as cartas terminam de voar.
    bot = gameplay.partida.jogador_atual
    gameplay.atualizar(0.1)
    assert gameplay.partida.jogador_atual is bot
    for _ in range(60):
        gameplay.atualizar(0.1)
    assert gameplay.partida.jogador_atual is not bot
    pygame.quit()


def test_carta_solta_fora_de_alvo_volta_deslizando_para_a_mao():
    pygame.init()
    gameplay = Gameplay(JogoFake())
    gameplay.atualizar(5.0)
    carta, rect = gameplay._layout_mao()[0]

    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, rect.center))
    gameplay.tratar_evento(clique(pygame.MOUSEBUTTONUP, (20, 400)))
    assert gameplay.humano.mao[0] is carta
    voo = gameplay.animacoes.voo_de(carta)
    assert voo is not None and voo.origem != rect.topleft

    gameplay.desenhar(pygame.Surface((1360, 720)))
    gameplay.atualizar(1.0)
    assert not gameplay.animacoes.ativas
    pygame.quit()


def test_audio_fica_em_silencio_sem_arquivos(tmp_path, monkeypatch):
    import src.audio as audio

    monkeypatch.setattr(audio, "caminho_asset", lambda *partes: tmp_path.joinpath(*partes))
    pygame.init()
    som = audio.Audio()
    som.tocar_musica()
    som.atualizar()
    som.tocar_efeito("baixar")
    som.definir_volume(40)
    assert som.volume == 0.4
    pygame.quit()


def test_configuracoes_ajusta_volume():
    pygame.init()

    class AudioFake:
        volume = None

        def definir_volume(self, valor):
            self.volume = valor

    class JogoComAudio(JogoFake):
        volume = 100
        brilho = 80
        audio = AudioFake()

    from src.ui.configuracoes import Configuracoes

    jogo = JogoComAudio()
    config = Configuracoes(jogo)
    config.tratar_evento(clique(pygame.MOUSEBUTTONDOWN, config.trilha_volume.midleft))
    assert jogo.volume == 0
    assert jogo.audio.volume == 0
    pygame.quit()
