import pygame


class Audio:
    def __init__(self):
        self.volume = 1.0

    def definir_volume(self, valor: int) -> None:
        self.volume = max(0, min(100, valor)) / 100
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.set_volume(self.volume)
