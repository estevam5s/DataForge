// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Variáveis vivas",
  description: "Um valor está vivo enquanto ainda vai ser lido: a análise que acha o parâmetro esquecido e a conta inútil.",
};

const blocos: Bloco[] = [
  {"p": "Uma variável está **viva** num ponto do programa quando o valor dela ainda vai ser lido por algum caminho a partir dali. É a análise que diz qual cálculo é inútil (o resultado nunca é lido) e qual parâmetro sobrou (nunca é lido em caminho nenhum)."},
  { code: `adopt Arcane.Compilador as Comp

fonte := "action preco(base, desconto, taxa):\\n    final := base * 1.1\\n    yield final\\n"
vivas := Comp.vivas(fonte, "preco")
out vivas
assert vivas["0"] is ["base"]           // 'desconto' e 'taxa' nunca são lidos`, lang: 'df' },
  {"p": "A análise corre **para trás**: sai do fim de cada bloco e sobe, porque é o futuro de um ponto que decide se o valor ainda serve. E junta os caminhos — num `given`, uma variável lida em qualquer dos ramos está viva antes dele."},
  {"table": {"head": ["Resultado", "Quer dizer"], "rows": [["parâmetro nunca vivo", "ele sobrou — ou a ação esqueceu de usá-lo"], ["atribuição cujo nome não está vivo depois", "a conta é jogada fora"], ["nome vivo na entrada que não é parâmetro", "ele é lido antes de ser escrito: vem de fora, ou é erro"]]}},
  {"p": "É a mesma família de análise que produz o aviso `talvez-nao-definida`: ver [O que o fluxo prova](/docs/compilador/analises)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Variáveis vivas"}
      description={"Um valor está vivo enquanto ainda vai ser lido: a análise que acha o parâmetro esquecido e a conta inútil."}
      href={"/docs/compilador/vivas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
