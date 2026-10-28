import pygame

from . import desenho, tema


class CartaSprite:
    LARGURA, ALTURA = tema.CARTA_LARGURA, tema.CARTA_ALTURA

    SIMBOLOS_NAIPES = {
        "Copas": "♥",
        "Ouros": "♦",
        "Paus": "♣",
        "Espadas": "♠"
    }

    _faces = {}

    @staticmethod
    def limpar_cache():
        CartaSprite._faces.clear()

    @staticmethod
    def superficie(carta):
        """Imagem da frente da carta: a do tema, se existir, ou o desenho padrão."""
        imagem = tema.imagem_carta(carta)
        if imagem is not None:
            return imagem
        chave = (carta.valor, carta.naipe)
        if chave not in CartaSprite._faces:
            CartaSprite._faces[chave] = CartaSprite._criar_face(carta)
        return CartaSprite._faces[chave]

    @staticmethod
    def superficie_verso():
        imagem = tema.imagem_verso()
        if imagem is not None:
            return imagem
        if "verso" not in CartaSprite._faces:
            CartaSprite._faces["verso"] = CartaSprite._criar_verso()
        return CartaSprite._faces["verso"]

    @staticmethod
    def desenhar(tela, carta, x, y, selecionada=False, destaque=None, elevacao=0):
        """Desenha a frente da carta.

        `destaque` é uma cor de contorno opcional; `elevacao` levanta a carta
        (hover), e `selecionada` a levanta mais, como quando é arrastada.
        """
        elevacao += tema.ELEVACAO_SELECAO if selecionada else 0
        rect = pygame.Rect(x, y - elevacao, CartaSprite.LARGURA, CartaSprite.ALTURA)
        CartaSprite._desenhar_sombra(tela, rect, elevacao)
        tela.blit(CartaSprite.superficie(carta), rect)
        if destaque is not None:
            desenho.contorno_brilhante(tela, rect, destaque, tema.RAIO_CARTA)
        return rect

    @staticmethod
    def desenhar_verso(tela, x, y):
        rect = pygame.Rect(x, y, CartaSprite.LARGURA, CartaSprite.ALTURA)
        CartaSprite._desenhar_sombra(tela, rect, 0)
        tela.blit(CartaSprite.superficie_verso(), rect)
        return rect

    @staticmethod
    def _desenhar_sombra(tela, rect, elevacao):
        if elevacao:
            desenho.sombra(tela, rect, tema.RAIO_CARTA, (3, 8), desfoque=8, alpha=95)
        else:
            desenho.sombra(tela, rect, tema.RAIO_CARTA, (1, 3), desfoque=3, alpha=120)

    # --- Desenho padrão --------------------------------------------------

    @staticmethod
    def _cor(carta):
        vermelho = carta.naipe in ("Copas", "Ouros")
        return tema.COR_NAIPE_VERMELHO if vermelho else tema.COR_NAIPE_PRETO

    @staticmethod
    def _indice(carta, cor):
        """Valor com o naipe embaixo, como no canto das cartas de baralho."""
        valor = tema.fonte("indice", 21).render(carta.valor, True, cor)
        naipe = tema.fonte("naipe", 13).render(CartaSprite.SIMBOLOS_NAIPES[carta.naipe], True, cor)
        largura = max(valor.get_width(), naipe.get_width())
        superficie = pygame.Surface((largura, valor.get_height() + naipe.get_height() - 6), pygame.SRCALPHA)
        superficie.blit(valor, valor.get_rect(midtop=(largura // 2, 0)))
        superficie.blit(naipe, naipe.get_rect(midbottom=(largura // 2, superficie.get_height())))
        return superficie

    @staticmethod
    def _criar_face(carta):
        largura, altura = CartaSprite.LARGURA, CartaSprite.ALTURA
        superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
        area = superficie.get_rect()
        pygame.draw.rect(superficie, tema.COR_CARTA, area, border_radius=tema.RAIO_CARTA)
        pygame.draw.rect(superficie, tema.COR_CARTA_BORDA, area, 1, border_radius=tema.RAIO_CARTA)

        cor = CartaSprite._cor(carta)
        simbolo = CartaSprite.SIMBOLOS_NAIPES[carta.naipe]
        indice = CartaSprite._indice(carta, cor)
        superficie.blit(indice, (5, 3))
        invertido = pygame.transform.rotate(indice, 180)
        superficie.blit(invertido, invertido.get_rect(bottomright=(largura - 5, altura - 3)))

        if carta.valor in ("J", "Q", "K"):
            moldura = area.inflate(-32, -30)
            pygame.draw.rect(superficie, tema.misturar(tema.COR_CARTA, cor, 0.1), moldura, border_radius=4)
            pygame.draw.rect(superficie, tema.misturar(tema.COR_CARTA, cor, 0.55), moldura, 1, border_radius=4)
            desenho.texto(superficie, carta.valor, tema.fonte("negrito", 28), cor,
                          center=(moldura.centerx, moldura.centery - 6))
            desenho.texto(superficie, simbolo, tema.fonte("naipe", 15), cor,
                          center=(moldura.centerx, moldura.bottom - 13))
        else:
            tamanho = 44 if carta.valor == "A" else 32
            desenho.texto(superficie, simbolo, tema.fonte("naipe", tamanho), cor,
                          center=(area.centerx, area.centery + 1))
        return superficie

    @staticmethod
    def _criar_verso():
        largura, altura = CartaSprite.LARGURA, CartaSprite.ALTURA
        superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
        area = superficie.get_rect()
        pygame.draw.rect(superficie, tema.COR_VERSO, area, border_radius=tema.RAIO_CARTA)

        interna = area.inflate(-12, -12)
        padrao = pygame.Surface(interna.size, pygame.SRCALPHA)
        cor_padrao = (*tema.COR_VERSO_DETALHE, 55)
        for deslocamento in range(-interna.height, interna.width, 9):
            pygame.draw.line(padrao, cor_padrao, (deslocamento, 0), (deslocamento + interna.height, interna.height))
            pygame.draw.line(padrao, cor_padrao, (deslocamento, interna.height), (deslocamento + interna.height, 0))
        superficie.blit(padrao, interna)
        pygame.draw.rect(superficie, tema.COR_VERSO_DETALHE, interna, 1, border_radius=4)

        cx, cy = area.center
        losango = [(cx, cy - 17), (cx + 12, cy), (cx, cy + 17), (cx - 12, cy)]
        pygame.draw.polygon(superficie, tema.COR_VERSO, losango)
        pygame.draw.polygon(superficie, tema.COR_VERSO_DETALHE, losango, 2)
        pygame.draw.rect(superficie, tema.escurecer(tema.COR_VERSO, 0.35), area, 1, border_radius=tema.RAIO_CARTA)
        return superficie
