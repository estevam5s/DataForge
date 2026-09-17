// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Métricas e cheiros",
  description: "dataforge oop: WMC, DIT, NOC, CBO, RFC, LCOM, fan-in, instabilidade e manutenibilidade — e os anti-padrões ligados ao princípio SOLID que ferem.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge oop` lê a árvore, sem executar, e mede cada blueprint pelas métricas de Chidamber e Kemerer — as que a engenharia de software usa desde 1994 para prever onde os defeitos aparecem."},
  { code: `dataforge oop src/
dataforge oop src/ --diagrama > classes.mmd
dataforge oop src/ --hierarquia
dataforge oop src/ --json
dataforge oop src/ --strict      # sai com erro se houver cheiro`, lang: 'bash' },
  {"table": {"head": ["Métrica", "O que mede", "Alto significa"], "rows": [["WMC", "soma da complexidade ciclomática dos métodos", "difícil de testar"], ["DIT", "profundidade na árvore de herança", "comportamento espalhado pelas mães"], ["NOC", "filhas diretas", "mudar a mãe afeta muita gente"], ["CBO", "com quantos tipos ele conversa", "acoplamento"], ["RFC", "métodos próprios + métodos que ele chama", "resposta difícil de prever"], ["LCOM", "0 coeso, 1 cada método mexe no seu campo", "vários blueprints dentro de um"], ["fan-in / fan-out", "quem depende dele / de quem ele depende", ""], ["instabilidade", "fan-out / (fan-in + fan-out)", "0 estável, 1 fácil de mudar"], ["MI", "índice de manutenibilidade, 0 a 100", "baixo é caro de manter"]]}},
  {"h2": "Cada cheiro diz o princípio"},
  {"table": {"head": ["Cheiro", "Princípio", "O que fazer"], "rows": [["`god-blueprint`", "SRP", "separar o que muda por motivos diferentes"], ["`baixa-coesao`", "SRP", "grupos de métodos com grupos de campos são blueprints diferentes"], ["`metodo-longo`", "SRP", "extrair passos com nome"], ["`switch-de-tipo`", "OCP", "um método no contrato, sobrescrito por cada tipo"], ["`sobrescrita-que-recusa`", "LSP", "se a filha não cumpre, ela não é subtipo"], ["`contrato-gordo`", "ISP", "contratos pequenos, um por cliente"], ["`dependencia-concreta`", "DIP", "receber pelo construtor, tipado pelo contrato"], ["`heranca-funda`", "composição sobre herança", "trocar níveis por campos"], ["`acoplamento-excessivo`", "baixo acoplamento", "depender de contratos"], ["`modelo-anemico`", "tell, don't ask", "trazer a regra para perto dos dados"], ["`inveja-de-recurso`", "tell, don't ask", "o método talvez pertença ao outro objeto"], ["`parametros-demais`", "KISS", "agrupar num record"], ["`dependencia-circular`", "acoplamento", "extrair um contrato"]]}},
  {"p": "Os limites estão numa tabela só (`LIMITES` em `dataforge/oop_analise.py`), porque são opinião — e opinião escrita em um lugar é discutível; espalhada, não. Os cheiros são sugestões: um blueprint que agrega e roteia pode ter CBO alto de propósito, e o comando só reprova com `--strict`."},
  {"h2": "O que o check prova, e o que o oop sugere"},
  {"p": "A fronteira é a certeza. O `dataforge check` acusa o que dá para **provar** e é erro em qualquer leitura: `override` sem alvo, herança de `final`, contrato incompleto ou com aridade incompatível, `readonly` escrito fora da construção, gancho de metaclasse desconhecido, variantes de `overload` com a mesma assinatura, `spawn` de contrato. O `dataforge oop` aponta o que é **provável**, e deixa a decisão com quem escreveu."},
];

const headings = [{ id: 'cada-cheiro-diz-o-principio', text: "Cada cheiro diz o princípio", level: 2 as const }, { id: 'o-que-o-check-prova-e-o-que-o-oop-sugere', text: "O que o check prova, e o que o oop sugere", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Métricas e cheiros"}
      description={"dataforge oop: WMC, DIT, NOC, CBO, RFC, LCOM, fan-in, instabilidade e manutenibilidade — e os anti-padrões ligados ao princípio SOLID que ferem."}
      href={"/docs/oop/metricas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
