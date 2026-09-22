// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Renomear sem quebrar",
  description: "relay novo as antigo — o nome novo e o velho, o mesmo objeto, e o abi dizendo que é compatível.",
};

const blocos: Bloco[] = [
  {"p": "Renomear uma ação pública quebra todo programa que chama o nome antigo — no dia em que ele atualiza. `relay novo as antigo` exporta **o mesmo objeto** com os dois nomes: quem usa o antigo continua funcionando, e o código novo já usa o nome certo."},
  { code: `// precos.df — a versao 2
action total_com_imposto(valor):
    yield valor * 1.1

// Os dois nomes saem; o antigo e so um apelido.
relay total_com_imposto, total_com_imposto as total`, lang: 'text', title: `precos.df` },
  { code: `adopt ./precos as P
assert P.total is P.total_com_imposto        // o MESMO objeto
out P.total(100)`, lang: 'df', title: `main.df` },
  {"h2": "O `abi` concorda"},
  { code: `$ dataforge abi v1/precos.df v2/precos.df
  + total_com_imposto  [simbolo-novo]
  veredito: versao MENOR — so acrescimos compativeis

$ # sem o apelido, o mesmo rename:
  - total              [simbolo-removido]
  veredito: versao MAIOR`, lang: 'text' },
  {"table": {"head": ["Forma", "Efeito"], "rows": [["`relay a`", "`a` sai com o próprio nome"], ["`relay a as b`", "só `b` sai — `a` fica interno"], ["`relay a, a as b`", "os dois saem, e são o mesmo objeto"], ["`relay a as b, c as b`", "**recusado**: um nome exportado duas vezes"]]}},
  {"callout": {"tipo": "dica", "titulo": "Quer que o nome velho também avise?", "texto": "`relay` apenas mantém o nome funcionando. Para que ele avise quem o usa, `Arcane.Evolucao.renomeada(nova, \"antigo\", \"2.0\")` — ver [Obsolescência](/docs/bibliotecas/obsolescencia)."}},
];

const headings = [{ id: 'o-abi-concorda', text: "O `abi` concorda", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Renomear sem quebrar"}
      description={"relay novo as antigo — o nome novo e o velho, o mesmo objeto, e o abi dizendo que é compatível."}
      href={"/docs/modulos/renomear"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
