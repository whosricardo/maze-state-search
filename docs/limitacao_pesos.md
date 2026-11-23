### Limitações do design dos pesos

**1. O que o WEIGHT agregado representa?**

Somar `+1` e `-1` para todas as interações entre o mesmo par de subreddits resulta no **saldo líquido de sentimento** daquela relação direcionada. Um peso positivo indica predominância de links classificados como positivos, enquanto um peso negativo indica predominância de links classificados como negativos. Valores próximos de zero indicam maior equilíbrio entre os dois tipos de interação.

**2. O que podemos perder ao fazer essa agregação?**

A agregação pode ocultar principalmente o **volume de interações** e o nível de oposição existente dentro da relação. Um par de subreddits com 10 links positivos e 9 negativos resulta em peso `1`, exatamente o mesmo valor de um par que apresentou apenas um único link positivo. Assim, relações com volumes e comportamentos muito diferentes podem receber o mesmo peso agregado.

Além disso, a agregação elimina a dimensão temporal das interações. Com apenas o peso final, não é possível observar, por exemplo, se uma relação apresentou mudanças de comportamento ao longo do período analisado.

**3. Qual é o problema de usar o WEIGHT original como custo de caminho?**

Algoritmos de caminho mínimo, como o Bellman-Ford, procuram **minimizar a soma dos pesos**. Como valores negativos representam relações com saldo de sentimento negativo, a minimização pode favorecer arestas cada vez mais negativas.

Isso cria uma limitação semântica: um caminho de menor custo matemático não representa necessariamente uma relação mais próxima, positiva ou desejável entre os subreddits. Além disso, quando existem ciclos negativos alcançáveis, o custo pode continuar diminuindo ao percorrer repetidamente o ciclo, fazendo com que não exista um caminho mínimo finito para os vértices afetados.

**4. Qual é a limitação da transformação usada no Dijkstra?**

A transformação

`cost = max_weight - weight + 1`

garante que todos os custos sejam positivos e faz com que arestas de maior peso agregado tenham menor custo transformado. Entretanto, ela altera o significado original dos pesos.

Além disso, cada aresta percorrida adiciona um custo base ao caminho. Como esse valor é acumulado a cada salto, caminhos com maior quantidade de arestas podem ser penalizados mesmo quando são compostos por relações de peso elevado. Dessa forma, a transformação introduz um viés em favor de caminhos com menos saltos, além de impedir que o custo transformado seja interpretado diretamente como o sentimento original da relação.
