// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Limpar dados",
  description: "Perfil primeiro, depois ausência, tipos, duplicatas e valores fora da curva — nessa ordem.",
};

const blocos: Bloco[] = [
  {"p": "Limpar sem olhar é adivinhar. O primeiro passo é o **perfil**: por coluna, o tipo inferido, quantos faltam, quantos distintos, mínimo e máximo. Ele diz onde está o problema antes de você mexer em qualquer coisa."},
  { code: `adopt Arcane.Quadro as Q

bruto := Q.de_vaults([
    {"id": 1, "idade": "34", "cidade": "Recife"},
    {"id": 2, "idade": "", "cidade": "recife "},
    {"id": 2, "idade": "", "cidade": "recife "},
    {"id": 3, "idade": "trinta", "cidade": "Natal"},
    {"id": 4, "idade": "290", "cidade": "Natal"}])

out bruto.perfil().texto()

limpo := bruto
    .sem_duplicadas()
    .converter({"idade": "Integer"})                         // 'trinta' vira void
    .mapear("cidade", lambda c: (c ?? "").trim().capitalize())

assert limpo.altura() is 4
assert limpo.coluna("idade") is [34, void, void, 290]
assert limpo.coluna("cidade") is ["Recife", "Recife", "Natal", "Natal"]`, lang: 'df' },
  {"table": {"head": ["Ordem", "Passo", "Verbo"], "rows": [["1", "olhar", "`perfil()`"], ["2", "tirar a linha repetida", "`sem_duplicadas(por)`"], ["3", "converter os tipos", "`converter({…})` — o que falha vira `void`, contado no perfil"], ["4", "padronizar o texto", "`mapear` com `trim`, `lower`, `capitalize`"], ["5", "decidir a ausência", "`preencher(\"media\")`, `sem_nulos()`, ou deixar"], ["6", "olhar o que sobrou fora da curva", "`fora_da_curva(col)` — **olhar**, não apagar"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Fora da curva não é erro", "texto": "Uma idade de 290 é erro de digitação; uma venda 30 vezes maior que a média pode ser o maior cliente do ano. `fora_da_curva` devolve as linhas para você **olhar** — apagar automaticamente o que é raro é apagar exatamente o que mais importa."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Limpar dados"}
      description={"Perfil primeiro, depois ausência, tipos, duplicatas e valores fora da curva — nessa ordem."}
      href={"/docs/dados/limpeza"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
