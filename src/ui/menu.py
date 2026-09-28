import os
import math
import pygame
from .botao import Botao
from ..cores import BRANCO, VERDE_MESA


class Menu:
    def __init__(self, jogo):
        self.jogo = jogo
        self.t = 0.0

        self.title_base = 60
        self.title_color = (255, 235, 120)  # warm yellow tone

        fonte = pygame.font.Font(None, 45)
        cx = jogo.largura // 2
        self.botoes = {
            "jogar": Botao("Jogar", (cx - 150, 170, 300, 70), fonte),
            "config": Botao("Configurações", (cx - 150, 260, 300, 70), fonte),
            "sair": Botao("Sair", (cx - 150, 350, 300, 70), fonte),
        }

        # load background images for decoration
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "backgrounds")
        paths = [os.path.join(assets_dir, f) for f in ("costelao.jpg", "original.jpg") if os.path.exists(os.path.join(assets_dir, f))]
        self.imgs = []
        for p in paths:
            try:
                surf = pygame.image.load(p).convert_alpha()
                self.imgs.append(surf)
            except Exception:
                pass

    def tratar_evento(self, evento):
        if self.botoes["jogar"].clicado(evento):
            self.jogo.trocar_tela("gameplay")
        elif self.botoes["config"].clicado(evento):
            self.jogo.trocar_tela("configuracoes")
        elif self.botoes["sair"].clicado(evento):
            self.jogo.rodando = False

    def atualizar(self, dt):
        self.t += dt

    def desenhar(self, tela):
        tela.fill(VERDE_MESA)

        # title with faster pulsating size
        scale = 1.0 + 0.10 * math.sin(self.t * 3.5)
        tamanho = max(28, int(self.title_base * scale))
        fonte_titulo = pygame.font.Font(None, tamanho)
        titulo = fonte_titulo.render("Mexe-Mexe", True, self.title_color)
        tela.blit(titulo, titulo.get_rect(center=(self.jogo.largura // 2, 80)))

        # draw buttons
        for botao in self.botoes.values():
            botao.desenhar(tela)

        # decorative side images: display costelao.jpg on the left and original.jpg on the right
        if len(self.imgs) >= 1:
            center_y = self.jogo.altura // 2
            desired_h = min(380, int(self.jogo.altura * 0.30))

            # pick left and right images explicitly
            img_left = self.imgs[0]
            img_right = self.imgs[1] if len(self.imgs) > 1 else self.imgs[0]

            def prepare(img):
                sf = desired_h / max(1, img.get_height())
                w = int(img.get_width() * sf)
                h = int(img.get_height() * sf)
                return pygame.transform.smoothscale(img, (w, h))

            left_img = prepare(img_left)
            right_img = prepare(img_right)

            angle_l = 10 * math.sin(self.t * 4.5)
            angle_r = -10 * math.sin(self.t * 4.5 + 0.6)

            left_r = pygame.transform.rotozoom(left_img, angle_l, 1.0)
            right_r = pygame.transform.rotozoom(right_img, angle_r, 1.0)

            lx = 48
            ly = center_y - left_r.get_height() // 2
            rx = self.jogo.largura - 48 - right_r.get_width()
            ry = center_y - right_r.get_height() // 2

            tela.blit(left_r, (lx, ly))
            tela.blit(right_r, (rx, ry))
