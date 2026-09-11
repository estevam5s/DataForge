// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "09 · Modulos",
  description: "12 exercícios: adopt, relay, seleção e apelidos.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 09`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["099", "**adopt de um modulo local**", "importe um arquivo .df vizinho e use suas acoes."], ["100", "**Import inexistente**", "comprove que importar um modulo que nao existe dispara erro."], ["101", "**Arcane.Math**", "use funcoes matematicas da biblioteca padrao."], ["102", "**Estatistica descritiva**", "calcule medidas de posicao e dispersao."], ["103", "**Arcane.Analytics**", "explore correlacao, percentis e outliers."], ["104", "**Regressao linear**", "ajuste uma reta e faca previsoes."], ["105", "**Dados tabulares**", "agrupe e resuma registros com Arcane.Analytics."], ["106", "**Arcane.IO**", "escreva, leia e apague um arquivo temporario."], ["107", "**JSON**", "serialize e desserialize estruturas."], ["108", "**Arcane.Database**", "crie uma tabela em memoria, insira e consulte."], ["109", "**Arcane.Text**", "formate um relatorio em caixa e tabela."], ["110", "**Arcane.Test**", "escreva asserts de biblioteca para uma funcao."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/09-modulos/099_adopt_local.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"09 · Modulos"}
      description={"12 exercícios: adopt, relay, seleção e apelidos."}
      href={"/docs/exercicios/09-modulos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
