// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cenários — dado, quando, então",
  description: "Comportamento escrito como frase, e a falha que diz em qual frase quebrou.",
};

const blocos: Bloco[] = [
  {"p": "`Crucible.cenario` escreve o teste como o comportamento é descrito: *dado* o estado, *quando* algo acontece, *então* o resultado. O ganho não é a sintaxe — é que a falha passa a dizer **em qual frase** quebrou, e essa frase é a que o negócio escreveu."},
  { code: `adopt Arcane.Crucible as C

c := C.cenario("saque acima do saldo")
c.dado("uma conta com R$ 100", lambda m: m.set("saldo", 100))
c.e("um limite de R$ 50", lambda m: m.set("limite", 50))
c.quando("tento sacar R$ 120", lambda m: m.set("ok", 120 smaller_eq m["saldo"] + m["limite"]))
c.entao("o saque e aceito", lambda m: m["ok"])
c.e("o saldo seria negativo", lambda m: m["saldo"] - 120 smaller 0)

out c.texto()
r := c.rodar()
assert r["ok"] and len(r["passos"]) is 5`, lang: 'df' },
  {"h2": "A falha nomeia o passo"},
  { code: `adopt Arcane.Crucible as C

c := C.cenario("frete gratis")
c.dado("um carrinho de R$ 180", lambda m: m.set("total", 180))
c.quando("calculo o frete", lambda m: m.set("frete", 0 given m["total"] bigger_eq 200 otherwise 15))
c.entao("o frete e zero", lambda m: m["frete"] is 0)

monitor:
    c.rodar()
    assert no
handle Error as e:
    out e.message
    assert "passo 3" in e.message and "o frete e zero" in e.message`, lang: 'df' },
  {"h2": "As três regras que ele cobra"},
  {"table": {"head": ["Regra", "Porque"], "rows": [["a ordem é **dado → quando → então**", "um preparo depois da ação faz o cenário testar duas coisas, e a falha não diz qual — um `dado` depois de `quando` é recusado na montagem"], ["**sem `entao` não há cenário**", "um cenário que só prepara e age não confere nada, e passaria sempre"], ["os passos dividem **um `mundo`**", "variável solta entre passos esconde de onde veio o valor que o `entao` confere"]]}},
  {"callout": {"tipo": "nota", "titulo": "Não é Gherkin, e não é Cucumber", "texto": "Não há arquivo `.feature` separado nem casamento de frase por expressão regular. A frase e a ação moram juntas, no mesmo arquivo — o que se perde em separação ganha-se em não haver dois lugares que precisam concordar."}},
  {"p": "Continue em [Testes de integração](/docs/testes/integracao)."},
];

const headings = [{ id: 'a-falha-nomeia-o-passo', text: "A falha nomeia o passo", level: 2 as const }, { id: 'as-tres-regras-que-ele-cobra', text: "As três regras que ele cobra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cenários — dado, quando, então"}
      description={"Comportamento escrito como frase, e a falha que diz em qual frase quebrou."}
      href={"/docs/testes/bdd"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
