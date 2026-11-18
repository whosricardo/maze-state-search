# Documentação de Uso de Inteligência Artificial

## 1. Ferramenta utilizada

Durante o desenvolvimento do projeto foi utilizado o **ChatGPT (OpenAI)** como ferramenta de apoio ao aprendizado, revisão de código, interpretação de testes e discussão de decisões de implementação.

O uso da ferramenta ocorreu de maneira incremental. Foram apresentadas dúvidas, trechos de código já desenvolvidos e resultados de testes para análise e revisão.

Até o estágio atual, a ferramenta foi utilizada principalmente para apoio conceitual, identificação de erros, sugestão de casos de teste e discussão da organização do projeto.

---

## 2. Organização inicial do projeto

A IA foi utilizada para discutir a separação de responsabilidades entre os principais módulos.

A organização adotada até o momento considera:

```text
io.py
    leitura e validação dos mapas

estados.py
    regras relacionadas às posições do mapa
    custos das células
    construção das representações relacionadas ao labirinto

graph.py
    estrutura genérica de grafo direcionado e ponderado

metrics.py
    métricas aplicadas sobre a estrutura Graph
```

Foi discutida principalmente a necessidade de manter `graph.py` independente das regras específicas do labirinto.

Dessa forma, a classe `Graph` apenas armazena vértices, arestas e pesos, enquanto `estados.py` é responsável por interpretar o mapa e determinar quais elementos devem fazer parte do grafo.

---

## 3. Leitura e validação dos mapas

A IA foi utilizada para auxiliar na compreensão da representação do mapa em Python através de listas de listas.

Foi discutido o acesso às posições utilizando:

```python
grid[row][col]
```

Também foram revisadas funções desenvolvidas pelo grupo para validar:

- existência de conteúdo no mapa;
- formato retangular;
- utilização apenas dos símbolos permitidos;
- existência de exatamente um ponto inicial `S`;
- existência de exatamente um objetivo `G`.

Durante essa etapa também foram esclarecidos comportamentos específicos de Python, como indexação negativa e acesso a matrizes representadas através de listas.

Os testes dessas funções foram desenvolvidos utilizando `pytest`.

---

## 4. Lógica de vizinhança

Foi desenvolvida pelo grupo uma função `neighbor_logic(pos, grid)` responsável por determinar posições fisicamente adjacentes a uma posição do mapa.

A IA foi utilizada para revisar versões intermediárias dessa função e discutir:

- representação de posições através de tuplas `(row, col)`;
- verificação dos limites da matriz;
- comportamento de índices negativos em Python;
- bloqueio causado por paredes `#`;
- ordem de verificação das direções;
- consistência do tipo retornado pela função.

A ordem utilizada foi:

```text
Norte
Leste
Sul
Oeste
```

Também foi discutida a decisão de retornar uma lista vazia `[]` quando a posição fornecida estiver fora do mapa ou corresponder a uma parede.

---

## 5. Testes da lógica de vizinhança

A IA foi utilizada para sugerir e revisar casos de teste para `neighbor_logic()`.

Até o momento foram implementados testes para:

- posição com quatro vizinhos disponíveis;
- posição com o movimento para o norte bloqueado;
- posição atual localizada em uma parede;
- posição com coordenadas negativas;
- posição com coordenadas superiores aos limites da matriz.

Durante os testes foi discutida também a importância de verificar a ordem dos vizinhos retornados.

Os testes foram escritos pelo grupo utilizando `pytest`.

---

## 6. Estrutura genérica de grafo

A IA foi utilizada como apoio conceitual para compreender a diferença entre:

```text
vértice
aresta
peso
grafo direcionado
estrutura de adjacência
```

Inicialmente foi considerada uma representação baseada em listas:

```python
{
    vertice: [(vizinho, peso)]
}
```

Posteriormente foi discutida uma representação baseada em dicionários:

```python
{
    vertice: {
        vizinho: peso
    }
}
```

A segunda representação foi escolhida por permitir que cada relação entre uma origem e um destino tenha um único peso associado.

---

## 7. Desenvolvimento da classe `Graph`

A classe `Graph` foi desenvolvida pelo grupo de maneira incremental.

Até o momento ela possui as seguintes responsabilidades:

```text
add_vertex(vertex)
    adiciona um vértice caso ele ainda não exista

add_edge(source, destination, weight)
    garante a existência dos dois vértices
    e registra uma aresta direcionada com peso

get_neighbors(vertex)
    retorna os vizinhos e seus respectivos pesos
```

A IA foi utilizada para revisar diferentes versões da classe e identificar problemas como:

- sobrescrita de vértices existentes;
- tentativa de acessar uma origem antes de adicioná-la ao grafo;
- utilização incorreta de listas e dicionários;
- criação de arestas duplicadas;
- tratamento de múltiplos pesos para a mesma relação origem-destino.

Foi adotada uma estrutura equivalente a:

```python
{
    source: {
        destination: weight
    }
}
```

---

## 8. Testes da classe `Graph`

Os testes da classe foram desenvolvidos pelo grupo utilizando `pytest`.

Foram discutidos e implementados testes relacionados a:

- criação de vértices;
- tentativa de adicionar o mesmo vértice mais de uma vez;
- criação de arestas;
- criação automática dos vértices de origem e destino;
- comportamento quando uma relação já existe;
- consulta dos vizinhos de um vértice;
- vértices sem arestas de saída.

A IA foi utilizada para revisar os valores esperados e interpretar diferenças entre o estado esperado e o estado real da estrutura `adjacency`.

---

## 9. Custos das células

A IA foi utilizada para discutir como representar os custos fixos associados aos símbolos do mapa.

