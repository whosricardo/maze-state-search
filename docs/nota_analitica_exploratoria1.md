### Exploratória 1 — Relação entre grau de saída e grau de entrada

**1. O que o gráfico mostra:**  
Cada ponto representa um subreddit da rede de hyperlinks do Reddit. O eixo X representa o **grau de saída**, isto é, a quantidade de comunidades distintas para as quais o subreddit possui conexões de saída. O eixo Y representa o **grau de entrada**, correspondente à quantidade de comunidades distintas das quais ele recebe conexões. Os dois eixos utilizam escala `symlog`, permitindo visualizar simultaneamente valores iguais a zero, graus baixos e valores que chegam à ordem dos milhares.

**2. O que eu observei:**  
A grande maioria dos subreddits concentra-se em graus baixos, principalmente entre 0 e 10. Também existem pontos sobre os eixos, correspondentes a comunidades que apresentam apenas grau de entrada ou apenas grau de saída. A partir dos graus mais elevados, observa-se uma associação positiva aparente entre as duas variáveis: subreddits com maior grau de saída também tendem a apresentar maior grau de entrada. Nas extremidades da distribuição aparecem poucos subreddits com graus muito superiores aos da maioria da rede.

**3. Por que usamos scatter plot:**  
O scatter plot foi utilizado porque estamos investigando a relação entre **duas variáveis quantitativas**, grau de saída e grau de entrada, medidas para a mesma unidade de análise, cada subreddit. Ao representar cada comunidade como um par ordenado \((x, y)\), o gráfico permite observar simultaneamente a concentração dos dados, a relação entre as duas variáveis e a presença de valores extremos, características que seriam mais difíceis de visualizar em um gráfico destinado à análise de apenas uma variável.
