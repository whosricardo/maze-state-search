# Maze State Search

Projeto acadêmico desenvolvido para a disciplina de Estruturas de Dados e Algoritmos, envolvendo modelagem e análise de grafos.

O projeto está dividido em duas partes principais:

- **Parte 1:** modelagem de mapas como grafos de estados e aplicação de algoritmos de busca e caminho mínimo.
- **Parte 2:** análise da rede de hyperlinks entre comunidades do Reddit utilizando BFS, DFS, Dijkstra e Bellman-Ford, além de análise exploratória e visualização de dados.

## Estrutura do projeto

```text
maze-state-search/
├── data/
│   ├── dataset_parte2/
│   ├── mapas/
│   └── mapas_grupo/
│
├── docs/
│   ├── ai_usage.md
│   ├── discussao_critica.md
│   ├── limitacao_pesos.md
│   ├── nota_analitica_explanatoria1.md
│   ├── nota_analitica_explanatoria2.md
│   ├── nota_analitica_exploratoria1.md
│   ├── nota_analitica_exploratoria2.md
│   ├── pergunta_pesquisa.md
│   └── proposta_dataset.md
│
├── out/
│   ├── parte1/
│   └── parte2/
│
├── src/
│   ├── frontend/
│   ├── graphs/
│   │   ├── algorithms.py
│   │   ├── estados.py
│   │   ├── export.py
│   │   ├── graph.py
│   │   ├── io.py
│   │   └── metrics.py
│   │
│   └── parte2/
│       ├── algorithm_comparison.py
│       ├── benchmark.py
│       ├── benchmark_utils.py
│       ├── eda.py
│       ├── explanatory_visualizations.py
│       ├── inspect_dataset.py
│       ├── loader.py
│       └── visualizations.py
│
├── tests/
├── README.md
└── requirements.txt
```

## Requisitos

- Python 3
- `pip`
- Ambiente virtual recomendado

As dependências utilizadas pelo projeto estão listadas em:

```text
requirements.txt
```

## Instalação

Clone o repositório e acesse sua pasta:

```bash
git clone <URL_DO_REPOSITORIO>
cd maze-state-search
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Testes

Os testes automatizados estão localizados em `tests/`.

Execute todos os testes com:

```bash
pytest
```

ou:

```bash
python -m pytest
```

Os testes cobrem as estruturas de grafo e os principais algoritmos utilizados no projeto, incluindo BFS, DFS, Dijkstra e Bellman-Ford.

## Parte 1 — Grafos de estados

A Parte 1 utiliza os mapas armazenados em:

```text
data/mapas/
```

Os resultados produzidos são armazenados em:

```text
out/parte1/
```

Entre os resultados gerados estão:

- métricas dos grafos;
- graus dos vértices;
- classificação de arestas pela DFS;
- caminhos encontrados;
- análise das camadas;
- detecção de ciclo negativo;
- comparação das modelagens.

### Execução

```bash
python -m src.solve
```

### Interface Pygame

```bash
python -m src.frontend
python -m src.frontend --mapa data/mapas/m03_tres_chaves.txt
python -m src.frontend --editor
```

A capa abre o menu com **Parte 1**, **Parte 2** e **Voltar à capa**. No labirinto,
use o ícone na borda da lateral para abrir a seleção de mapa, modelo do grafo e algoritmo. Use **Comparar os quatro**
para sincronizar os tabuleiros e clique em um deles para ampliá-lo. **Esc** fecha a
ampliação ou retorna ao menu. Abra **Expandir painel** para ajustar a velocidade
e consultar métricas, camadas e graus. Para a demonstração com mapa surpresa,
arraste o arquivo `.txt` para a janela ou use `--mapa caminho/do/mapa.txt`.

A rubrica também exige `out/parte1/labirinto_interativo.html` como entrega da equipe.

## Parte 2 — Reddit Hyperlink Network

O dataset utilizado está localizado em:

```text
data/dataset_parte2/soc-redditHyperlinks-body.tsv
```

Baixe a versão oficial do [Stanford SNAP](https://snap.stanford.edu/data/soc-RedditHyperlinks.html):

```bash
python scripts/download_reddit_dataset.py
```

Na interface, **Casos salvos** e **Figuras e notas** usam os arquivos já registrados
pelo grupo. Abra **Consulta ao vivo** e carregue o dataset para pesquisar comunidades.
BFS e DFS aceitam destino opcional. Dijkstra e Bellman-Ford exigem os dois campos.
O tempo de uma consulta individual aparece separado das médias do benchmark.

Cada registro representa um hyperlink direcionado entre dois subreddits.

Na preparação do grafo, as interações entre o mesmo par direcionado de comunidades são agregadas utilizando o campo `LINK_SENTIMENT`.

O peso agregado utilizado é:

```text
WEIGHT = soma dos valores de LINK_SENTIMENT
```

O grafo resultante é:

- direcionado;
- ponderado;
- composto por subreddits como vértices;
- composto por relações via hyperlink como arestas.

### Algoritmos utilizados

Foram utilizados:

- BFS;
- DFS;
- Dijkstra;
- Bellman-Ford.

As implementações compartilhadas estão em:

```text
src/graphs/algorithms.py
```

## Benchmarks

Os resultados dos benchmarks da Parte 2 são armazenados em:

```text
out/parte2/parte2_report.json
```

O relatório contém:

- múltiplas execuções de cada caso;
- tempos médios;
- casos de BFS e DFS com diferentes fontes;
- casos de Dijkstra com diferentes pares;
- casos de Bellman-Ford;
- experimentos de escalabilidade em 10%, 50% e 100% do grafo.

### Executar benchmarks

```bash
python -m src.parte2.benchmark
```

## Comparação dos algoritmos

Para gerar a tabela e o gráfico comparativo dos tempos médios:

```bash
python -m src.parte2.algorithm_comparison
```

O gráfico é salvo em:

```text
out/parte2/comparacao_algoritmos.png
```

## Análise e visualização de dados

As visualizações da Parte 2 são armazenadas em:

```text
out/parte2/
```

Atualmente são geradas:

### Visualizações exploratórias

- `scatter_graus_symlog.png`
- `interacoes_ao_longo_do_tempo.png`

### Visualizações explanatórias

- `explanatoria_1_concentracao_graus.png`
- `explanatoria_2_crescimento_interacoes.png`

As respectivas notas analíticas estão armazenadas em `docs/`.

### Executar as visualizações

```bash
python -m src.parte2.visualizations
python -m src.parte2.explanatory_visualizations
```

## Documentação

Os documentos auxiliares da Parte 2 estão em:

```text
docs/
```

Eles incluem:

- proposta do dataset;
- pergunta de pesquisa;
- notas analíticas;
- discussão crítica;
- limitações do design dos pesos;
- registro do uso de IA.

## Uso de IA

Os usos de ferramentas de IA realizados durante o desenvolvimento são registrados em:

```text
docs/ai_usage.md
```

Trechos de código que receberam suporte de IA são identificados no código utilizando comentários no formato:

```python
# [IA] <ferramenta> – <finalidade>
```

## Saídas

Os arquivos gerados pelo projeto são armazenados separadamente do código-fonte:

```text
out/
├── parte1/
└── parte2/
```

Essa separação mantém código, dados de entrada e resultados organizados em diretórios distintos.

## Integrantes

- Lucas Menezes Santana
- Ricardo Sergio Freitas
- Thiago Medeiros
- Kauan Novello

## Contribuições

A divisão das contribuições individuais do grupo é apresentada na matriz de contribuição da documentação final do projeto.
