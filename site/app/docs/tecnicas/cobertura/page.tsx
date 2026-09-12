// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/kiln_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cobertura de testes",
  description: "Quais linhas os testes executaram, e por que os dois lados da fração precisam estar certos.",
};

const blocos: Bloco[] = [
  {"p": "Uma suíte verde não diz nada sobre o que ela não exercita. `13 passaram` não distingue \"o sistema está testado\" de \"os treze caminhos fáceis estão testados\" — e num sistema de 200 arquivos, o código que ninguém tocou é exatamente onde o bug mora."},
  {"h2": "Como se pede"},
  { code: `dataforge test --cobertura
dataforge test --cobertura --linhas     # as linhas descobertas, em faixas
dataforge test --minimo=80              # reprova abaixo disso (saída 1)

dataforge crucible --cobertura          # o mesmo, no Crucible`, lang: 'bash' },
  { code: `  src/main.df         ░░░░░░░░░░░░░░░░░░░░   0.0%  0/94
                      sem teste: montar_cli, mostrar, principal
  src/repositorio.df  ████████████████████ 100.0%  38/38
  src/tarefa.df       ████████████████████ 100.0%  14/14

  total  35.6%  52 de 146 linhas executáveis`, lang: 'text' },
  {"p": "`--minimo` aceita `80`, `80%` e `0.8`. A fronteira é em 1 **inclusive**: `--minimo=1` é um por cento, porque ninguém exige cobertura total digitando `1`."},
  {"h2": "A informação que resolve"},
  {"p": "`58% coberto` não diz o que fazer. **`sem teste: nunca_chamada`** diz."},
  {"p": "Por isso o relatório lista, para cada arquivo, os nomes das ações cujo corpo nunca rodou — e com `--linhas`, as linhas em faixas (`3-5, 9, 11-12`), porque uma lista de setenta números é ilegível."},
  {"h2": "Os dois lados da fração"},
  {"p": "Cada metade tem um jeito próprio de mentir, e as duas foram tratadas:"},
  {"table": {"head": ["Metade", "De onde vem", "Como mentiria"], "rows": [["denominador", "o parser: quais linhas são **executáveis**", "contar comentário e linha vazia dá um número sempre pessimista, que ninguém olha duas vezes"], ["numerador", "a execução, instrumentada", "com a compilação de corpos ligada, o corpo das ações passa por fora e **toda ação daria 0%**"]]}},
  {"p": "E duas escolhas que mudam o que se lê:"},
  {"callout": {"tipo": "nota", "titulo": "A linha do `action` não conta; o corpo conta", "texto": "Assim uma ação nunca chamada aparece com **0%**, e não com 20% por causa da linha da declaração. Zero é a leitura honesta."}},
  {"callout": {"tipo": "nota", "titulo": "Arquivo sem teste nenhum aparece com 0%", "texto": "Em vez de sumir do relatório. Sumir é o que faz uma cobertura de 95% conviver com metade do sistema sem teste — e é o defeito mais comum das ferramentas que medem só o que foi importado."}},
  {"h2": "O que ela não mede"},
  {"p": "É de **linha**, e não de ramo: `given a and b` conta como coberta mesmo que `b` nunca tenha sido avaliado. Medir ramo exigiria instrumentar a avaliação de expressão, o que dobraria o custo — e cobertura de linha já responde a pergunta que importa, que é \"existe código que ninguém testou\"."},
  {"h2": "No CI"},
  { code: `- name: testes com cobertura mínima
  run: dataforge test --minimo=80`, lang: 'yaml' },
  {"p": "O comando devolve `1` quando fica abaixo, então o job falha. Comece pelo número que você já tem, e suba-o um ponto por vez — um mínimo de 80% num projeto a 35% só ensina a desligar a verificação."},
  {"h2": "Uma advertência"},
  {"p": "Cobertura alta não é qualidade. Um teste que chama tudo e não verifica nada dá 100%:"},
  { code: `action test_nao_verifica_nada():
    processar_pedido(pedido)      // coberto a 100%, zero garantido`, lang: 'df' },
  {"p": "O número serve para achar o que está a **zero**, e é aí que ele vale quase tudo o que custa. Para o resto, [`Crucible`](/docs/tecnicas/testes) — matchers, dublês, teste por propriedade e instantâneo."},
  {"h2": "`forge_modules/` fica de fora"},
  {"p": "Os testes das suas dependências não são os seus. Um projeto com 13 testes relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca que ninguém escreveu."},
];

const headings = [{ id: 'como-se-pede', text: "Como se pede", level: 2 as const }, { id: 'a-informacao-que-resolve', text: "A informação que resolve", level: 2 as const }, { id: 'os-dois-lados-da-fracao', text: "Os dois lados da fração", level: 2 as const }, { id: 'o-que-ela-nao-mede', text: "O que ela não mede", level: 2 as const }, { id: 'no-ci', text: "No CI", level: 2 as const }, { id: 'uma-advertencia', text: "Uma advertência", level: 2 as const }, { id: 'forgemodules-fica-de-fora', text: "`forge_modules/` fica de fora", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cobertura de testes"}
      description={"Quais linhas os testes executaram, e por que os dois lados da fração precisam estar certos."}
      href={"/docs/tecnicas/cobertura"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
