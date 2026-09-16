# Mexe-Mexe

Projeto acadêmico em Python e Pygame, organizado conforme o modelo da disciplina.

## Executar

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Estrutura

- `assets/`: imagens, sons e fundos.
- `src/entidades/`: cartas, baralho, jogadores e partida.
- `src/regras/`: validação de trincas, sequências e mesa.
- `src/mundo/`: estado da mesa.
- `src/ui/`: telas, HUD, botões e representação visual das cartas.
- `src/jogo.py`: loop principal e troca de telas.
- `main.py`: ponto de entrada.

A implementação atual é uma base executável. O fluxo Menu, Configurações e Gameplay funciona, assim como criação do baralho, distribuição, compra e alternância de turnos. A manipulação interativa dos jogos da mesa será acrescentada nas próximas etapas.
