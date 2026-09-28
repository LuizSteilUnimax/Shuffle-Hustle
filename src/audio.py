import os
import random

import pygame


class Audio:
    def __init__(self):
        self.volume = 1.0
        self.gameplay_tracks = [
            os.path.join("assets", "sounds", "loop-ambiance.mp3"),
            os.path.join("assets", "sounds", "loop-soundtrack.mp3"),
        ]
        self.menu_tracks = self._listar_menu_tracks()
        self._menu_track_inicial = self.menu_tracks[0] if self.menu_tracks else None
        self._menu_posicao = 0.0
        self._menu_ativa = False
        self._canal_ambiente = None
        self._canal_trilha = None
        self._inicializar_mixer()
        self._selecionar_track_do_sessao()

    def _listar_menu_tracks(self):
        pasta = os.path.join("assets", "sounds")
        if not os.path.isdir(pasta):
            return []

        arquivos = []
        for nome in sorted(os.listdir(pasta)):
            caminho = os.path.join(pasta, nome)
            if os.path.isfile(caminho) and nome.lower().endswith((".mp3", ".wav", ".ogg")):
                if nome.lower().startswith("loop-"):
                    continue
                arquivos.append(caminho)
        return arquivos

    def _selecionar_track_do_sessao(self):
        if not self.menu_tracks:
            self._menu_track_inicial = None
            return
        self._menu_track_inicial = random.choice(self.menu_tracks)
        self._menu_posicao = 0.0

    def _inicializar_mixer(self):
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except pygame.error:
            return

    def definir_volume(self, valor: int) -> None:
        self.volume = max(0, min(100, valor)) / 100
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.set_volume(self.volume)
            if self._canal_ambiente is not None:
                self._canal_ambiente.set_volume(self.volume)
            if self._canal_trilha is not None:
                self._canal_trilha.set_volume(self.volume)

    def _salvar_posicao_menu(self) -> None:
        if pygame.mixer.get_init() is None or not self._menu_ativa:
            return
        pos_ms = pygame.mixer.music.get_pos()
        self._menu_posicao = max(0.0, pos_ms / 1000.0)

    def _parar_audio(self) -> None:
        if pygame.mixer.get_init() is None:
            return
        pygame.mixer.stop()
        pygame.mixer.music.stop()

    def _usar_track_menu_atual(self):
        return self._menu_track_inicial

    def tocar_menu(self) -> None:
        self._salvar_posicao_menu()
        self._parar_audio()
        if pygame.mixer.get_init() is None:
            return

        faixa = self._usar_track_menu_atual()
        if faixa is None:
            return

        pygame.mixer.music.load(faixa)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(start=self._menu_posicao)
        self._menu_ativa = True

    def tocar_gameplay(self) -> None:
        self._salvar_posicao_menu()
        self._parar_audio()
        self._menu_ativa = False
        if pygame.mixer.get_init() is None:
            return

        self._canal_ambiente = pygame.mixer.Channel(0)
        self._canal_trilha = pygame.mixer.Channel(1)

        ambiente = pygame.mixer.Sound(self.gameplay_tracks[0])
        trilha = pygame.mixer.Sound(self.gameplay_tracks[1])

        self._canal_ambiente.play(ambiente, loops=-1)
        self._canal_trilha.play(trilha, loops=-1)
        self._canal_ambiente.set_volume(self.volume)
        self._canal_trilha.set_volume(self.volume)
