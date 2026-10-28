# Mexe-Mexe

Projeto acadêmico em Python e Pygame para uma versão digital do jogo de cartas
Mexe-Mexe. A interface usa componentes de desenho independentes da lógica, para
que imagens e sprites de cartas possam ser adicionados sem alterar as regras.

## Executar

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

A janela pode ser redimensionada; F11 alterna a tela cheia.

## Som

Todo áudio é opcional: arquivos ausentes apenas deixam aquele som em silêncio.

- `assets/sounds/loop-ambiance.mp3` e `loop-soundtrack.mp3`: música da partida.
- Outros arquivos de áudio em `assets/sounds/`: música do menu (uma é sorteada).
- `assets/sounds/efeitos/<evento>.ogg` (ou `.wav`/`.mp3`): efeitos, com os eventos
  `comprar`, `baixar`, `invalido`, `confirmar`, `vitoria` e `derrota`.

Use apenas áudio com licença livre, já que o repositório é público.

## Estrutura

- `assets/`: recursos de imagem e áudio opcionais usados pelo projeto.
- `src/entidades/`: cartas, baralho, jogadores e partida.
- `src/regras/`: validação de trincas, sequências e mesa.
- `src/mundo/`: estado da mesa.
- `src/ui/`: telas, HUD, botões e representação visual das cartas.
- `src/jogo.py`: loop principal e troca de telas.
- `main.py`: ponto de entrada.

A implementação inclui menu, configurações (brilho e número de bots),
partida contra 1 a 3 bots, rearranjo livre da mesa durante o turno, compra,
fim de jogo e contagem de pontos.

## Regras implementadas

- Baralho com dois conjuntos comuns de 52 cartas, sem coringas; 9 cartas por
  jogador.
- Trincas têm pelo menos três cartas do mesmo valor; naipes podem se repetir.
- Sequências têm pelo menos três cartas consecutivas do mesmo naipe. O ás pode
  ser baixo (A-2-3) ou alto (Q-K-A), sem dar a volta.
- No turno, o jogador rearranja a mesa livremente. Para finalizar, precisa ter
  baixado ao menos uma carta da mão e deixar todos os jogos válidos. Quem não
  baixa nada compra uma carta, o que encerra o turno.
- Vence quem ficar sem cartas. Quando a última carta do monte é comprada (ela
  conta para quem a comprou), vence quem tiver menos pontos na mão (cartas numéricas pelo valor; J=11, Q=12, K=13, A=14).

## Arte

Imagens de cartas e fundo podem ser colocadas em `assets/` e são usadas
automaticamente; veja `src/ui/tema.py` para os nomes de arquivo.

Consulte `my-website/docs/regras.mdx` para a descrição completa.
