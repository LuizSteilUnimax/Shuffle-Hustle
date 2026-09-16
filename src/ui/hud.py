import pygame
from ..cores import BRANCO

def desenhar_hud(tela, partida):
    fonte = pygame.font.Font(None, 28)
    textos = [f"Vez: {partida.jogador_atual.nome}", f"Monte: {len(partida.baralho)} cartas"]
    for i, texto in enumerate(textos):
        tela.blit(fonte.render(texto, True, BRANCO), (20, 15 + i * 28))
