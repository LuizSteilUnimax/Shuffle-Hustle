from .baralho import Baralho
from .bot import Bot
from .carta import Carta
from .jogador import Jogador
from ..mundo.mesa import Mesa

# Destinos especiais para Partida.mover_carta.
NOVO_JOGO = "novo_jogo"
MAO = "mao"


def _contem(cartas, carta) -> bool:
    return any(atual is carta for atual in cartas)


def _remover(cartas, carta) -> None:
    del cartas[next(i for i, atual in enumerate(cartas) if atual is carta)]


class Partida:
    """Estado de uma partida de Mexe-Mexe.

    Durante o turno a mesa funciona como área de trabalho: o jogador da vez
    move cartas livremente e a validação acontece só em finalizar_turno().
    desfazer_turno() devolve mesa e mão ao estado do início do turno.
    """

    def __init__(self, jogadores=None, cartas_iniciais=9, baralho=None):
        self.baralho = Baralho() if baralho is None else baralho
        self.mesa = Mesa()
        self.jogadores = list(jogadores) if jogadores else [Jogador("Jogador")]
        self.cartas_iniciais = cartas_iniciais
        self.indice_atual = 0
        self.jogadas = 0
        self.encerrada = False
        self.monte_esgotado = False
        self.resultado = []
        self.vencedores = []
        self._mesa_inicio = []
        self._mao_inicio = []

    @property
    def jogador_atual(self):
        return self.jogadores[self.indice_atual]

    @property
    def vencedor(self):
        return self.vencedores[0] if self.vencedores else None

    @property
    def rodada(self) -> int:
        """Rodada atual, contando a partir de 1 (uma rodada = todos jogaram)."""
        return self.jogadas // len(self.jogadores) + 1

    def iniciar(self) -> None:
        for _ in range(self.cartas_iniciais):
            for jogador in self.jogadores:
                jogador.receber(self.baralho.comprar())
        for jogador in self.jogadores:
            jogador.ordenar_mao()
        self._iniciar_turno()

    def _iniciar_turno(self) -> None:
        self._mesa_inicio = self.mesa.snapshot()
        self._mao_inicio = list(self.jogador_atual.mao)

    def _proximo_turno(self) -> None:
        self.indice_atual = (self.indice_atual + 1) % len(self.jogadores)
        self.jogadas += 1
        self._iniciar_turno()

    # --- Estado do turno -------------------------------------------------

    def cartas_baixadas(self):
        """Cartas que saíram da mão do jogador da vez neste turno."""
        mao = self.jogador_atual.mao
        return [carta for carta in self._mao_inicio if not _contem(mao, carta)]

    def veio_da_mao(self, carta) -> bool:
        return _contem(self._mao_inicio, carta)

    def mesa_alterada(self) -> bool:
        def assinatura(jogos):
            return sorted(sorted(map(id, jogo)) for jogo in jogos)
        return assinatura(self.mesa.jogos) != assinatura(self._mesa_inicio)

    def motivo_bloqueio(self):
        """Por que o turno ainda não pode ser finalizado, ou None."""
        if not self.cartas_baixadas():
            return "Baixe ao menos uma carta da mão ou compre."
        if not self.mesa.esta_valida():
            return "Todos os jogos da mesa precisam ser válidos, com 3 ou mais cartas."
        return None

    def pode_finalizar(self) -> bool:
        return not self.encerrada and self.motivo_bloqueio() is None

    def pode_comprar(self) -> bool:
        return not self.encerrada and not self.cartas_baixadas()

    # --- Ações -----------------------------------------------------------

    def _localizar(self, carta):
        if _contem(self.jogador_atual.mao, carta):
            return self.jogador_atual.mao
        return next((jogo for jogo in self.mesa.jogos if _contem(jogo, carta)), None)

    def mover_carta(self, carta, destino, posicao=None) -> bool:
        """Move uma carta da mão ou da mesa para um jogo, um novo jogo ou a mão.

        `destino` é o índice de um jogo da mesa, NOVO_JOGO ou MAO. Só voltam
        para a mão cartas que estavam nela no início do turno.
        """
        if self.encerrada:
            return False
        origem = self._localizar(carta)
        if origem is None:
            return False

        if destino == MAO:
            if not self.veio_da_mao(carta):
                return False
            alvo = self.jogador_atual.mao
        elif destino == NOVO_JOGO:
            alvo = None
        elif isinstance(destino, int) and 0 <= destino < len(self.mesa.jogos):
            alvo = self.mesa.jogos[destino]
        else:
            return False

        _remover(origem, carta)
        if alvo is None:
            self.mesa.jogos.append([carta])
        elif posicao is None:
            alvo.append(carta)
        else:
            alvo.insert(posicao, carta)
        self.mesa.jogos[:] = [jogo for jogo in self.mesa.jogos if jogo]
        return True

    def mover_para_novo_jogo(self, cartas) -> bool:
        cartas = list(cartas)
        if not cartas or not self.mover_carta(cartas[0], NOVO_JOGO):
            return False
        novo = self.mesa.jogos[-1]
        for carta in cartas[1:]:
            indice = next(i for i, jogo in enumerate(self.mesa.jogos) if jogo is novo)
            self.mover_carta(carta, indice)
        return True

    def desfazer_turno(self) -> None:
        baixadas = self.cartas_baixadas()
        self.mesa.restaurar(self._mesa_inicio)
        self.jogador_atual.mao.extend(baixadas)

    def finalizar_turno(self) -> bool:
        if not self.pode_finalizar():
            return False
        if self.jogador_atual.venceu():
            self._encerrar()
        else:
            self._proximo_turno()
        return True

    def comprar(self):
        """Compra uma carta e passa o turno.

        Rearranjos da mesa sem cartas baixadas são desfeitos. Quando a última
        carta do monte é comprada, ela entra na mão de quem comprou e a partida
        termina pela contagem de pontos.
        """
        if not self.pode_comprar():
            return None
        self.desfazer_turno()
        carta = self.baralho.comprar()
        self.jogador_atual.receber(carta)
        if not len(self.baralho):
            self.monte_esgotado = True
            self._encerrar()
        else:
            self._proximo_turno()
        return carta

    def _encerrar(self) -> None:
        self.encerrada = True
        for jogador in self.jogadores:
            jogador.pontos = jogador.pontos_na_mao()
        self.resultado = sorted(self.jogadores, key=lambda jogador: jogador.pontos)
        menor = self.resultado[0].pontos
        self.vencedores = [j for j in self.resultado if j.pontos == menor]

    # --- Persistência ----------------------------------------------------

    def para_dict(self) -> dict:
        """Estado completo da partida em andamento, inclusive o turno em curso.

        As cartas são comparadas por identidade (há cartas repetidas com dois
        baralhos), então cada objeto vira um índice em uma lista de cartas.
        """
        cartas, indices = [], {}

        def refs(lista):
            resultado = []
            for carta in lista:
                if id(carta) not in indices:
                    indices[id(carta)] = len(cartas)
                    cartas.append([carta.valor, carta.naipe])
                resultado.append(indices[id(carta)])
            return resultado

        dados = {
            "versao": 1,
            "monte": refs(self.baralho.cartas),
            "jogadores": [
                {"nome": jogador.nome, "bot": jogador.eh_bot, "mao": refs(jogador.mao)}
                for jogador in self.jogadores
            ],
            "mesa": [refs(jogo) for jogo in self.mesa.jogos],
            "indice_atual": self.indice_atual,
            "jogadas": self.jogadas,
            "mesa_inicio": [refs(jogo) for jogo in self._mesa_inicio],
            "mao_inicio": refs(self._mao_inicio),
        }
        dados["cartas"] = cartas
        return dados

    @classmethod
    def de_dict(cls, dados) -> "Partida":
        """Recria uma partida salva por para_dict(). Erros de formato propagam."""
        if dados.get("versao") != 1:
            raise ValueError("Versão de partida salva desconhecida.")
        cartas = [Carta(valor, naipe) for valor, naipe in dados["cartas"]]
        if any(c.valor not in Carta.ORDEM or c.naipe not in Baralho.NAIPES for c in cartas):
            raise ValueError("Carta desconhecida na partida salva.")

        def objetos(indices):
            return [cartas[i] for i in indices]

        jogadores = []
        for info in dados["jogadores"]:
            jogador = (Bot if info["bot"] else Jogador)(info["nome"])
            jogador.mao = objetos(info["mao"])
            jogadores.append(jogador)

        baralho = Baralho(0)
        baralho.cartas = objetos(dados["monte"])
        partida = cls(jogadores, cartas_iniciais=0, baralho=baralho)
        partida.mesa.jogos = [objetos(jogo) for jogo in dados["mesa"]]
        partida.indice_atual = dados["indice_atual"] % len(jogadores)
        partida.jogadas = dados["jogadas"]
        partida._mesa_inicio = [objetos(jogo) for jogo in dados["mesa_inicio"]]
        partida._mao_inicio = objetos(dados["mao_inicio"])
        return partida
