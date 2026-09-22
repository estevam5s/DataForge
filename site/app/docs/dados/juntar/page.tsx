// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Juntar quadros",
  description: "Os quatro JOIN — dentro, esquerda, direita, fora — e as linhas que somem ou se multiplicam.",
};

const blocos: Bloco[] = [
  {"p": "`juntar` cruza dois quadros por uma coluna em comum, como o `JOIN` do SQL. O tipo decide o que acontece com as linhas que **não** casam — e é aí que moram os erros."},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"loja": "A", "valor": 10}, {"loja": "A", "valor": 20},
    {"loja": "B", "valor": 5}, {"loja": "B", "valor": 5}])
lojas := Q.de_vaults([{"loja": "A", "cidade": "Recife"}, {"loja": "C", "cidade": "Natal"}])

assert vendas.juntar(lojas, "loja").altura() is 2             // so o que casa
assert vendas.juntar(lojas, "loja", "esquerda").altura() is 4 // toda venda
assert vendas.juntar(lojas, "loja", "fora").altura() is 5     // tudo, dos dois lados

esq := vendas.juntar(lojas, "loja", "esquerda")
assert esq.onde(lambda l: l["loja"] is "B").coluna("cidade") is [void, void]
out esq.texto()`, lang: 'df' },
  {"table": {"head": ["Tipo", "Mantém", "Uso típico"], "rows": [["`dentro`", "só as linhas que casam nos dois", "vendas com cadastro válido"], ["`esquerda`", "toda linha da esquerda; a direita vira `void` onde falta", "**o mais comum**: enriquecer sem perder venda"], ["`direita`", "toda linha da direita", "lojas, com ou sem venda"], ["`fora`", "tudo dos dois lados", "conciliar duas fontes"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A chave repetida multiplica linhas", "texto": "Se o quadro da direita tiver a loja `A` duas vezes (um cadastro duplicado), cada venda de `A` sai **duas** vezes — e a soma dobra, calada. Antes de juntar, confira `lojas.duplicadas(\"loja\").altura() is 0`."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Juntar quadros"}
      description={"Os quatro JOIN — dentro, esquerda, direita, fora — e as linhas que somem ou se multiplicam."}
      href={"/docs/dados/juntar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
