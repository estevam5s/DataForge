// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Listas, vaults e conjuntos",
  description: "Guardar muitos valores: a lista em ordem, o vault por nome, o conjunto sem repetição.",
};

const blocos: Bloco[] = [
  {"p": "Uma variável guarda um valor. Para guardar muitos, há três coleções, e cada uma responde uma pergunta diferente."},
  {"table": {"head": ["Coleção", "Escreve", "Responde"], "rows": [["**Cluster** (lista)", "`[10, 20, 30]`", "*qual é o terceiro?* — pela posição, a partir de 0"], ["**Vault** (dicionário)", "`{\"nome\": \"Ana\"}`", "*qual é o nome?* — pela chave"], ["**Set** (conjunto)", "`{\"azul\", \"verde\"}`", "*isto está aqui?* — sem repetição e sem ordem"]]}},
  { code: `notas := [7.5, 9, 6]
notas.append(10)
out notas[0], notas[-1], len(notas)     // o primeiro, o ultimo, quantos
assert notas[1] is 9

aluna := {"nome": "Ana", "idade": 20}
aluna["curso"] := "Matematica"
out aluna["nome"], "cursa", aluna["curso"]
assert "idade" in aluna

cores := {"azul", "verde", "azul"}       // a repeticao some
assert len(cores) is 2 and "verde" in cores
assert set([1, 1, 2]) is {1, 2}`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A lista começa no zero", "texto": "`notas[0]` é o **primeiro** item, e `notas[1]` o segundo. É a convenção de quase toda linguagem, e o erro mais comum de quem começa. `notas[-1]` é o último, sem precisar saber o tamanho."}},
  {"h2": "Percorrer"},
  { code: `produtos := {"cafe": 18.5, "pao": 7.0, "leite": 5.2}
total := 0
cycle nome in produtos:
    out $"{nome}: R$ {produtos[nome]}"
    total += produtos[nome]
assert total is 30.7`, lang: 'df' },
  {"p": "Próximo: [Ações](/docs/primeiros-passos/acoes)."},
];

const headings = [{ id: 'percorrer', text: "Percorrer", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Listas, vaults e conjuntos"}
      description={"Guardar muitos valores: a lista em ordem, o vault por nome, o conjunto sem repetição."}
      href={"/docs/primeiros-passos/colecoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
