# Documentação de Uso de Inteligência Artificial

## Ferramenta utilizada

Durante o desenvolvimento inicial do projeto foi utilizado o **ChatGPT (OpenAI)** como ferramenta de apoio ao aprendizado, revisão de código e discussão de decisões de implementação.

O uso ocorreu de forma incremental, a partir de trechos de código escritos pelo grupo e dúvidas surgidas durante o desenvolvimento.

---

## Leitura e validação dos mapas

A IA foi utilizada para auxiliar na compreensão de como representar o mapa em Python utilizando listas de listas e coordenadas no formato:

```python
(row, col)
```

Também foi utilizada para revisar o código escrito para leitura e validação dos arquivos de mapa.

Foram discutidas validações relacionadas a:

- formato retangular do mapa;
- símbolos permitidos;
- existência de exatamente um ponto inicial `S`;
- existência de exatamente um objetivo `G`.

Durante essa etapa, a IA também foi utilizada para esclarecer características específicas da linguagem Python, como indexação de listas e comportamento de índices negativos.

---

## Lógica de vizinhança

O grupo desenvolveu uma função para identificar posições vizinhas válidas a partir de uma coordenada do mapa.

A IA foi utilizada para revisar essa implementação e discutir:

- verificação dos limites da matriz;
- tratamento de paredes (`#`);
- representação das posições através de tuplas;
- ordem de verificação das direções;
- consistência do tipo retornado pela função.

A função foi desenvolvida incrementalmente pelo grupo e posteriormente validada através de testes.

---

## Testes da lógica de vizinhança

A IA foi utilizada para sugerir situações relevantes que deveriam ser testadas.

Foram considerados casos como:

- posição com quatro vizinhos disponíveis;
- direção bloqueada por uma parede;
- posição atual localizada em uma parede;
- posição localizada fora dos limites do mapa.

Os testes foram implementados utilizando `pytest`.

A IA também foi utilizada para revisar os testes e interpretar diferenças entre o resultado esperado e o resultado produzido pelo código.

---

## Estrutura genérica de grafo

Durante a implementação da estrutura básica de grafo, a IA foi utilizada para esclarecer conceitos como:

```text
vértice
aresta
peso
lista de adjacência
grafo direcionado
```

Também foram discutidas diferentes formas de representar a estrutura de adjacência em Python.

Inicialmente foi considerada uma representação baseada em listas:

```python
{
    vertice: [(vizinho, peso)]
}
```

Posteriormente, foi adotada uma representação baseada em dicionários:

```python
{
    vertice: {
        vizinho: peso
    }
}
```

Essa decisão foi discutida considerando a necessidade de armazenar uma única relação direcionada entre uma origem e um destino.

---

## Desenvolvimento da classe `Graph`

A classe `Graph` foi desenvolvida pelo grupo de forma incremental.

Até o momento, foram implementadas operações para:

```text
adicionar um vértice
adicionar uma aresta direcionada com peso
consultar os vizinhos de um vértice
```

A IA foi utilizada para revisar versões intermediárias da implementação e apontar inconsistências entre a estrutura de dados escolhida e as operações realizadas sobre ela.

Também foi discutido o comportamento esperado quando:

- um vértice já existe;
- uma aresta utiliza vértices ainda não cadastrados;
- uma relação entre origem e destino já existe;
- um vértice não possui vizinhos.

---

## Testes da classe `Graph`

Os testes da classe foram escritos pelo grupo utilizando `pytest`.

Até o momento foram discutidos e implementados testes relacionados a:

- adição de vértices;
- tentativa de adicionar novamente um vértice já existente;
- adição de arestas;
- criação dos vértices de origem e destino durante a adição de uma aresta;
- tentativa de adicionar novamente uma relação já existente;
- consulta dos vizinhos de um vértice;
- consulta de um vértice sem arestas de saída.

A IA foi utilizada para revisar a lógica dos testes e verificar se os valores esperados estavam de acordo com o comportamento implementado pela classe.

---

## Organização do código

A IA também foi utilizada para discutir a separação de responsabilidades entre os módulos já trabalhados.

Até o momento, a organização considerada é:

```text
io.py
    leitura e validação dos mapas

estados.py
    lógica relacionada às posições e ao domínio do labirinto

graph.py
    estrutura genérica de grafo
```

Foi discutida a importância de manter a classe `Graph` independente das regras específicas do labirinto.

Dessa forma, a estrutura de grafo é responsável apenas por armazenar vértices, arestas e pesos, enquanto as regras relacionadas ao mapa permanecem em módulos específicos do domínio.

---

## Forma de utilização da IA

O uso da IA ocorreu principalmente através da apresentação de código previamente escrito pelo grupo para revisão.

Alguns exemplos do tipo de interação realizada foram:

```text
"Essa lógica para encontrar os vizinhos está correta?"
```

```text
"Qual é a diferença entre adicionar um vértice e uma aresta?"
```

```text
"Essa representação de lista de adjacência faz sentido?"
```

```text
"Esse teste está verificando o comportamento correto?"
```

```text
"Por que o resultado do teste foi diferente do esperado?"
```

Assim, até esta etapa do projeto, a IA foi utilizada principalmente como ferramenta de **apoio conceitual, revisão de implementação e auxílio na elaboração e interpretação de testes**.

---

## Responsabilidade pelo desenvolvimento

O código apresentado até o momento foi desenvolvido de forma incremental pelo grupo.

As sugestões fornecidas pela IA foram utilizadas como apoio para compreensão dos conceitos, identificação de erros e discussão de alternativas de implementação.

As decisões finais sobre a estrutura do código e sua implementação permaneceram sob responsabilidade dos integrantes do grupo.
