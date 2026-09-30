import pygame
from ..cores import BRANCO, PRETO, VERMELHO

CINZA_BORDA = (220, 220, 220)
CINZA_SOMBRA = (40, 40, 40)      
AZUL_BARALHO = (25, 50, 110)      

class CartaSprite:
    LARGURA, ALTURA = 75, 105
    FONTE_CANTO = None
    FONTE_CENTRO = None

    SIMBOLOS_NAIPES = {
        "Copas": "♥",
        "Ouros": "♦",
        "Paus": "♣",
        "Espadas": "♠"
    }

    @staticmethod
    def inicializar_fontes():
        
        if CartaSprite.FONTE_CANTO is None:
            if not pygame.font.get_init():
                pygame.font.init()
            
            
            CartaSprite.FONTE_CANTO = pygame.font.SysFont('arial', 16, bold=True)
            CartaSprite.FONTE_CENTRO = pygame.font.SysFont('arial', 42, bold=True)

    @staticmethod
    def desenhar(tela, carta, x, y, selecionada=False):
        """Desenha a frente da carta com os valores e naipes correspondentes."""
        
        CartaSprite.inicializar_fontes()

        
        deslocamento_y = 15 if selecionada else 0
        rect = pygame.Rect(x, y - deslocamento_y, CartaSprite.LARGURA, CartaSprite.ALTURA)

       
        distancia_sombra = 5 if selecionada else 3
        sombra_rect = pygame.Rect(rect.x + distancia_sombra, rect.y + distancia_sombra, rect.width, rect.height)
        pygame.draw.rect(tela, CINZA_SOMBRA, sombra_rect, border_radius=8)

        
        pygame.draw.rect(tela, BRANCO, rect, border_radius=8)

        
        cor = VERMELHO if carta.naipe in ("Copas", "Ouros") else PRETO

        
        simbolo = CartaSprite.SIMBOLOS_NAIPES.get(carta.naipe, "")
        
        
        txt_valor = CartaSprite.FONTE_CANTO.render(carta.valor, True, cor)
        txt_naipe_canto = CartaSprite.FONTE_CANTO.render(simbolo, True, cor)
        
        tela.blit(txt_valor, (rect.x + 6, rect.y + 5))
        tela.blit(txt_naipe_canto, (rect.x + 6, rect.y + 20))

        
        txt_centro = CartaSprite.FONTE_CENTRO.render(simbolo, True, cor)
        centro_rect = txt_centro.get_rect(center=(rect.centerx, rect.centery + 2))
        tela.blit(txt_centro, centro_rect)

        
        cor_borda = PRETO if selecionada else CINZA_BORDA
        pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=8)

        return rect

    @staticmethod
    def desenhar_verso(tela, x, y):
        """Desenha o verso da carta com um padrão geométrico elegante."""
        rect = pygame.Rect(x, y, CartaSprite.LARGURA, CartaSprite.ALTURA)
        
        
        sombra = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        pygame.draw.rect(tela, CINZA_SOMBRA, sombra, border_radius=8)
        
        
        pygame.draw.rect(tela, AZUL_BARALHO, rect, border_radius=8)
        
        
        borda_interna = rect.inflate(-10, -10)
        pygame.draw.rect(tela, BRANCO, borda_interna, 1, border_radius=5)
        
        
        centro_x, centro_y = rect.centerx, rect.centery
        pontos_losango = [
            (centro_x, centro_y - 20),  
            (centro_x + 15, centro_y),  
            (centro_x, centro_y + 20),  
            (centro_x - 15, centro_y)   
        ]
        pygame.draw.polygon(tela, BRANCO, pontos_losango, 2)
        
        
        pygame.draw.rect(tela, (15, 30, 70), rect, 2, border_radius=8)
