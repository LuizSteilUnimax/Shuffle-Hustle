import pygame

from . import desenho, tema
from .animacao import Animacoes, Voo
from .botao import Botao
from .carta_sprite import CartaSprite
from .hud import cartas, desenhar_assentos, rects_assentos
from ..entidades.bot import Bot
from ..entidades.jogador import Jogador
from ..entidades.partida import Partida, MAO, NOVO_JOGO
from ..regras.validacao import validar_jogo, ordenar_jogo

ATRASO_BOT = 1.2
DURACAO_DESTAQUE_BOT = 3.0
DURACAO_AVISO = 2.5
PASSOS_MESA = (24, 18, 13)
ESCALONAMENTO_DISTRIBUICAO = 0.06
ESCALONAMENTO_BOT = 0.09


class Gameplay:
    def __init__(self, jogo, partida=None):
        """Começa uma partida nova ou, com `partida`, retoma uma salva."""
        self.jogo = jogo
        retomada = partida is not None
        if not retomada:
            num_bots = getattr(jogo, "num_bots", 2)
            jogadores = [Jogador("Você")] + [Bot(f"Bot {i + 1}") for i in range(num_bots)]
            partida = Partida(jogadores)
            partida.iniciar()
        self.partida = partida
        self.humano = next(j for j in partida.jogadores if not j.eh_bot)
        self._jogadas_salvas = partida.jogadas

        self.arrasto = None
        self.aviso = ""
        self.tempo_aviso = 0.0
        self.tempo_bot = 0.0
        self.destaques_bot = []
        self.tempo_destaque_bot = 0.0
        self.tempo = 0.0
        self.animacoes = Animacoes()
        self.fim_anunciado = False

        largura, altura = jogo.largura, jogo.altura
        self.rect_monte = pygame.Rect(20, 104, CartaSprite.LARGURA + 40, CartaSprite.ALTURA + 80)
        x_mesa = self.rect_monte.right + 20
        self.rect_mesa = pygame.Rect(x_mesa, 104, largura - x_mesa - 20, altura - 344)
        y_botoes = self.rect_mesa.bottom + 12
        self.rect_mao = pygame.Rect(
            x_mesa, y_botoes + 48, self.rect_mesa.width, altura - y_botoes - 48
        )

        self.comprar = Botao("Comprar", (x_mesa, y_botoes, 130, 40))
        self.desfazer = Botao("Desfazer", (x_mesa + 142, y_botoes, 130, 40))
        self.finalizar = Botao(
            "Finalizar jogada", (x_mesa + 284, y_botoes, 190, 40), papel="primario"
        )
        self.ordenar = Botao("Ordenar mão", (self.rect_mesa.right - 150, y_botoes, 150, 40))
        self.menu = Botao("Menu", (largura - 120, 14, 100, 36))

        centro = largura // 2
        y_fim = altura // 2 + 60 + 17 * len(partida.jogadores)
        self.jogar_novamente = Botao(
            "Jogar novamente", (centro - 210, y_fim, 200, 46), papel="primario"
        )
        self.voltar_menu = Botao("Voltar ao menu", (centro + 10, y_fim, 200, 46))

        if retomada:
            self.retomar()
            return
        # Distribuição: as cartas da mão saem do monte uma a uma.
        for i, (carta, _) in enumerate(self._layout_mao()):
            self.animacoes.adicionar(
                Voo(carta, self._origem_monte(), atraso=i * ESCALONAMENTO_DISTRIBUICAO)
            )

    # --- Estado ------------------------------------------------------------

    def retomar(self):
        """Volta à partida (vinda do menu ou do disco) sem arrasto pendente."""
        self.arrasto = None
        if not self.partida.encerrada:
            self._mostrar_aviso(f"Partida retomada: rodada {self.partida.rodada}.")

    def _chamar_jogo(self, metodo, *args):
        # As telas de teste usam um jogo simplificado, sem sessão nem placar.
        funcao = getattr(self.jogo, metodo, None)
        if funcao is not None:
            funcao(*args)

    def _salvar_se_mudou(self):
        """Salva a sessão a cada troca de turno."""
        if self.partida.jogadas != self._jogadas_salvas:
            self._jogadas_salvas = self.partida.jogadas
            self._chamar_jogo("salvar_sessao")

    def _vez_do_humano(self) -> bool:
        return not self.partida.encerrada and self.partida.jogador_atual is self.humano

    def _som(self, evento):
        audio = getattr(self.jogo, "audio", None)
        if audio is not None:
            audio.tocar_efeito(evento)

    def _mostrar_aviso(self, texto):
        self.aviso = texto
        self.tempo_aviso = DURACAO_AVISO

    # --- Layout ------------------------------------------------------------

    def _layout_mesa(self):
        """Posição de cada jogo e carta da mesa, e da área de novo jogo."""
        area = self.rect_mesa.inflate(-28, -28)
        altura_linha = CartaSprite.ALTURA + 16
        jogos = self.partida.mesa.jogos

        for passo in PASSOS_MESA:
            grupos = []
            x, y = area.x, area.y
            larguras = [CartaSprite.LARGURA + passo * (len(jogo) - 1) for jogo in jogos]
            larguras.append(CartaSprite.LARGURA)  # área de novo jogo
            posicoes = []
            for largura in larguras:
                if x + largura > area.right and x > area.x:
                    x, y = area.x, y + altura_linha
                posicoes.append((x, y))
                x += largura + 24
            if y + CartaSprite.ALTURA <= area.bottom:
                break

        for indice, jogo in enumerate(jogos):
            x, y = posicoes[indice]
            cartas_jogo = [
                (carta, pygame.Rect(x + i * passo, y, CartaSprite.LARGURA, CartaSprite.ALTURA))
                for i, carta in enumerate(ordenar_jogo(jogo))
            ]
            rect = pygame.Rect(x, y, larguras[indice], CartaSprite.ALTURA).inflate(12, 12)
            grupos.append({"indice": indice, "jogo": jogo, "rect": rect, "cartas": cartas_jogo})

        novo = pygame.Rect(*posicoes[-1], CartaSprite.LARGURA, CartaSprite.ALTURA)
        return grupos, novo

    def _layout_mao(self):
        mao = self.humano.mao
        largura_util = self.rect_mao.width - CartaSprite.LARGURA
        espacamento = min(CartaSprite.LARGURA + 6, largura_util // max(1, len(mao) - 1))
        total = espacamento * (len(mao) - 1) + CartaSprite.LARGURA
        inicio = self.rect_mao.centerx - total // 2
        y = self.jogo.altura - CartaSprite.ALTURA - 20
        return [
            (carta, pygame.Rect(inicio + i * espacamento, y, CartaSprite.LARGURA, CartaSprite.ALTURA))
            for i, carta in enumerate(mao)
        ]

    def _alvo(self, posicao):
        """Onde uma carta arrastada cairia: ("mao",), ("novo",), ("jogo", grupo) ou None."""
        if self.rect_mao.collidepoint(posicao):
            return ("mao",)
        if not self._vez_do_humano():
            return None
        grupos, novo = self._layout_mesa()
        if novo.inflate(12, 12).collidepoint(posicao):
            return ("novo",)
        for grupo in grupos:
            if grupo["rect"].collidepoint(posicao):
                return ("jogo", grupo)
        return None

    def _origem_monte(self):
        return (self.rect_monte.centerx - CartaSprite.LARGURA // 2, self.rect_monte.y + 40)

    def _origem_assento(self, jogador):
        assento = rects_assentos(self.partida)[self.partida.jogadores.index(jogador)]
        return (assento.centerx - CartaSprite.LARGURA // 2, assento.centery - CartaSprite.ALTURA // 2)

    def _posicoes(self):
        """Carta e retângulo atual de cada carta visível (mão do humano e mesa)."""
        posicoes = {id(carta): (carta, rect) for carta, rect in self._layout_mao()}
        grupos, _ = self._layout_mesa()
        for grupo in grupos:
            for carta, rect in grupo["cartas"]:
                posicoes[id(carta)] = (carta, rect)
        return posicoes

    def _animar(self, acao, origem_nova=None, origens=None, escalonamento=0.0):
        """Executa `acao` e faz as cartas que mudaram de lugar deslizarem até ele.

        Cartas que não estavam visíveis antes saem de `origem_nova`, uma após a
        outra se houver `escalonamento`. `origens` substitui a posição inicial
        de cartas específicas (por exemplo, onde uma carta arrastada foi solta).
        """
        antes = self._posicoes()
        for chave, (carta, rect) in antes.items():
            voo = self.animacoes.voo_de(carta)
            if voo is not None and voo.iniciado:
                antes[chave] = (carta, pygame.Rect(voo.posicao(rect.topleft), rect.size))
        antes.update(origens or {})

        resultado = acao()

        atraso = 0.0
        for chave, (carta, rect) in self._posicoes().items():
            anterior = antes.get(chave)
            if anterior is None and origem_nova is not None:
                self.animacoes.adicionar(Voo(carta, origem_nova, atraso=atraso))
                atraso += escalonamento
            elif anterior is not None and anterior[1].topleft != rect.topleft:
                self.animacoes.adicionar(Voo(carta, anterior[1].topleft))
        return resultado

    def _carta_sob_mouse_na_mao(self):
        if self.arrasto is not None or self.partida.encerrada:
            return None
        posicao = pygame.mouse.get_pos()
        for carta, rect in reversed(self._layout_mao()):
            if rect.collidepoint(posicao):
                return carta
        return None

    # --- Eventos -----------------------------------------------------------

    def tratar_evento(self, evento):
        if self.menu.clicado(evento):
            self.jogo.trocar_tela("menu")
            return

        if self.partida.encerrada:
            if self.jogar_novamente.clicado(evento):
                self.jogo.trocar_tela("gameplay")
            elif self.voltar_menu.clicado(evento):
                self.jogo.trocar_tela("menu")
            return

        self._atualizar_botoes()
        if self.comprar.clicado(evento):
            self._comprar()
        elif self.desfazer.clicado(evento):
            self._animar(self.partida.desfazer_turno)
            self._som("baixar")
            self._mostrar_aviso("Jogada desfeita.")
        elif self.finalizar.clicado(evento):
            self._finalizar()
        elif self.ordenar.clicado(evento):
            self._animar(self.humano.ordenar_mao)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self._iniciar_arrasto(evento.pos)
        elif evento.type == pygame.MOUSEMOTION and self.arrasto is not None:
            self.arrasto["pos"] = evento.pos
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and self.arrasto:
            self._soltar(evento.pos)

    def _comprar(self):
        carta = self._animar(self.partida.comprar, origem_nova=self._origem_monte())
        self._som("comprar")
        if carta is not None:
            self._mostrar_aviso(f"Você comprou {carta}.")

    def _finalizar(self):
        motivo = self.partida.motivo_bloqueio()
        if motivo is not None:
            self._som("invalido")
            self._mostrar_aviso(motivo)
            return
        self.partida.finalizar_turno()
        self._som("confirmar")
        self._mostrar_aviso("Jogada confirmada.")

    def _iniciar_arrasto(self, posicao):
        candidatos = [("mao", carta, rect) for carta, rect in self._layout_mao()]
        if self._vez_do_humano():
            grupos, _ = self._layout_mesa()
            candidatos = [
                ("mesa", carta, rect) for grupo in grupos for carta, rect in grupo["cartas"]
            ] + candidatos
        # A última carta desenhada fica por cima, então a busca é de trás para frente.
        for origem, carta, rect in reversed(candidatos):
            if rect.collidepoint(posicao):
                self.animacoes.cancelar(carta)
                self.arrasto = {
                    "carta": carta,
                    "origem": origem,
                    "offset": (posicao[0] - rect.x, posicao[1] - rect.y),
                    "pos": posicao,
                }
                return

    def _soltar(self, posicao):
        """Aplica a soltura; a carta desliza de onde foi solta até o novo lugar
        (ou de volta, se a jogada não mudou nada)."""
        carta = self.arrasto["carta"]
        solta = pygame.Rect(
            posicao[0] - self.arrasto["offset"][0],
            posicao[1] - self.arrasto["offset"][1],
            CartaSprite.LARGURA,
            CartaSprite.ALTURA,
        )
        efeito = self._animar(
            lambda: self._aplicar_soltura(posicao), origens={id(carta): (carta, solta)}
        )
        self.arrasto = None
        if efeito is not None:
            self._som(efeito)

    def _aplicar_soltura(self, posicao):
        """Move a carta conforme o alvo; retorna o efeito sonoro a tocar, se houver."""
        carta, origem = self.arrasto["carta"], self.arrasto["origem"]
        alvo = self._alvo(posicao)
        if alvo is None:
            return None

        if alvo[0] == "mao":
            indice = sum(
                1
                for outra, rect in self._layout_mao()
                if outra is not carta and rect.centerx < posicao[0]
            )
            if origem == "mao":
                self.humano.mover_na_mao(carta, indice)
                return None
            if not self.partida.mover_carta(carta, MAO, indice):
                self._mostrar_aviso("Só cartas que você baixou neste turno podem voltar para a mão.")
                return "invalido"
            return "baixar"
        if alvo[0] == "novo":
            return "baixar" if self.partida.mover_carta(carta, NOVO_JOGO) else None
        if any(atual is carta for atual in alvo[1]["jogo"]):
            return None
        return "baixar" if self.partida.mover_carta(carta, alvo[1]["indice"]) else None

    # --- Atualização -------------------------------------------------------

    def _atualizar_botoes(self):
        vez = self._vez_do_humano()
        baixou = vez and bool(self.partida.cartas_baixadas())
        self.comprar.ativo = vez and self.partida.pode_comprar()
        self.desfazer.ativo = vez and (baixou or self.partida.mesa_alterada())
        self.finalizar.ativo = baixou

    def atualizar(self, dt):
        self._atualizar_partida(dt)
        self._salvar_se_mudou()

    def _atualizar_partida(self, dt):
        self.tempo += dt
        self.animacoes.atualizar(dt)
        if self.tempo_aviso > 0:
            self.tempo_aviso = max(0.0, self.tempo_aviso - dt)
        if self.tempo_destaque_bot > 0:
            self.tempo_destaque_bot = max(0.0, self.tempo_destaque_bot - dt)
            if self.tempo_destaque_bot == 0:
                self.destaques_bot = []
        self._atualizar_botoes()

        if self.partida.encerrada and not self.fim_anunciado:
            self.fim_anunciado = True
            self._chamar_jogo("registrar_fim", self.partida)
            self._som("vitoria" if self.humano in self.partida.vencedores else "derrota")

        bot = self.partida.jogador_atual
        if self.partida.encerrada or not bot.eh_bot:
            self.tempo_bot = 0.0
            return
        if self.animacoes.ativas:
            return
        self.tempo_bot += dt
        if self.tempo_bot < ATRASO_BOT:
            return
        self.tempo_bot = 0.0
        na_mesa = {id(carta) for jogo in self.partida.mesa.jogos for carta in jogo}
        baixadas = self._animar(
            lambda: bot.jogar_turno(self.partida),
            origem_nova=self._origem_assento(bot),
            escalonamento=ESCALONAMENTO_BOT,
        )
        self._som("baixar" if baixadas else "comprar")
        if not baixadas and not self.partida.encerrada:
            # A carta comprada vai virada para o assento do bot.
            self.animacoes.adicionar(Voo(None, self._origem_monte(), self._origem_assento(bot)))
        if baixadas:
            self.destaques_bot = [
                carta
                for jogo in self.partida.mesa.jogos
                for carta in jogo
                if id(carta) not in na_mesa
            ]
            self.tempo_destaque_bot = DURACAO_DESTAQUE_BOT
            self._mostrar_aviso(f"{bot.nome} baixou {cartas(baixadas)}.")
        else:
            self._mostrar_aviso(f"{bot.nome} comprou uma carta.")

    # --- Desenho -----------------------------------------------------------

    def _desenhar_monte(self, tela):
        rect = self.rect_monte
        desenho.painel_rebaixado(tela, rect)
        desenho.texto(tela, "MONTE", tema.fonte("seminegrito", 13), tema.TEXTO_SUAVE,
                      midtop=(rect.centerx, rect.y + 10))

        restantes = len(self.partida.baralho)
        x_carta = rect.centerx - CartaSprite.LARGURA // 2
        y_carta = rect.y + 40
        if restantes:
            # Algumas camadas dão volume à pilha e diminuem conforme ela acaba.
            camadas = min(4, (restantes + 19) // 20)
            for camada in range(camadas - 1, -1, -1):
                CartaSprite.desenhar_verso(tela, x_carta, y_carta - camada * 2)
        else:
            vazio = pygame.Rect(x_carta, y_carta, CartaSprite.LARGURA, CartaSprite.ALTURA)
            desenho.contorno_tracejado(tela, tema.TEXTO_INATIVO, vazio)
        desenho.texto(tela, str(restantes), tema.fonte("seminegrito", 20), tema.TEXTO,
                      midbottom=(rect.centerx, rect.bottom - 6))

    def _desenhar_mesa(self, tela):
        desenho.painel_rebaixado(tela, self.rect_mesa)

        vez = self._vez_do_humano()
        arrastada = self.arrasto["carta"] if self.arrasto else None
        alvo = self._alvo(self.arrasto["pos"]) if self.arrasto else None
        grupos, novo = self._layout_mesa()

        for grupo in grupos:
            desenho.painel(tela, grupo["rect"], (255, 255, 255), raio=10, alpha=14)
            if alvo is not None and alvo[0] == "jogo" and alvo[1]["indice"] == grupo["indice"]:
                desenho.contorno_brilhante(tela, grupo["rect"], tema.ACENTO, 10)
            elif not validar_jogo(grupo["jogo"]):
                desenho.contorno_brilhante(tela, grupo["rect"], tema.COR_JOGO_INVALIDO, 10)
            for carta, rect in grupo["cartas"]:
                if carta is arrastada or self.animacoes.voo_de(carta) is not None:
                    continue
                if vez and self.partida.veio_da_mao(carta):
                    destaque = tema.COR_DESTAQUE
                elif any(carta is outra for outra in self.destaques_bot):
                    destaque = tema.COR_DESTAQUE_BOT
                else:
                    destaque = None
                CartaSprite.desenhar(tela, carta, rect.x, rect.y, destaque=destaque)

        if vez:
            sobre = alvo is not None and alvo[0] == "novo"
            cor = tema.ACENTO if sobre else tema.TEXTO_INATIVO
            if sobre:
                desenho.brilho(tela, novo, tema.ACENTO, tema.RAIO_CARTA)
            desenho.contorno_tracejado(tela, cor, novo)
            desenho.texto(tela, "+", tema.fonte("regular", 30), cor,
                          center=(novo.centerx, novo.centery - 12))
            desenho.texto(tela, "Novo jogo", tema.fonte("seminegrito", 12), cor,
                          center=(novo.centerx, novo.centery + 16))

    def _desenhar_mao(self, tela):
        arrastada = self.arrasto["carta"] if self.arrasto else None
        sob_mouse = self._carta_sob_mouse_na_mao()
        for carta, rect in self._layout_mao():
            if carta is arrastada or self.animacoes.voo_de(carta) is not None:
                continue
            elevacao = tema.ELEVACAO_HOVER if carta is sob_mouse else 0
            CartaSprite.desenhar(tela, carta, rect.x, rect.y, elevacao=elevacao)

    def _desenhar_voos(self, tela):
        posicoes = self._posicoes()
        for voo in self.animacoes.voos:
            if not voo.iniciado:
                continue
            if voo.carta is None:
                x, y = voo.posicao(voo.destino)
                CartaSprite.desenhar_verso(tela, x, y)
                continue
            atual = voo.destino or (posicoes[id(voo.carta)][1].topleft if id(voo.carta) in posicoes else None)
            if atual is None:
                continue
            x, y = voo.posicao(atual)
            do_bot = any(voo.carta is outra for outra in self.destaques_bot)
            destaque = tema.COR_DESTAQUE_BOT if do_bot else None
            # Desenhada levemente elevada: mesma posição, sombra maior.
            CartaSprite.desenhar(tela, voo.carta, x, y + 6, destaque=destaque, elevacao=6)

    def _desenhar_arrasto(self, tela):
        if self.arrasto is None:
            return
        x = self.arrasto["pos"][0] - self.arrasto["offset"][0]
        y = self.arrasto["pos"][1] - self.arrasto["offset"][1]
        CartaSprite.desenhar(tela, self.arrasto["carta"], x, y, selecionada=True)

    def _desenhar_status(self, tela):
        """Mensagem em uma pílula no topo; avisos aparecem e somem suavemente."""
        if self.tempo_aviso > 0:
            texto, cor = self.aviso, tema.ACENTO
            alpha = min(1.0, self.tempo_aviso / 0.3, (DURACAO_AVISO - self.tempo_aviso) / 0.15)
        elif self.partida.encerrada:
            texto, cor, alpha = "Fim de jogo", tema.TEXTO_SUAVE, 1.0
        elif self._vez_do_humano():
            texto = "Sua vez: arraste cartas para a mesa e finalize a jogada, ou compre."
            cor, alpha = tema.TEXTO_SUAVE, 1.0
        else:
            texto, cor, alpha = f"Vez de {self.partida.jogador_atual.nome}...", tema.TEXTO_SUAVE, 1.0

        imagem = tema.fonte("regular", 15).render(texto, True, cor)
        pilula = pygame.Surface((imagem.get_width() + 36, imagem.get_height() + 10), pygame.SRCALPHA)
        desenho.painel(pilula, pilula.get_rect(), (0, 0, 0), raio=pilula.get_height() // 2, alpha=95)
        pilula.blit(imagem, imagem.get_rect(center=pilula.get_rect().center))
        pilula.set_alpha(round(255 * max(0.0, alpha)))
        tela.blit(pilula, pilula.get_rect(center=(self.jogo.largura // 2, 85)))

    def _desenhar_resultado(self, tela):
        sombra = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 165))
        tela.blit(sombra, (0, 0))

        partida = self.partida
        painel = pygame.Rect(0, 0, 540, 230 + 36 * len(partida.resultado))
        painel.midbottom = (self.jogo.largura // 2, self.jogar_novamente.rect.bottom + 28)
        desenho.sombra(tela, painel, 20, (0, 10), desfoque=16, alpha=150)
        desenho.painel(tela, painel, tema.SUPERFICIE, raio=20, borda=tema.escurecer(tema.ACENTO, 0.3))

        nomes = [jogador.nome for jogador in partida.vencedores]
        if len(nomes) > 1:
            titulo = "Empate: " + ", ".join(nomes)
        elif partida.vencedor is self.humano:
            titulo = "Você venceu!"
        else:
            titulo = f"{nomes[0]} venceu!"
        if partida.monte_esgotado:
            subtitulo = "Monte esgotado: vence quem tem menos pontos na mão."
        else:
            subtitulo = f"{partida.vencedor.nome} ficou sem cartas."

        desenho.texto(tela, titulo, tema.fonte("negrito", tema.TAMANHO_TITULO), tema.ACENTO,
                      midtop=(painel.centerx, painel.y + 22))
        desenho.texto(tela, subtitulo, tema.fonte("regular", tema.TAMANHO_PEQUENO), tema.TEXTO_SUAVE,
                      midtop=(painel.centerx, painel.y + 80))

        colunas = (("midleft", painel.x + 36), ("center", painel.centerx + 50), ("midright", painel.right - 36))
        y = painel.y + 128
        cabecalho = tema.fonte("seminegrito", 12)
        for texto, (ancora, x) in zip(("JOGADOR", "CARTAS", "PONTOS"), colunas):
            desenho.texto(tela, texto, cabecalho, tema.TEXTO_INATIVO, **{ancora: (x, y)})

        for i, jogador in enumerate(partida.resultado):
            y = painel.y + 162 + i * 36
            venceu = jogador in partida.vencedores
            if venceu:
                faixa = pygame.Rect(painel.x + 20, y - 16, painel.width - 40, 32)
                desenho.painel(tela, faixa, tema.ACENTO, raio=8, alpha=40)
            fonte = tema.fonte("seminegrito" if venceu else "regular", 17)
            cor = tema.ACENTO if venceu else tema.TEXTO
            valores = (f"{i + 1}. {jogador.nome}", cartas(len(jogador.mao)), f"{jogador.pontos} pts")
            for texto, (ancora, x) in zip(valores, colunas):
                desenho.texto(tela, texto, fonte, cor, **{ancora: (x, y)})

        self.jogar_novamente.desenhar(tela)
        self.voltar_menu.desenhar(tela)

    def desenhar(self, tela):
        tema.desenhar_fundo(tela)
        desenhar_assentos(tela, self.partida, self.tempo)
        self.menu.desenhar(tela)
        self._desenhar_status(tela)
        self._desenhar_monte(tela)
        self._desenhar_mesa(tela)
        for botao in (self.comprar, self.desfazer, self.finalizar, self.ordenar):
            botao.desenhar(tela)
        self._desenhar_mao(tela)
        self._desenhar_voos(tela)
        self._desenhar_arrasto(tela)
        if self.partida.encerrada:
            self._desenhar_resultado(tela)
