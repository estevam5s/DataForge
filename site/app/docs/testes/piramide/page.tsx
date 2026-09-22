// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A pirâmide, e o que não testar",
  description: "Quantos de cada tipo, onde o custo mora — e as quatro coisas que não merecem teste.",
};

const blocos: Bloco[] = [
  {"p": "A pirâmide não é uma regra de proporção: é uma consequência de custo. Um teste unitário roda em milissegundos e aponta a linha; um ponta a ponta leva segundos e diz *“algo quebrou”*. Por isso a base é larga e o topo é estreito — e uma suíte de cabeça para baixo é lenta, instável e não diz onde procurar."},
  { code: `          ▲  ponta a ponta   poucos · segundos · "algo quebrou"
         ▲▲▲  integracao      dezenas · dezenas de ms · "qual encaixe"
      ▲▲▲▲▲▲▲  unitarios      centenas · milissegundos · "qual linha"`, lang: 'text' },
  {"h2": "Onde cada tipo de defeito aparece"},
  {"table": {"head": ["Defeito", "Onde ele é pego"], "rows": [["a conta de desconto errada", "unitário"], ["o SQL que o banco recusa", "integração"], ["o JSON que a rota não entende", "integração (`Kiln.test`)"], ["o `main.df` que não liga as peças", "ponta a ponta"], ["a corrida entre dois pedidos", "ponta a ponta, com servidor de verdade"], ["o teste que não testa", "mutação — [Crucible.mutar](/docs/crucible/mutacao)"]]}},
  {"h2": "O que não testar"},
  {"table": {"head": ["Não teste", "Porque"], "rows": [["a biblioteca dos outros", "`sorted` já é testado; teste o **seu** uso dele"], ["o código gerado", "teste o gerador — ou compare com a saída esperada"], ["o que não tem lógica (um `record` só com campos)", "o teste repete a declaração"], ["detalhes privados", "o teste quebra a cada refatoração que não mudou nada"]]}},
  {"h2": "Cobertura: um piso, não uma meta"},
  {"p": "`dataforge test --cobertura --minimo=80` reprova quando a cobertura cai — e é para isso que serve. Como meta ela mente: 100% de linhas executadas não diz que alguma coisa foi **conferida**. Um teste sem `expect` cobre tudo e não prova nada."},
  { code: `dataforge test tests/ --cobertura            # quais linhas rodaram
dataforge test tests/ --cobertura --minimo=80 # reprova abaixo de 80%
dataforge crucible tests/ --mutar src/regras.df  # o teste pega a mudanca?`, lang: 'bash' },
  {"p": "Continue em [Cobertura](/docs/tecnicas/cobertura) e [Testes instáveis](/docs/testes/instaveis)."},
];

const headings = [{ id: 'onde-cada-tipo-de-defeito-aparece', text: "Onde cada tipo de defeito aparece", level: 2 as const }, { id: 'o-que-nao-testar', text: "O que não testar", level: 2 as const }, { id: 'cobertura-um-piso-nao-uma-meta', text: "Cobertura: um piso, não uma meta", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A pirâmide, e o que não testar"}
      description={"Quantos de cada tipo, onde o custo mora — e as quatro coisas que não merecem teste."}
      href={"/docs/testes/piramide"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
