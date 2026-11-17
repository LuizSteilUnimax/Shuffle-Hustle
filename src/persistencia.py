"""Partida em andamento e placar salvos em disco, em JSON.

Os arquivos ficam na pasta de dados do usuário (veja pasta_dados()); a variável
de ambiente MEXE_MEXE_DADOS troca essa pasta, o que os testes usam. Falhas de
leitura ou escrita nunca derrubam o jogo: a partida apenas deixa de ser salva.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from .entidades.partida import Partida

ARQUIVO_SESSAO = "sessao.json"
ARQUIVO_PLACAR = "placar.json"
LIMITE_PLACAR = 200


def pasta_dados() -> Path:
    if os.environ.get("MEXE_MEXE_DADOS"):
        return Path(os.environ["MEXE_MEXE_DADOS"])
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home())
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "mexe-mexe"


def _ler(nome):
    try:
        with open(pasta_dados() / nome, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (OSError, ValueError):
        return None


def _escrever(nome, dados) -> bool:
    """Grava em um arquivo temporário e troca de uma vez, para nunca deixar
    um arquivo pela metade se o jogo fechar durante a escrita."""
    caminho = pasta_dados() / nome
    temporario = caminho.with_suffix(".tmp")
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False)
        os.replace(temporario, caminho)
        return True
    except OSError:
        return False


# --- Partida em andamento --------------------------------------------------

def salvar_sessao(partida) -> bool:
    return _escrever(ARQUIVO_SESSAO, partida.para_dict())


def carregar_sessao():
    """A partida salva, ou None se não houver uma (ou se o arquivo for inválido)."""
    dados = _ler(ARQUIVO_SESSAO)
    if dados is None:
        return None
    try:
        return Partida.de_dict(dados)
    except (KeyError, IndexError, TypeError, ValueError, AttributeError, ZeroDivisionError):
        return None


def apagar_sessao() -> None:
    try:
        (pasta_dados() / ARQUIVO_SESSAO).unlink(missing_ok=True)
    except OSError:
        pass


# --- Placar -------------------------------------------------------------------

def registrar_resultado(partida, data=None) -> dict:
    """Acrescenta uma partida encerrada ao placar e devolve o registro."""
    registro = {
        "data": (data or datetime.now()).isoformat(timespec="minutes"),
        "rodadas": partida.rodada,
        "monte_esgotado": partida.monte_esgotado,
        "jogadores": [
            {"nome": j.nome, "bot": j.eh_bot, "cartas": len(j.mao), "pontos": j.pontos}
            for j in partida.jogadores
        ],
        "vencedores": [j.nome for j in partida.vencedores],
    }
    placar = [registro] + carregar_placar()
    _escrever(ARQUIVO_PLACAR, placar[:LIMITE_PLACAR])
    return registro


def carregar_placar():
    """Partidas registradas, da mais recente para a mais antiga."""
    dados = _ler(ARQUIVO_PLACAR)
    if not isinstance(dados, list):
        return []
    return [r for r in dados if isinstance(r, dict) and isinstance(r.get("jogadores"), list)]


def humano(registro):
    return next((j for j in registro["jogadores"] if not j.get("bot")), None)


def resultado_humano(registro) -> str:
    """"vitoria", "empate" ou "derrota" do ponto de vista do jogador humano."""
    jogador = humano(registro)
    vencedores = registro.get("vencedores", [])
    if jogador is None or jogador["nome"] not in vencedores:
        return "derrota"
    return "vitoria" if len(vencedores) == 1 else "empate"


def colocacao(registro) -> int:
    """Posição do humano por pontos; empatados dividem a posição."""
    jogador = humano(registro)
    if jogador is None:
        return len(registro["jogadores"])
    return 1 + sum(1 for j in registro["jogadores"] if j["pontos"] < jogador["pontos"])


def resumo(placar) -> dict:
    resultados = [resultado_humano(r) for r in placar]
    maior = atual = 0
    for resultado in reversed(resultados):  # da mais antiga para a mais recente
        atual = atual + 1 if resultado == "vitoria" else 0
        maior = max(maior, atual)
    partidas = len(resultados)
    vitorias = resultados.count("vitoria")
    return {
        "partidas": partidas,
        "vitorias": vitorias,
        "empates": resultados.count("empate"),
        "derrotas": resultados.count("derrota"),
        "aproveitamento": round(100 * vitorias / partidas) if partidas else 0,
        "maior_sequencia": maior,
    }
