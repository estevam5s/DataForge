// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_resultado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Resultado e Talvez",
  description: "A falha como valor: ok/falha com mapear, entao e recuperar; e Talvez para onde void é ambíguo — as três formas de lidar com o que dá errado.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem tem **três** formas de lidar com o que dá errado, e elas respondem a perguntas diferentes. Escolher a errada é o que produz código que engole erro ou que interrompe o que devia continuar."},
  {"table": {"head": ["Forma", "Quando", "O que acontece"], "rows": [["`monitor` / `handle` / `trigger`", "o que **não era esperado**: disco cheio, rede caída, bug", "interrompe e sobe até quem sabe tratar"], ["`void` com `??` e `?.`", "a **ausência** simples: campo opcional, cache vazio", "segue com um padrão"], ["`Arcane.Resultado`", "a falha **esperada** de uma fronteira: validação, busca, parsing", "vira valor, e quem chama decide"]]}},
  {"callout": {"tipo": "nota", "titulo": "A regra prática", "texto": "Se quem chama **precisa** decidir o que fazer, devolva `Resultado`. Se ninguém ali pode fazer nada a respeito, `trigger`. Um `Resultado` que todo mundo ignora é pior que um erro; um `trigger` para o que era esperado obriga `monitor` em todo lugar."}},
  {"h2": "ok e falha"},
  { code: `adopt Arcane.Resultado as R

action buscar(id) -> Resultado:
    given id smaller 0:
        yield R.falha("id negativo", 400)
    yield R.ok({"id": id, "nome": "Ana"})

achado := buscar(7)
perdido := buscar(-1)

assert achado.deu_certo()
assert achado.valor()["nome"] is "Ana"

assert perdido.falhou()
assert perdido.erro() is "id negativo"
assert perdido.detalhe() is 400
assert perdido.ou("ninguém") is "ninguém" `, lang: 'df' },
  {"h2": "A falha atravessa a corrente"},
  {"p": "`mapear` muda o valor, `entao` encadeia outra operação que também devolve `Resultado`, e `recuperar` dá outra chance. A falha passa por todos eles **intacta** — é isso que dispensa um `given` entre cada passo."},
  { code: `adopt Arcane.Resultado as R

action dobro(x):
    yield R.ok(x * 2)

assert R.ok(2).mapear(lambda x => x + 1).valor() is 3
assert R.ok(2).entao(dobro).valor() is 4

assert R.falha("parou").mapear(lambda x => x + 1).erro() is "parou"
assert R.falha("parou").entao(dobro).erro() is "parou"
assert R.falha("parou").recuperar(lambda motivo => R.ok(0)).valor() is 0`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Ler o valor de uma falha levanta", "texto": "`r.valor()` numa falha é uma afirmação — e ela levanta, com o motivo dentro da mensagem. Quem não quer afirmar usa `r.ou(padrao)`, que nunca levanta, ou `r.exigir(\"mensagem própria\")`, que levanta com a frase de quem chamou."}},
  {"h2": "tentar: transformar erro em valor, uma vez"},
  {"p": "`R.tentar` roda a ação e devolve `ok` ou `falha` com a mensagem. Ele captura o erro da **linguagem** — um sinal de controle (`halt`, `skip`, `yield`) atravessa, senão um `halt` dentro dele viraria falha em vez de sair do laço."},
  { code: `adopt Arcane.Resultado as R

action dividir(a, b):
    yield a / b

assert R.tentar(dividir, 10, 2).valor() is 5.0

ruim := R.tentar(dividir, 1, 0)
assert ruim.falhou()
assert "zero" in ruim.erro()`, lang: 'df' },
  {"h2": "todos: a validação inteira, ou o primeiro motivo"},
  {"p": "É o que se quer ao validar um formulário: ou sai a lista pronta, ou sai o motivo — e não uma lista com buracos. `R.erros` faz o contrário, e reúne **todos** os motivos para relatar de uma vez."},
  { code: `adopt Arcane.Resultado as R

assert R.todos([R.ok(1), R.ok(2), R.ok(3)]).valor() is [1, 2, 3]
assert R.todos([R.ok(1), R.falha("cpf"), R.falha("email")]).erro() is "cpf"
assert R.erros([R.ok(1), R.falha("cpf"), R.falha("email")]) is ["cpf", "email"]`, lang: 'df' },
  {"h2": "Talvez: quando void é ambíguo"},
  {"p": "`void` resolve a ausência em quase todo lugar. O que ele não resolve é **distinguir** \"a chave não está lá\" de \"a chave está lá e vale void\" — que é exatamente a dúvida de um vault de configuração, de um cache e de uma busca."},
  { code: `adopt Arcane.Resultado as R

config := {"tema": void}

tem := R.chave(config, "tema")
nao := R.chave(config, "idioma")

assert tem.tem() and tem.valor() is void      // está lá, e vale void
assert not nao.tem()
assert nao.ou("pt-BR") is "pt-BR"

assert R.algo(2).mapear(lambda x => x * 5).valor() is 10
assert R.nada().mapear(lambda x => x * 5).ou("nada") is "nada"
assert not R.algo(4).filtrar(lambda x => x bigger 10).tem()
assert R.primeiro([1, 2, 3], lambda x => x bigger 2).valor() is 3
assert R.nada().para_resultado("vazio").erro() is "vazio" `, lang: 'df' },
  {"h2": "A superfície"},
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`R.ok(valor)` · `R.falha(erro, detalhe)`", "cria o resultado"], ["`R.tentar(acao, …)`", "roda e captura o erro da linguagem"], ["`R.de(valor, motivo)`", "`void` vira falha; o resto vira `ok`"], ["`R.todos(lista)` · `R.erros(lista)`", "junta, ou reúne os motivos"], ["`r.deu_certo()` · `r.falhou()`", "pergunta"], ["`r.valor()` · `r.erro()` · `r.detalhe()`", "lê — `valor()` levanta na falha"], ["`r.ou(padrao)` · `r.exigir(msg)`", "lê sem levantar, ou com a sua mensagem"], ["`r.mapear(f)` · `r.entao(f)` · `r.recuperar(f)`", "transforma, encadeia, recupera"], ["`R.algo(v)` · `R.nada()` · `R.talvez(v)`", "cria o `Talvez`"], ["`R.primeiro(colecao, cond)` · `R.chave(vault, nome)`", "busca que pode não achar"], ["`t.tem()` · `t.valor()` · `t.ou(p)` · `t.mapear(f)` · `t.filtrar(f)`", "o `Talvez`"], ["`t.para_resultado(motivo)`", "vira `Resultado`"]]}},
];

const headings = [{ id: 'ok-e-falha', text: "ok e falha", level: 2 as const }, { id: 'a-falha-atravessa-a-corrente', text: "A falha atravessa a corrente", level: 2 as const }, { id: 'tentar-transformar-erro-em-valor-uma-vez', text: "tentar: transformar erro em valor, uma vez", level: 2 as const }, { id: 'todos-a-validacao-inteira-ou-o-primeiro-motivo', text: "todos: a validação inteira, ou o primeiro motivo", level: 2 as const }, { id: 'talvez-quando-void-e-ambiguo', text: "Talvez: quando void é ambíguo", level: 2 as const }, { id: 'a-superficie', text: "A superfície", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Resultado e Talvez"}
      description={"A falha como valor: ok/falha com mapear, entao e recuperar; e Talvez para onde void é ambíguo — as três formas de lidar com o que dá errado."}
      href={"/docs/tipos/resultado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
