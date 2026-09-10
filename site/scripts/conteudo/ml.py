# -*- coding: utf-8 -*-
"""Aprendizado de máquina — a página do Cortex e a técnica."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

_CORTEX = sorted(k for k in get_module("Arcane.Cortex")
                 if not k.startswith("__"))

PAGINAS = [
{
"href": "/docs/biblioteca/cortex",
"title": "Arcane.Cortex",
"description": f"Aprendizado de máquina: {len(_CORTEX)} símbolos — regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA.",
"blocos": [
 {"code": """adopt Arcane.Cortex as ML

treino, teste := ML.dividir(dados, 0.2)
modelo := ML.floresta(treino, "comprou", ["idade", "renda", "visitas"])

r := ML.avaliar(modelo, teste)
out $"acerto {r["acuracia"]}, F1 {r["f1"]}\"""", "lang": "df"},

 {"h2": "Preparar"},
 {"table": {"head": ["Símbolo", "Faz"], "rows": [
   ["`dividir(linhas, p, semente, estratificar)`", "treino e teste — **embaralha antes**"],
   ["`embaralhar(linhas, semente)`", "ordem aleatória, reprodutível"],
   ["`categorico(linhas, coluna)`", "texto vira uma coluna 0/1 por valor"],
   ["`escalonar(linhas, colunas)`", "a média e o desvio de cada coluna"],
   ["`aplicar_escala(linhas, escala)`", "normaliza com a escala do treino"]]}},

 {"h2": "Treinar"},
 {"table": {"head": ["Símbolo", "Para quê"], "rows": [
   ["`linear(linhas, alvo, colunas)`", "prever um **número** — mínimos quadrados"],
   ["`logistica(linhas, alvo, colunas)`", "**duas** classes"],
   ["`arvore(linhas, alvo, colunas)`", "classificar, com regras legíveis"],
   ["`floresta(linhas, alvo, colunas, arvores)`", "várias árvores votando — o padrão bom"],
   ["`vizinhos(linhas, alvo, colunas, k)`", "k-NN — não treina, decide na hora"],
   ["`bayes_texto(linhas, alvo, coluna)`", "classificar **texto**"],
   ["`kmedias(linhas, colunas, grupos)`", "agrupar sem rótulo"],
   ["`pca(linhas, colunas, componentes)`", "reduzir dimensões"]]}},

 {"h2": "Usar e avaliar"},
 {"table": {"head": ["Símbolo", "Devolve"], "rows": [
   ["`prever(modelo, linhas)`", "a previsão de cada linha"],
   ["`prever_um(modelo, linha)`", "uma só"],
   ["`probabilidade(modelo, linha)`", "a confiança — `logistica` e `floresta`"],
   ["`avaliar(modelo, teste)`", "acurácia, precisão, revocação, F1 — ou MAE/RMSE/R²"],
   ["`matriz(modelo, teste)`", "a matriz de confusão, em texto"],
   ["`validacao_cruzada(...)`", "média **e desvio** entre k dobras"],
   ["`importancia(modelo)`", "quais colunas decidem"],
   ["`salvar(modelo, caminho)` / `carregar`", "JSON legível, sem pickle"]]}},

 {"h2": "O que ele não é"},
 {"p": "Não é TensorFlow. Não há GPU, retropropagação nem rede profunda — e **fingir que há seria pior que não ter**."},
 {"callout": {"tipo": "nota", "titulo": "A versão anterior era exatamente isso", "texto": "`sentiment` devolvia `neutral 0.5` para qualquer texto, `Dense(4)` devolvia `{\"type\": \"Dense\", \"units\": 4}`, e `classify` pedia um modelo que não existia em lugar nenhum. Cinco símbolos, nenhum funcionando. O que está aqui agora são os algoritmos clássicos implementados de verdade, na escala em que um interpretador de árvore trabalha: milhares de linhas, não milhões."}},
]},

