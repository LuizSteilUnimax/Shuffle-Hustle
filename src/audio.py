"""Música e efeitos sonoros, todos opcionais.

Arquivos em `assets/sounds/`:

- `loop-ambiance.mp3` e `loop-soundtrack.mp3` tocam juntos, em loop, durante a
  partida (a ambiência por streaming, a trilha carregada em segundo plano);
- os demais arquivos de áudio da pasta são músicas do menu: uma é sorteada por
  sessão e continua de onde parou ao voltar ao menu;
- `efeitos/<evento>.ogg` (ou `.wav`/`.mp3`) são efeitos sonoros, com os eventos
  listados em EFEITOS.

Um arquivo ausente, ou a falta de dispositivo de áudio, apenas silencia aquele
som: o jogo nunca depende do áudio para funcionar.
"""
import random
import threading

import pygame

from .util import caminho_asset

FORMATOS = (".ogg", ".wav", ".mp3")
# A ambiência é longa e toca por streaming (mixer.music); a trilha fica
# decodificada na memória para tocar junto, em um canal reservado.
FAIXA_AMBIENTE = "loop-ambiance.mp3"
FAIXA_TRILHA = "loop-soundtrack.mp3"
EFEITOS = ("comprar", "baixar", "invalido", "confirmar", "vitoria", "derrota")


class Audio:
    def __init__(self):
        self.volume = 1.0
        self.disponivel = self._inicializar_mixer()
        self.faixa_menu = self._sortear_faixa_menu()
        self._posicao_menu = 0.0
        self._tocando = None
        self._canal_trilha = None
        self._sons = {}
        self._trava = threading.Lock()
        if self.disponivel:
            # Decodificar a trilha leva cerca de um segundo; faz isso enquanto o menu aparece.
            threading.Thread(
                target=self._carregar, args=(caminho_asset("sounds", FAIXA_TRILHA),), daemon=True
            ).start()

    @staticmethod
    def _inicializar_mixer() -> bool:
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            # O canal 0 fica com a trilha da partida; efeitos usam os demais.
            pygame.mixer.set_reserved(1)
            return True
        except pygame.error:
            return False

    @staticmethod
    def _sortear_faixa_menu():
        pasta = caminho_asset("sounds")
        if not pasta.is_dir():
            return None
        faixas = [
            caminho
            for caminho in sorted(pasta.iterdir())
            if caminho.is_file()
            and caminho.suffix.lower() in FORMATOS
            and not caminho.name.lower().startswith("loop-")
        ]
        return random.choice(faixas) if faixas else None

    def _carregar(self, caminho):
        with self._trava:
            if caminho not in self._sons:
                som = None
                if caminho.is_file():
                    try:
                        som = pygame.mixer.Sound(str(caminho))
                    except pygame.error:
                        som = None
                self._sons[caminho] = som
            return self._sons[caminho]

    def definir_volume(self, valor: int) -> None:
        self.volume = max(0, min(100, valor)) / 100
        if not self.disponivel:
            return
        pygame.mixer.music.set_volume(self.volume)
        if self._canal_trilha is not None:
            self._canal_trilha.set_volume(self.volume)

    def _parar(self) -> None:
        if self._tocando == "menu":
            # get_pos conta a partir do último play, que começou em _posicao_menu.
            self._posicao_menu += max(0, pygame.mixer.music.get_pos()) / 1000
        pygame.mixer.music.stop()
        if self._canal_trilha is not None:
            self._canal_trilha.stop()
            self._canal_trilha = None
        self._tocando = None

    def tocar_menu(self) -> None:
        if not self.disponivel or self._tocando == "menu":
            return
        self._parar()
        if self.faixa_menu is None:
            return
        try:
            pygame.mixer.music.load(str(self.faixa_menu))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops=-1, start=self._posicao_menu)
            self._tocando = "menu"
        except pygame.error:
            self._posicao_menu = 0.0

    def tocar_partida(self) -> None:
        if not self.disponivel or self._tocando == "partida":
            return
        self._parar()
        self._tocando = "partida"
        ambiente = caminho_asset("sounds", FAIXA_AMBIENTE)
        if ambiente.is_file():
            try:
                pygame.mixer.music.load(str(ambiente))
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                pass
        trilha = self._carregar(caminho_asset("sounds", FAIXA_TRILHA))
        if trilha is not None:
            self._canal_trilha = pygame.mixer.Channel(0)
            self._canal_trilha.play(trilha, loops=-1)
            self._canal_trilha.set_volume(self.volume)

    def tocar_efeito(self, evento: str) -> None:
        if not self.disponivel:
            return
        som = next(
            (
                som
                for som in (
                    self._carregar(caminho_asset("sounds", "efeitos", evento + formato))
                    for formato in FORMATOS
                )
                if som is not None
            ),
            None,
        )
        if som is not None:
            som.set_volume(self.volume)
            som.play()
