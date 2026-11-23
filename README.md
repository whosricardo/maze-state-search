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
# TODO: adicionar aqui o comando principal utilizado pelo grupo
# para executar a Parte 1.
```

## Parte 2 — Reddit Hyperlink Network

O dataset utilizado está localizado em:

```text
data/dataset_parte2/soc-redditHyperlinks-body.tsv
```

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
# TODO: confirmar o comando utilizado para executar benchmark.py
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
# TODO: confirmar os comandos exatos utilizados pelo grupo
# para visualizations.py e explanatory_visualizations.py.
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

```text
TODO: adicionar nomes dos integrantes do grupo.
```

## Contribuições

A divisão das contribuições individuais do grupo é apresentada na matriz de contribuição da documentação final do projeto.