Foi criada a estrutura:

```python
CELL_COST = {
    '.': 1,
    'S': 1,
    'G': 1,
    ',': 3,
    '~': 5,

    'a': 1,
    'b': 1,
    'c': 1,
    'd': 1,

    'A': 1,
    'B': 1,
    'C': 1,
    'D': 1,

    '>': 1,
    '<': 1,
    '^': 1,
    'v': 1,

    '*': -2,
}
```

Foi discutida a diferença entre:

```text
ALLOWED_SYMBOLS
    símbolos válidos em um mapa

CELL_COST
    símbolos que possuem um custo fixo de entrada
```

O símbolo `#` não foi incluído por representar uma parede não atravessável.

O símbolo `+` também não foi incluído nessa tabela de custos fixos, pois seu comportamento depende do estado da execução.

---

## 10. Função `cell_cost`

Foi desenvolvida pelo grupo uma função simples para consultar os custos fixos:

```python
def cell_cost(symbol):
    return CELL_COST[symbol]
```

A IA foi utilizada para discutir o comportamento dessa implementação.

Foi decidido utilizar o acesso direto ao dicionário para que símbolos que não possuam custo fixo provoquem um `KeyError`, tornando o uso incorreto da função explícito.

Foram implementados testes para diferentes categorias de símbolos, incluindo:

- piso;
- lama;
- água;
- chave;
- porta;
- esteira;
- fonte de custo negativo.

Também foi desenvolvido um teste utilizando:

```python
with pytest.raises(KeyError):
```

para verificar o comportamento quando `cell_cost('+')` é chamado.

---

## 11. Início da construção de `G_pos`

A IA foi utilizada para discutir conceitualmente a construção do grafo de posições `G_pos`.

Foi definido o seguinte fluxo:

```text
arquivo do mapa
        ↓
parse_map()
        ↓
grid
        ↓
build_g_pos(grid)
        ↓
Graph
```

Foi discutida a importância de `build_g_pos()` receber o `grid` já interpretado, mantendo a leitura de arquivos como responsabilidade de `io.py`.

A primeira etapa implementada pelo grupo para `build_g_pos()` foi:

1. criar um objeto `Graph` vazio;
2. percorrer todas as posições da matriz;
3. verificar o símbolo existente em cada posição;
4. ignorar as paredes `#`;
5. adicionar cada posição atravessável como um vértice;
6. retornar o grafo.

A versão atual desenvolvida pelo grupo é equivalente a:

```python
def build_g_pos(grid):
    g_pos = Graph()

    for row in range(len(grid)):
        for column in range(len(grid[row])):
            symbol = grid[row][column]
            pos = (row, column)

            if symbol != '#':
                g_pos.add_vertex(pos)

    return g_pos
```

A IA foi utilizada para revisar essa implementação e identificar inicialmente uma condição invertida que adicionava paredes ao grafo. O grupo realizou a correção antes de prosseguir.

---

## 12. Teste inicial de `G_pos`

Foi desenvolvido um teste específico para verificar somente a criação dos vértices de `G_pos`, antes da implementação das arestas.

Foi utilizado um pequeno grid controlado:

```python
grid = [
    ['#', '#', '#', '#', '#'],
    ['#', 'S', '.', ',', '#'],
    ['#', '#', '#', '#', '#'],
]
```

O resultado esperado foi definido como:

```python
{
    (1, 1): {},
    (1, 2): {},
    (1, 3): {},
}
```

Esse teste verifica que:

```text
paredes não se tornam vértices

posições atravessáveis se tornam vértices

nenhuma aresta é criada nesta etapa inicial
```

Foi optado por utilizar diretamente uma matriz no teste, em vez de criar um arquivo temporário, para testar `build_g_pos()` isoladamente da lógica de leitura de arquivos.

---

## 13. Uso do `pytest` e ambiente de desenvolvimento

A IA também foi utilizada para auxiliar na interpretação de problemas relacionados ao ambiente de desenvolvimento.

Em um momento, o editor indicou que o módulo `pytest` não poderia ser resolvido.

Foi verificado através da execução dos testes que:

```text
pytest estava instalado no ambiente virtual
os testes eram executados corretamente
```

Com isso, foi identificado que o problema estava relacionado à configuração do interpretador utilizado pelo editor, e não à implementação do projeto.

---

## 14. Forma de interação utilizada

O uso da IA ocorreu principalmente através de perguntas sobre código já escrito ou sobre decisões específicas antes da implementação.

Exemplos das interações realizadas:

```text
"Essa lógica para encontrar vizinhos está correta?"
```

```text
"Qual é a diferença entre um vértice e uma aresta?"
```

```text
"Como representar uma lista de adjacência em Python?"
```

```text
"Esse teste está verificando corretamente a função?"
```

```text
"Por que esse teste falhou?"
```

```text
"Como dividir as responsabilidades entre graph.py e estados.py?"
```

```text
"Como representar o custo das células?"
```

```text
"Como começar a construir G_pos?"
```

---

## 15. Responsabilidade pelo desenvolvimento

O desenvolvimento do código foi realizado incrementalmente pelos integrantes do grupo.

A IA foi utilizada como ferramenta de:

- apoio conceitual;
- revisão de código;
- identificação de erros;
- discussão de estruturas de dados;
- sugestão e revisão de testes;
- interpretação de resultados do `pytest`;
- discussão da arquitetura do projeto.

As decisões finais, implementação do código, execução dos testes e organização do projeto permaneceram sob responsabilidade dos integrantes do grupo.

Este documento representa o uso da IA **até o estágio atual do desenvolvimento** e deverá ser atualizado conforme novas etapas forem realizadas.
