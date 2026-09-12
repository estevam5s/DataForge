"""Vitrine — o framework de dashboards e aplicações de dados.

O que é
-------
Você escreve um programa de cima para baixo; ele vira uma página web.
Sem HTML, sem JavaScript, sem separar o que calcula do que mostra.

    adopt Arcane.Vitrine as V

    V.titulo("Vendas")
    regiao := V.escolha("Região", ["Sul", "Norte"])
    V.metrica("Total", 128400.0, variacao := 12.5)
    V.grafico_barras(dados_de(regiao))

O modelo de execução
--------------------
A cada interação, **o programa inteiro roda de novo** — e o estado da
sessão sobrevive. É o modelo do Streamlit, e ele é escolhido por um
motivo específico: quem escreve não precisa pensar em callback, em
diffing, nem em qual pedaço da tela atualizar. A linha de cima sempre
aconteceu antes da linha de baixo.

O custo é que o programa precisa ser rápido o bastante para rodar a cada
clique — daí o `V.cache`, que existe desde o primeiro dia e não como
otimização posterior.

Sobre o que ele é construído
----------------------------
O servidor é o **Kiln**. HTTP, rotas, arquivos estáticos, sessão,
cabeçalhos de segurança e REST já existem lá, testados, e reimplementá-los
aqui criaria duas implementações do mesmo protocolo para divergirem.

A Vitrine é o que o Kiln não tem: árvore de componentes, estado por
sessão, e a renderização.

Por que não se chama "Stream"
-----------------------------
`Arcane.Stream` já é o módulo de streaming de dados — tópicos,
partições, offsets, grupos de consumo. Duas coisas chamadas Stream no
mesmo `adopt` seria a ambiguidade que este projeto passa o tempo todo
evitando.

"Vitrine" é onde a peça pronta é exposta. O nome segue a metáfora da
forja, como Kiln, Crucible e Forge.
"""

from .api import ArcaneVitrine

__all__ = ["ArcaneVitrine"]
