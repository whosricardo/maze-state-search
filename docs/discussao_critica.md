### BFS

**Quando ele é útil neste dataset?**

Quando queremos explorar a rede de subreddits por camadas de proximidade ou medir o alcance de uma comunidade de forma eficiente, com complexidade \(O(V + E)\), sem considerar os pesos das arestas.

**O que ele consegue responder?**

Qual é o menor caminho em número de saltos entre dois subreddits, quantos subreddits são alcançáveis a partir de uma origem e quais comunidades estão a 1, 2 ou \(k\) graus de separação.

**Qual é a principal limitação dele aqui?**

O BFS desconsidera os pesos agregados das arestas. Assim, cada conexão entre dois subreddits é tratada como um único salto, independentemente do valor ou do sinal do peso associado à relação.

### DFS

**Quando ele é útil neste dataset?**

Quando o objetivo é explorar em profundidade a estrutura de conectividade alcançável a partir de um subreddit, analisar cadeias de referências e detectar ciclos, mantendo complexidade \(O(V + E)\).

**O que ele consegue responder?**

Quais subreddits são alcançáveis a partir de uma origem, quais relações aparecem durante a exploração e se existem ciclos entre as comunidades alcançadas. A implementação também classifica as arestas encontradas como `TREE`, `BACK`, `FORWARD` ou `CROSS`.

**Qual é a principal limitação dele aqui?**

O DFS não garante encontrar o menor caminho entre dois subreddits, nem em número de saltos nem em peso acumulado, e também não utiliza os pesos das arestas na exploração.

### Dijkstra

**Quando ele é útil neste dataset?**

Quando precisamos calcular caminhos de menor custo utilizando pesos não negativos. Na implementação utilizada, além da exploração com fila de prioridade, existe uma verificação inicial de todos os pesos do grafo.

**O que ele consegue responder?**

Qual é o trajeto de menor custo acumulado entre um subreddit de origem e um destino, utilizando o custo atribuído às ligações depois da transformação dos pesos.

**Por que foi necessário transformar os pesos?**

O algoritmo de Dijkstra exige pesos não negativos para garantir seu funcionamento correto. Como o dataset possui pesos negativos, foi necessário transformá-los antes da execução.

**Qual é a principal limitação dessa transformação?**

A transformação altera a interpretação original dos pesos,