{
"href": "/docs/tecnicas/ml",
"title": "Aprendizado de máquina",
"description": "Treinar é a parte fácil. O que separa um modelo útil de um número bonito é a avaliação.",
"blocos": [
 {"p": "`Arcane.Cortex` traz os algoritmos clássicos, implementados em DataForge puro. Eles cobrem a maioria esmagadora dos problemas de **dado tabular** — que é onde a maior parte do trabalho real acontece."},

 {"h2": "O caminho inteiro"},
 {"code": """adopt Arcane.Cortex as ML

// 1. dividir ANTES de olhar
treino, teste := ML.dividir(clientes, 0.2, 42, "comprou")

// 2. treinar
modelo := ML.floresta(treino, "comprou", ["idade", "renda", "visitas"], 30)

// 3. medir no que ele NÃO viu
r := ML.avaliar(modelo, teste)
out $"acurácia {r["acuracia"]}  F1 {r["f1"]}"
out ML.matriz(modelo, teste)

// 4. entender
out ML.importancia(modelo)

// 5. guardar
ML.salvar(modelo, "modelos/compra.json")""", "lang": "df"},

 {"h2": "Dividir antes de olhar"},
 {"p": "`dividir` **embaralha sempre**, e isso não é detalhe. Dado quase nunca chega em ordem aleatória: vem ordenado por data, por id, por categoria. Cortar sem embaralhar põe todo um tipo de exemplo de um lado só, e a avaliação passa a medir outra coisa."},
 {"code": """// num problema com 2% de fraude, o corte cego pode
// deixar o teste sem fraude nenhuma
treino, teste := ML.dividir(dados, 0.2, 42, "fraude")""", "lang": "df"},
 {"p": "O quarto argumento **estratifica**: mantém a proporção das classes nos dois lados."},
 {"callout": {"tipo": "nota", "titulo": "A semente é fixa de propósito", "texto": "Sem ela, treinar duas vezes dá modelos diferentes — e comparar duas ideias vira comparar dois sorteios. Quem quer variar passa a semente."}},

 {"h2": "A acurácia mente"},
 {"p": "Num problema com 99% de uma classe, um modelo que **responde sempre a mesma coisa** acerta 99%. É o caso que faz alguém publicar um modelo inútil achando que ele é bom."},
 {"code": """{
  "acuracia": 0.95,
  "precisao": 0.90, "revocacao": 0.95, "f1": 0.92,
  "por_classe": {
    "comum": {"precisao": 0.95, "revocacao": 1.00, "f1": 0.97, "quantos": 190},
    "raro":  {"precisao": 0.00, "revocacao": 0.00, "f1": 0.00, "quantos": 10}
  }
}""", "lang": "json"},
 {"p": "95% de acurácia, e a classe que interessa nunca é encontrada. Por isso `avaliar` devolve **precisão, revocação e F1** por classe, e a média é ponderada pelo tamanho — a simples trataria 10 exemplos como iguais a 190."},
 {"p": "E `matriz` mostra **onde** ele erra:"},
 {"code": """real \\ previsto      comum     raro
------------------------------------
comum                  190        0
raro                    10        0""", "lang": "text"},

 {"h2": "Uma divisão mede um sorteio"},
 {"code": """r := ML.validacao_cruzada(dados, "comprou", colunas, "floresta", 5)
// {"media": 0.9533, "desvio": 0.0163,
//  "por_dobra": [0.9833, 0.95, 0.95, 0.95, 0.9333]}""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "O desvio diz mais que a média", "texto": "Um modelo que varia muito entre as dobras não é confiável, por melhor que seja a média. Com 200 linhas, a diferença entre duas sementes chega a dez pontos — e escolher um modelo por causa disso é escolher pelo sorteio."}},

 {"h2": "Qual algoritmo"},
 {"table": {"head": ["Situação", "Use", "Por quê"], "rows": [
   ["prever um número", "`linear`", "solução exata, sem taxa de aprendizado para errar"],
   ["duas classes, fronteira reta", "`logistica`", "rápida, e dá probabilidade"],
   ["quer entender a decisão", "`arvore`", "as regras são legíveis"],
   ["quer o melhor resultado", "`floresta`", "corrige o que a árvore decora"],
   ["fronteira estranha, poucos dados", "`vizinhos`", "não supõe forma nenhuma"],
   ["classificar texto", "`bayes_texto`", "difícil de bater em texto curto"],
   ["não há rótulo", "`kmedias`", "acha os grupos sozinho"],
   ["muitas colunas", "`pca`", "reduz preservando a variância"]]}},

 {"h2": "Por que a floresta bate a árvore"},
 {"p": "Uma árvore sozinha **decora** o treino. A floresta corrige isso por duas fontes de variação: cada árvore vê uma amostra **com reposição** das linhas, e cada corte olha só um subconjunto das colunas."},
 {"p": "Sem as duas, as árvores sairiam quase idênticas e a votação não acrescentaria nada. Num problema onde uma classe está *dentro* da outra — que nenhuma reta separa — a diferença medida foi de 90% para 97%."},

 {"h2": "Escala importa (para alguns)"},
 {"code": """escala := ML.escalonar(treino, ["idade", "renda"])
treino := ML.aplicar_escala(treino, escala)
teste  := ML.aplicar_escala(teste, escala)     // a MESMA escala""", "lang": "df"},
 {"p": "Sem escala, uma coluna em milhares domina uma em unidades no k-NN e na logística — a distância vira a da coluna grande, e as outras deixam de existir. **Árvore e floresta não precisam**: elas cortam por coluna, e a grandeza não muda a ordem."},
 {"callout": {"tipo": "atencao", "titulo": "A escala vem do TREINO", "texto": "Calcular a escala com o teste junto é vazamento: o modelo passa a saber algo sobre os dados que deveria não conhecer, e a avaliação fica otimista sem ninguém notar."}},

 {"h2": "Texto vira número por one-hot"},
 {"code": """r := ML.categorico(linhas, "cidade")
// cria 'cidade_sp', 'cidade_rj', 'cidade_bh' — 0 ou 1""", "lang": "df"},
 {"p": "Uma coluna por valor, e não um número por categoria: numerar `azul=0, verde=1, vermelho=2` faria o modelo achar que vermelho é *maior* que azul, e que verde está no meio dos dois."},

 {"h2": "Guardar"},
 {"code": """ML.salvar(modelo, "modelos/compra.json")
modelo := ML.carregar("modelos/compra.json")""", "lang": "df"},
 {"p": "É **JSON**, e não pickle. Pickle executaria código ao carregar: um modelo baixado de qualquer lugar viraria execução arbitrária. E o JSON ainda dá para abrir e entender o que o modelo é."},

 {"h2": "Os limites, ditos"},
 {"list": [
   "**Não há rede neural.** Sem GPU e sem retropropagação, uma rede profunda em interpretador de árvore não terminaria.",
   "**A escala é de milhares de linhas**, não milhões. Para além disso, exporte em [Parquet](/docs/tecnicas/parquet) e use uma ferramenta dedicada.",
   "**Não há ajuste automático de hiperparâmetro.** `validacao_cruzada` mede; escolher é seu.",
   "**Nada disso substitui olhar os dados.** `Qualidade.perfil()` antes de treinar acha mais problema que qualquer modelo."]},
]},
]
