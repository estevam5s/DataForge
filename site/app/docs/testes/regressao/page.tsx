// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes de regressão",
  description: "O teste que falha antes do conserto, o instantâneo — e por que todo bug vira teste.",
};

const blocos: Bloco[] = [
  {"p": "Um bug corrigido sem teste volta. Não por descuido: a correção é feita na pressa, e três meses depois alguém *“simplifica”* aquela linha estranha. O teste de regressão é o que explica, para sempre, por que a linha é estranha."},
  {"h2": "A ordem é o método"},
  {"list": ["**Reproduza** o bug num teste. Ele precisa falhar — pelo motivo do bug.", "**Corrija** o código. O teste passa.", "**Deixe o teste** com o nome do comportamento, e o número do chamado num comentário."], "ordered": true},
  { code: `adopt Arcane.Crucible

// Chamado #318: "Joao da Silva" virava "Joao Da Silva" na nota fiscal.
action titulo_de_nome(nome):
    miudas := ["da", "de", "do", "das", "dos", "e"]
    partes := []
    cycle p in nome.lower().split(" "):
        given p in miudas and len(partes) bigger 0:
            partes.append(p)
        otherwise:
            partes.append(capitalize(p))
    yield " ".join(partes)

crucible "nome na nota fiscal":
    // #318 — a preposicao ficava maiuscula
    trial "preposicao no meio fica minuscula":
        expect titulo_de_nome("JOAO DA SILVA") is "Joao da Silva"

    trial "mas no comeco e maiuscula":
        expect titulo_de_nome("de souza") is "De Souza"

r := Crucible.run()
assert r["falhou"] is 0`, lang: 'df' },
  {"h2": "O instantâneo, para o que é grande"},
  {"p": "Para uma saída de trinta linhas — um relatório, um HTML, um JSON — escrever o esperado à mão dá um teste que ninguém mantém. `Crucible.snapshot` grava na primeira vez e compara depois; `DF_ATUALIZAR_SNAPSHOT=1` aceita uma mudança **intencional**."},
  {"table": {"head": ["Instantâneo serve para", "Não serve para"], "rows": [["uma saída grande e estável", "um valor com data, hora ou id aleatório"], ["pegar a mudança **não pedida**", "descobrir se a saída está **certa** — na primeira vez ele aprova qualquer coisa"], ["HTML, relatório, JSON de rota", "o que cabe num `expect … is …`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Revise o diff do instantâneo", "texto": "Atualizar todos os instantâneos sem ler o diff transforma a regressão em aprovação automática. O arquivo vai para o controle de versão justamente para que a mudança apareça na revisão."}},
  {"p": "Continue em [Instantâneos](/docs/tecnicas/instantaneos) e [Mutação](/docs/crucible/mutacao)."},
];

const headings = [{ id: 'a-ordem-e-o-metodo', text: "A ordem é o método", level: 2 as const }, { id: 'o-instantaneo-para-o-que-e-grande', text: "O instantâneo, para o que é grande", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes de regressão"}
      description={"O teste que falha antes do conserto, o instantâneo — e por que todo bug vira teste."}
      href={"/docs/testes/regressao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
