# Exercicio 218 — Uma aplicação de dados com a Vitrine

## Enunciado

Escreva um programa de cima para baixo que vira uma página web, e
confira o que ele faz **sem abrir navegador nenhum**.

## Conceitos

```dataforge
adopt Arcane.Vitrine as V

action painel():
    V.titulo("Vendas")
    regiao := V.escolha("Região", ["Sul", "Norte"])
    V.metrica("Total", 128400)
    V.grafico_barras(dados_de(regiao), x := "mes")

V.rodar(painel, porta := 8501)
```

Não há palavra reservada nova. A Vitrine é um módulo da biblioteca, e
tudo nela é chamada de ação.

## O modelo de execução

A cada interação, **o programa inteiro roda de novo** — e o estado da
sessão sobrevive.

```
clique  →  o programa roda do começo  →  a árvore vira HTML  →  a tela troca
              ↑                                                      │
              └──────────  o estado da sessão continua  ─────────────┘
```

Isso parece desperdício e é o contrário: quem escreve nunca pensa em
callback, em diffing, nem em qual pedaço da tela atualizar. A linha de
cima sempre aconteceu antes da linha de baixo, como em qualquer
programa. O preço é que a página precisa ser rápida a cada clique — daí
o `V.cache`, que existe desde o primeiro dia e não como otimização
posterior.

## Para que serve

Mostrar dado é metade do trabalho de quem trabalha com dado, e a outra
metade normalmente exige HTML, CSS, JavaScript, um servidor e um build.
A Vitrine troca tudo isso por um programa que já se sabe escrever.

O `Kiln` continua sendo o framework de **sites e APIs**, onde cada rota
devolve o que quiser. A Vitrine é para **painel e aplicação de dados**,
onde a página é o programa. Ela roda sobre o Kiln: HTTP, rota, sessão e
cabeçalho de segurança já estavam lá, testados.

## O que o exercício cobre

| Parte | Ideia |
|---|---|
| 1 | componente é chamada de ação, e ela **devolve** o valor |
| 2 | o estado sobrevive; o clique vale por **uma** execução |
| 3 | a área de layout é um objeto, e os componentes são métodos dela |
| 4 | `mark @V.cache` faz a leitura acontecer uma vez, e não por clique |
| 5 | gráfico vira SVG escrito no servidor, sem biblioteca |
| 6 | formulário só entrega os valores quando alguém confirma |
| 7 | um erro aparece **na página**, e não derruba o servidor |
| 8 | `V.pedir` faz um pedido HTTP de verdade, sem socket |

## Três armadilhas

**O botão vale por uma execução.** `given V.botao("Pagar")` é verdadeiro
no ciclo do clique e falso nos seguintes. Se fosse permanente, o
pagamento aconteceria de novo no próximo carregamento da página.

**Cada tecla roda o programa inteiro.** É o preço do modelo. Num campo
ligado a uma consulta pesada, ponha-o dentro de um `V.formulario(...)`:
aí os valores só chegam quando alguém aperta o botão de envio.

**`V.html` não escapa nada.** É a única porta de XSS da Vitrine, e ela
existe porque às vezes não há alternativa. Nunca passe por ali algo que
veio do usuário — para isso, `V.texto`, que escapa.

## Para ver no navegador

```bash
dataforge run exercicios/28-vitrine/218_vitrine.df    # os testes
dataforge run examples/vitrine_dashboard.df -- --servir
```

O segundo sobe em `http://127.0.0.1:8501` um painel com quatro métricas,
quatro gráficos, abas, filtro na barra lateral e exportação para CSV.
