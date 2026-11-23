### Explanatória 1 — Concentração dos subreddits em graus baixos

**1. O que o gráfico comunica:**  
A mensagem principal é que a maior parte dos subreddits possui poucos relacionamentos distintos com outras comunidades: **91,8% apresentam simultaneamente grau de saída menor ou igual a 10 e grau de entrada menor ou igual a 10**. Isso mostra que a grande maioria das comunidades está concentrada na região de baixos graus, enquanto apenas 8,2% dos subreddits ficam fora dessa faixa.

**2. Relação com a pergunta de pesquisa:**  
Esse resultado ajuda a responder à pergunta *“Como os subreddits se relacionam e interagem entre si por meio de hyperlinks dentro da rede do Reddit?”* ao mostrar que a quantidade de comunidades distintas com as quais cada subreddit se conecta não é distribuída de maneira uniforme. A maior parte apresenta poucos relacionamentos de entrada e saída, enquanto uma parcela menor alcança graus mais elevados.

**3. Por que destacamos a região até grau 10:**  
O retângulo sombreado foi utilizado para direcionar a atenção para a região em que se encontra a maior parte dos subreddits. Como a escala `symlog` permite representar simultaneamente graus muito baixos e valores elevados, o destaque ajuda o leitor a identificar rapidamente a faixa de interesse sem desconsiderar o restante da distribuição.

**4. Por que colocamos a porcentagem diretamente no gráfico:**  
Em um gráfico de dispersão com milhares de pontos, existe sobreposição entre observações que possuem graus iguais ou semelhantes. Por isso, apenas observar a densidade visual não permite estimar com precisão quantos subreddits pertencem à região destacada. A anotação de **91,8%** transforma essa concentração em uma medida quantitativa direta e facilita a compreensão da principal mensagem do gráfico.

**5. Diferença para a exploratória:**  
A visualização exploratória foi utilizada para observar a distribuição geral dos graus de entrada e saída e identificar padrões presentes nos dados. Já a explanatória direciona a atenção para um achado específico dessa exploração: a concentração de **91,8% dos subreddits na região em que os graus de entrada e saída são menores ou iguais a 10**. O destaque da região e a anotação percentual tornam essa mensagem mais direta para o leitor.
