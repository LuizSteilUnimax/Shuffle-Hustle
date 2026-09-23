import pygame
from .botao import Botao
from .carta_sprite import CartaSprite
from .hud import desenhar_hud
from ..cores import VERDE_MESA, BRANCO
from ..entidades.partida import Partida


class Gameplay:
    def __init__(self, jogo):
        self.jogo = jogo
        self.partida = Partida()
        self.partida.iniciar()

        self.espacos_mesa = [
            {"nome": "Combinação 1", "cartas": [], "rect": pygame.Rect(310, 150, 160, 110)},
            {"nome": "Combinação 2", "cartas": [], "rect": pygame.Rect(500, 150, 160, 110)},
        ]
        self.nova_combinacao = pygame.Rect(self.jogo.largura - 170, 150, 130, 110)
        self.carta_arrastando = None
        self.posicao_drag = None

        fonte = pygame.font.Font(None, 30)
        self.comprar = Botao("Comprar", (20, jogo.altura - 70, 140, 45), fonte)
        self.passar = Botao("Passar turno", (jogo.largura - 190, jogo.altura - 70, 160, 45), fonte)
        self.menu = Botao("Menu", (jogo.largura - 140, 15, 120, 40), fonte)

    def _sincronizar_mesa(self):
        self.partida.mesa.jogos = [slot["cartas"][:] for slot in self.espacos_mesa if slot["cartas"]]

    def adicionar_slot_mesa(self):
        nome = f"Combinação {len(self.espacos_mesa) + 1}"
        rect = pygame.Rect(310 + len(self.espacos_mesa) * 190, 150, 160, 110)
        self.espacos_mesa.append({"nome": nome, "cartas": [], "rect": rect})
        self._sincronizar_mesa()

    def passar_turno(self):
        self.partida.proximo_turno()

    def _cartas_na_mao(self):
        jogador = self.partida.jogador_atual
        mao = jogador.mao
        inicio = max(180, (self.jogo.largura - (len(mao) - 1) * 38 - 70) // 2)
        rects = []
        for i, carta in enumerate(mao):
            x = inicio + i * 38
            y = self.jogo.altura - 125
            rects.append((carta, i, pygame.Rect(x, y, CartaSprite.LARGURA, CartaSprite.ALTURA)))
        return rects

    def tratar_evento(self, evento):
        if self.menu.clicado(evento):
            self.jogo.trocar_tela("menu")
            return

        if self.comprar.clicado(evento):
            self.partida.comprar()
            self.partida.proximo_turno()
            return

        if self.passar.clicado(evento):
            self.passar_turno()
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.nova_combinacao.collidepoint(evento.pos):
                self.adicionar_slot_mesa()
                return

            for carta, _, rect in self._cartas_na_mao():
                if rect.collidepoint(evento.pos):
                    self.carta_arrastando = {"carta": carta}
                    self.posicao_drag = evento.pos
                    return

        elif evento.type == pygame.MOUSEMOTION and self.carta_arrastando is not None:
            self.posicao_drag = evento.pos

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and self.carta_arrastando is not None:
            carta = self.carta_arrastando["carta"]
            jogador = self.partida.jogador_atual
            slot = next((slot for slot in self.espacos_mesa if slot["rect"].collidepoint(evento.pos)), None)

            if slot is not None and carta in jogador.mao:
                jogador.remover_cartas([carta])
                slot["cartas"].append(carta)
                self._sincronizar_mesa()

            self.carta_arrastando = None
            self.posicao_drag = None

    def atualizar(self, dt):
        pass

    def desenhar_pilha(self, tela):
        rect = pygame.Rect(40, 110, 180, 200)
        pygame.draw.rect(tela, (60, 90, 70), rect, border_radius=18)
        pygame.draw.rect(tela, BRANCO, rect, 2, border_radius=18)

        fonte_titulo = pygame.font.Font(None, 28)
        fonte_numero = pygame.font.Font(None, 40)
        titulo = fonte_titulo.render("Monte", True, BRANCO)
        tela.blit(titulo, (rect.x + 18, rect.y + 16))
        tela.blit(fonte_numero.render(str(len(self.partida.baralho)), True, BRANCO), (rect.centerx - 18, rect.centery + 15))

        texto = pygame.font.Font(None, 20).render("Compras e descartes", True, BRANCO)
        tela.blit(texto, (rect.x + 16, rect.y + rect.height - 30))

    def desenhar_area_mesa(self, tela):
        rect = pygame.Rect(250, 115, self.jogo.largura - 500, 180)
        pygame.draw.rect(tela, (54, 86, 60), rect, border_radius=20)
        pygame.draw.rect(tela, BRANCO, rect, 2, border_radius=20)

        titulo = pygame.font.Font(None, 30).render("Mesa", True, BRANCO)
        tela.blit(titulo, (rect.x + 20, rect.y + 15))

        for slot in self.espacos_mesa:
            pygame.draw.rect(tela, (90, 120, 90), slot["rect"], border_radius=12)
            pygame.draw.rect(tela, BRANCO, slot["rect"], 1, border_radius=12)

            nome = pygame.font.Font(None, 18).render(slot["nome"], True, BRANCO)
            tela.blit(nome, (slot["rect"].x + 10, slot["rect"].y + 10))

            if not slot["cartas"]:
                texto = pygame.font.Font(None, 16).render("Solte aqui", True, BRANCO)
                tela.blit(texto, (slot["rect"].x + 18, slot["rect"].y + 50))
                continue

            x_base = slot["rect"].x + 18
            for indice, carta in enumerate(slot["cartas"]):
                CartaSprite.desenhar(tela, carta, x_base + indice * 26, slot["rect"].y + 45)

        pygame.draw.rect(tela, (110, 135, 110), self.nova_combinacao, border_radius=12)
        pygame.draw.rect(tela, BRANCO, self.nova_combinacao, 1, border_radius=12)
        mais = pygame.font.Font(None, 42).render("+", True, BRANCO)
        tela.blit(mais, mais.get_rect(center=self.nova_combinacao.center))
        titulo_nova = pygame.font.Font(None, 16).render("Nova combinação", True, BRANCO)
        tela.blit(titulo_nova, titulo_nova.get_rect(center=(self.nova_combinacao.centerx, self.nova_combinacao.bottom - 12)))

    def desenhar_jogadores(self, tela):
        fonte = pygame.font.Font(None, 26)
        for indice, jogador in enumerate(self.partida.jogadores):
            if indice == self.partida.indice_turno:
                caixa = pygame.Rect(250 + indice * 200, 30, 170, 55)
                pygame.draw.rect(tela, (80, 130, 90), caixa, border_radius=12)
                texto = fonte.render(f"{jogador.nome} (vez)", True, BRANCO)
            else:
                caixa = pygame.Rect(250 + indice * 200, 30, 170, 55)
                pygame.draw.rect(tela, (72, 78, 82), caixa, border_radius=12)
                texto = fonte.render(jogador.nome, True, BRANCO)
            tela.blit(texto, (caixa.x + 14, caixa.y + 14))

    def desenhar_mao_jogador(self, tela):
        jogador = self.partida.jogador_atual
        mao = jogador.mao
        inicio = max(180, (self.jogo.largura - (len(mao) - 1) * 38 - 70) // 2)

        for i, carta in enumerate(mao):
            rect = CartaSprite.desenhar(tela, carta, inicio + i * 38, self.jogo.altura - 125)
            if self.carta_arrastando is not None and self.carta_arrastando["carta"] == carta:
                pygame.draw.rect(tela, (255, 255, 255), rect, 2, border_radius=7)

        if self.carta_arrastando is not None and self.posicao_drag is not None:
            carta = self.carta_arrastando["carta"]
            rect = pygame.Rect(self.posicao_drag[0] - 35, self.posicao_drag[1] - 50, CartaSprite.LARGURA, CartaSprite.ALTURA)
            pygame.draw.rect(tela, BRANCO, rect, border_radius=7)
            pygame.draw.rect(tela, (0, 0, 0), rect, 2, border_radius=7)
            cor = (255, 0, 0) if carta.naipe in ("Copas", "Ouros") else (0, 0, 0)
            texto = pygame.font.Font(None, 24).render("JK" if carta.coringa else carta.valor, True, cor)
            tela.blit(texto, (rect.x + 7, rect.y + 7))

        legenda = pygame.font.Font(None, 22).render(f"Mão de {jogador.nome}", True, BRANCO)
        tela.blit(legenda, (self.jogo.largura // 2 - legenda.get_width() // 2, self.jogo.altura - 170))

    def desenhar(self, tela):
        tela.fill(VERDE_MESA)
        desenhar_hud(tela, self.partida)
        self.desenhar_jogadores(tela)
        self.desenhar_pilha(tela)
        self.desenhar_area_mesa(tela)
        self.comprar.desenhar(tela)
        self.passar.desenhar(tela)
        self.menu.desenhar(tela)
        self.desenhar_mao_jogador(tela)

        aviso = pygame.font.Font(None, 24).render("Estrutura base do jogo: mesa, mão, monte e turno", True, BRANCO)
        tela.blit(aviso, aviso.get_rect(center=(self.jogo.largura // 2, self.jogo.altura - 30)))
