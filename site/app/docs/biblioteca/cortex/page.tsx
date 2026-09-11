// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ml.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Cortex",
  description: "Aprendizado de máquina: 25 símbolos — regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Cortex as ML

treino, teste := ML.dividir(dados, 0.2)
modelo := ML.floresta(treino, "comprou", ["idade", "renda", "visitas"])

r := ML.avaliar(modelo, teste)
out $"acerto {r["acuracia"]}, F1 {r["f1"]}"`, lang: 'df' },
  {"h2": "Preparar"},
  {"table": {"head": ["Símbolo", "Faz"], "rows": [["`dividir(linhas, p, semente, estratificar)`", "treino e teste — **embaralha antes**"], ["`embaralhar(linhas, semente)`", "ordem aleatória, reprodutível"], ["`categorico(linhas, coluna)`", "texto vira uma coluna 0/1 por valor"], ["`escalonar(linhas, colunas)`", "a média e o desvio de cada coluna"], ["`aplicar_escala(linhas, escala)`", "normaliza com a escala do treino"]]}},
  {"h2": "Treinar"},
  {"table": {"head": ["Símbolo", "Para quê"], "rows": [["`linear(linhas, alvo, colunas)`", "prever um **número** — mínimos quadrados"], ["`logistica(linhas, alvo, colunas)`", "**duas** classes"], ["`arvore(linhas, alvo, colunas)`", "classificar, com regras legíveis"], ["`floresta(linhas, alvo, colunas, arvores)`", "várias árvores votando — o padrão bom"], ["`vizinhos(linhas, alvo, colunas, k)`", "k-NN — não treina, decide na hora"], ["`bayes_texto(linhas, alvo, coluna)`", "classificar **texto**"], ["`kmedias(linhas, colunas, grupos)`", "agrupar sem rótulo"], ["`pca(linhas, colunas, componentes)`", "reduzir dimensões"]]}},
  {"h2": "Usar e avaliar"},
  {"table": {"head": ["Símbolo", "Devolve"], "rows": [["`prever(modelo, linhas)`", "a previsão de cada linha"], ["`prever_um(modelo, linha)`", "uma só"], ["`probabilidade(modelo, linha)`", "a confiança — `logistica` e `floresta`"], ["`avaliar(modelo, teste)`", "acurácia, precisão, revocação, F1 — ou MAE/RMSE/R²"], ["`matriz(modelo, teste)`", "a matriz de confusão, em texto"], ["`validacao_cruzada(...)`", "média **e desvio** entre k dobras"], ["`importancia(modelo)`", "quais colunas decidem"], ["`salvar(modelo, caminho)` / `carregar`", "JSON legível, sem pickle"]]}},
  {"h2": "O que ele não é"},
  {"p": "Não é TensorFlow. Não há GPU, retropropagação nem rede profunda — e **fingir que há seria pior que não ter**."},
  {"callout": {"tipo": "nota", "titulo": "A versão anterior era exatamente isso", "texto": "`sentiment` devolvia `neutral 0.5` para qualquer texto, `Dense(4)` devolvia `{\"type\": \"Dense\", \"units\": 4}`, e `classify` pedia um modelo que não existia em lugar nenhum. Cinco símbolos, nenhum funcionando. O que está aqui agora são os algoritmos clássicos implementados de verdade, na escala em que um interpretador de árvore trabalha: milhares de linhas, não milhões."}},
];

const headings = [{ id: 'preparar', text: "Preparar", level: 2 as const }, { id: 'treinar', text: "Treinar", level: 2 as const }, { id: 'usar-e-avaliar', text: "Usar e avaliar", level: 2 as const }, { id: 'o-que-ele-nao-e', text: "O que ele não é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Cortex"}
      description={"Aprendizado de máquina: 25 símbolos — regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA."}
      href={"/docs/biblioteca/cortex"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
