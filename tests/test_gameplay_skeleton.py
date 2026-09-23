import pygame

from src.entidades.partida import Partida
from src.ui.gameplay import Gameplay


class JogoFake:
    largura = 960
    altura = 540

    def trocar_tela(self, nome):
        self.nome_da_tela = nome


def test_partida_inicia_com_estrutura_basica():
    partida = Partida()
    partida.iniciar()

    assert len(partida.jogadores) == 2
    assert partida.jogador_atual.nome == "Jogador 1"
    assert partida.mesa is not None
    assert partida.vencedor is None


def test_gameplay_exibe_estrutura_do_tabuleiro_sem_regras_especificas():
    pygame.init()
    jogo = JogoFake()
    gameplay = Gameplay(jogo)

    assert isinstance(gameplay.partida, Partida)
    assert hasattr(gameplay, "desenhar_area_mesa")
    assert hasattr(gameplay, "desenhar_mao_jogador")
    assert hasattr(gameplay, "desenhar_pilha")
    assert hasattr(gameplay, "passar_turno")
    assert len(gameplay.espacos_mesa) >= 2
    assert hasattr(gameplay, "nova_combinacao")

    tela = pygame.Surface((jogo.largura, jogo.altura))
    gameplay.desenhar(tela)
    pygame.quit()


def test_configuracoes_atualiza_estado_global_do_jogo():
    pygame.init()

    class JogoComConfiguracao:
        largura = 960
        altura = 540
        volume = 100
        brilho = 80

        def __init__(self):
            self.audio = type("AudioFake", (), {"definir_volume": lambda self, valor: setattr(self, "valor", valor)})()

        def trocar_tela(self, nome):
            self.tela = nome

    jogo = JogoComConfiguracao()
    from src.ui.configuracoes import Configuracoes

    config = Configuracoes(jogo)
    evento_volume = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(config.trilha_volume.centerx, config.trilha_volume.centery), button=1)
    config.tratar_evento(evento_volume)

    evento_brilho = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(config.trilha_brilho.centerx, config.trilha_brilho.centery), button=1)
    config.tratar_evento(evento_brilho)

    assert jogo.volume != 100
    assert jogo.brilho != 80
    pygame.quit()
