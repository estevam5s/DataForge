// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Adotar do Python",
  description: "adopt Python.x — o que atravessa, o que não converte, e o custo para quem instala.",
};

const blocos: Bloco[] = [
  {"p": "`adopt Python.statistics as st` traz qualquer módulo do Python. A ponte **não converte**: o objeto do Python chega como está, e a linguagem conversa com ele por protocolo — membro, método, índice, `len`, iteração, conta."},
  { code: `adopt Python.statistics as st
adopt Python.fractions as fr

assert st.median([3, 1, 2]) is 2
um_terco := fr.Fraction(1, 3)
assert um_terco + um_terco + um_terco is 1     // exato: nenhum float no caminho
out typeof(um_terco)     // 'Float' — o typeof responde pela familia numerica"`, lang: 'df' },
  {"table": {"head": ["Vale", "Não vale"], "rows": [["o módulo é da biblioteca padrão do Python (sem instalar)", "existe o mesmo em `Arcane.*`"], ["uma biblioteca madura para um formato binário complexo", "*“pode ser mais rápido”* sem medir"], ["cálculo numérico pesado (numpy)", "num pacote publicado, sem declarar a dependência"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`Python` é espaço reservado", "texto": "`adopt Python.x` é resolvido **antes** da biblioteca e dos arquivos vizinhos: um `Python.df` no disco não sequestra o import. E um módulo que não está instalado recebe uma mensagem com o Python exato onde instalar — a venv do DataForge não é a do terminal."}},
  {"p": "Continue em [A ponte](/docs/tecnicas/ponte)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Adotar do Python"}
      description={"adopt Python.x — o que atravessa, o que não converte, e o custo para quem instala."}
      href={"/docs/modulos/python"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
