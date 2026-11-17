"""Música e efeitos sonoros, todos opcionais.

Arquivos em `assets/sounds/`:

- `loop-ambiance.mp3` e `loop-soundtrack.mp3` formam a música do jogo: tocam
  juntos, em loop, desde a abertura e sem interrupção em todas as telas (a
  ambiência por streaming, a trilha carregada em segundo plano);
- `efeitos/<evento>.ogg` (ou `.wav`/`.mp3`) são efeitos sonoros, com os eventos
  listados em EFEITOS.

Um arquivo ausente, ou a falta de dispositivo de áudio, apenas silencia aquele
som: o jogo nunca depende do áudio para funcionar.
"""
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
        self._tocando = False
        self._canal_trilha = None
        self._sons = {}
        self._trava = threading.Lock()
        if self.disponivel:
            # Decodificar a trilha leva cerca de um segundo; faz isso sem travar a abertura.
            threading.Thread(
                target=self._carregar, args=(caminho_asset("sounds", FAIXA_TRILHA),), daemon=True
            ).start()

    @staticmethod
    def _inicializar_mixer() -> bool:
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            # O canal 0 fica com a trilha da música; efeitos usam os demais.
            pygame.mixer.set_reserved(1)
            return True
        except pygame.error:
            return False

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
        if self._canal_trilha:
            self._canal_trilha.set_volume(self.volume)

    def tocar_musica(self) -> None:
        """Começa a música do jogo. Chamadas seguintes não a reiniciam, então
        ela continua do mesmo ponto ao trocar de tela."""
        if not self.disponivel or self._tocando:
            return
        self._tocando = True
        ambiente = caminho_asset("sounds", FAIXA_AMBIENTE)
        if ambiente.is_file():
            try:
                pygame.mixer.music.load(str(ambiente))
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(loops=-1)
            except pygame.error:
                pass
        self.atualizar()

    def atualizar(self) -> None:
        """Junta a trilha à música assim que ela terminar de carregar."""
        if not self._tocando or self._canal_trilha is not None:
            return
        caminho = caminho_asset("sounds", FAIXA_TRILHA)
        if caminho not in self._sons:
            return  # ainda carregando
        trilha = self._sons[caminho]
        self._canal_trilha = False  # tentado: não procura de novo
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
