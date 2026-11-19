## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch, commit, pull request conventions.

## Labirinto interativo (pygame)

Interface gráfica que anima os algoritmos do grupo (`src/graphs/`) sobre os mapas.
Ela **não reimplementa** nenhum algoritmo: só chama `build_g_est`, `bfs`, `dfs`,
`dijkstra`, `bellman_ford`, `find_trap_states` e `analyze_layers` e anima o resultado.

### Instalação

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
```

### Execução (sempre a partir da raiz do repositório)

```bash
python -m src.frontend                              # abre no m03
python -m src.frontend --mapa caminho/surpresa.txt  # abre direto um mapa (ex.: mapa surpresa)
python -m src.frontend --editor                     # abre no editor de mapas
```

Também dá para **arrastar um `.txt` para a janela** para abrir um mapa novo.

### O que tem

- Escolha de mapa (`data/mapas/` + `data/mapas_grupo/`) e de algoritmo (BFS, Dijkstra, Bellman-Ford, DFS).
- Animação passo a passo com posição, chaves, bônus consumidos, custo acumulado e o rótulo `(l,c)|chaves|{bônus}`.
- Percurso com **cor por camada** (conjunto de chaves); exportação em PNG para `out/parte1/` (tecla `P`).
- Controle de velocidade, linha do tempo arrastável (com marcas onde muda de camada), passo a passo.
- Três modelagens: grafo de estados × posições com porta = chão × porta = parede.
- Modo exploração (ordem de descoberta), mapa de calor de estados por casa com filtro por camada,
  estados-armadilha, Dijkstra recusando pesos negativos, ciclo negativo do Bellman-Ford em loop.
- Comparação lado a lado de dois algoritmos.
- Painel de métricas (ordem, tamanho, densidade, teto teórico, ocupação, becos, camadas).
- Editor de mapas com validação (`io.py`), análise ao vivo e checklist dos requisitos dos mapas do grupo.

### Atalhos

| Tecla | Ação | Tecla | Ação |
|---|---|---|---|
| `Espaço` | reproduzir/pausar | `1`–`4` | algoritmo |
| `←` `→` | passo (Shift = 10) | `Shift+1`–`4` | algoritmo para comparar |
| `↑` `↓` | velocidade | `M` | modelo do grafo |
| `Home` `End` | início/fim | `X` | exploração |
| `Tab` | próximo mapa | `H` / `L` | mapa de calor / camada |
| `R` | reiniciar | `T` | armadilhas |
| `P` | exportar PNG | `C` | comparar |
| `E` | editor | `F1` | ajuda |
