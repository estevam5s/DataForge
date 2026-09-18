// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_stm.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Memória transacional",
  description: "Escritas que acontecem juntas ou não acontecem: variável transacional, atomicamente, retentar e ou_entao — a composição que o mutex não tem.",
};

const blocos: Bloco[] = [
  {"p": "O problema está medido neste repositório: duas threads somando na mesma variável entregaram **40.425 de 80.000**, em silêncio. As respostas que existiam eram `mutex` — e a disciplina de lembrar dele em todo lugar — e `contador`, que só serve para contar."},
  {"p": "O que nenhuma das duas resolve é **compor**. Transferir de uma conta para outra são duas escritas que precisam acontecer juntas ou não acontecer. Com mutex isso vira ordem de aquisição, e ordem errada é impasse — uma regra que ninguém consegue verificar."},
  {"h2": "A transação"},
  { code: `adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

total := T.variavel(0)

action somar(i):
    cycle _ in range(0, 200):
        T.atomicamente(lambda => T.escrever(total, T.ler(total) + 1))

C.para_cada(somar, [i cycle i in range(1, 41)])
assert T.valor(total) is 8000          // 40 threads, 200 somas, nada perdido`, lang: 'df' },
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`T.variavel(v)`", "cria a variável transacional"], ["`T.atomicamente(acao)`", "roda a ação como transação: tudo, ou nada"], ["`T.ler(v)` · `T.escrever(v, x)`", "só valem **dentro** de uma transação"], ["`T.modificar(v, f)`", "`escrever(v, f(ler(v)))` — a forma que não esquece o ler"], ["`T.valor(v)`", "uma **foto**, fora de transação, sem promessa nenhuma"], ["`T.retentar()`", "desiste e **espera** alguma variável lida mudar"], ["`T.ou_entao(a, b)`", "tenta a primeira; se ela pedir para esperar, tenta a segunda"], ["`T.estatisticas()`", "confirmadas, conflitos, retentativas, esperas"]]}},
  {"h2": "Atomicidade: metade escrita não existe"},
  { code: `adopt Arcane.Stm as T

a := T.variavel(10)
b := T.variavel(10)

action quebrar():
    T.escrever(a, 999)
    trigger "no meio"

monitor:
    T.atomicamente(quebrar)
handle Error as e:
    assert e.message is "no meio"

assert T.valor(a) is 10 and T.valor(b) is 10      // nada foi publicado`, lang: 'df' },
  {"p": "O erro **não é engolido**: a transação desfaz o rascunho e o erro sobe para quem chamou decidir. Engoli-lo transformaria uma falha num silêncio, que é o oposto do que atomicidade significa."},
  {"h2": "Isolamento: a transação vê a própria escrita"},
  { code: `adopt Arcane.Stm as T

x := T.variavel(1)

action dentro():
    primeiro := T.ler(x)
    T.escrever(x, 5)
    yield [primeiro, T.ler(x)]        // lê o que ela mesma escreveu

assert T.atomicamente(dentro) is [1, 5]
assert T.valor(x) is 5`, lang: 'df' },
  {"h2": "Composição: duas transações viram uma"},
  {"p": "É o que o mutex não dá. Duas operações que já são transacionais podem ser chamadas dentro de uma terceira, e aí elas são **uma só** transação — aninhar é achatar."},
  { code: `adopt Arcane.Stm as T

a := T.variavel(1)
b := T.variavel(1)

action dobrar_a():
    T.escrever(a, T.ler(a) * 2)

action dobrar_b():
    T.escrever(b, T.ler(b) * 2)

action as_duas():
    dobrar_a()
    dobrar_b()

T.atomicamente(as_duas)               // uma transação, duas escritas
assert T.valor(a) is 2 and T.valor(b) is 2`, lang: 'df' },
  {"h2": "Esperar sem girar: retentar e ou_entao"},
  {"p": "`T.retentar()` diz \"não dá para seguir com o que existe agora\". A transação é abandonada e **dorme** até alguma variável que ela leu mudar — um `persist` girando gastaria um núcleo para não fazer nada."},
  { code: `adopt Arcane.Stm as T

fila := T.variavel([])
reserva := T.variavel(["de reserva"])

action da_fila():
    itens := T.ler(fila)
    given len(itens) is 0:
        T.retentar()                  // vazia: espera
    yield itens[0]

action da_reserva():
    yield T.ler(reserva)[0]

// ou_entao: a primeira pediu para esperar, então vai a segunda
assert T.atomicamente(lambda => T.ou_entao(da_fila, da_reserva)) is "de reserva" `, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Ler fora de uma transação é recusado", "texto": "`T.ler(v)` e `T.escrever(v, x)` sem transação levantam, dizendo por quê: um valor lido solto não teria garantia nenhuma — com cara de garantia. Para a foto existe `T.valor(v)`, que diz no nome o que é."}},
  {"h2": "Como funciona, e o que custa"},
  {"p": "Otimismo com validação, no modelo clássico: a transação lê e escreve num **rascunho**; no fim, sob uma trava curta, confere se alguma variável lida mudou de versão; se mudou, descarta tudo e tenta de novo; se não, publica as escritas de uma vez e acorda quem espera."},
  {"table": {"head": ["Custo", "Quando aparece"], "rows": [["trabalho repetido", "quando duas transações escrevem na **mesma** variável ao mesmo tempo — o conflito custa repetição, e não dado errado"], ["a trava do commit", "curta de propósito: protege a validação e a publicação, não o corpo. Se protegesse o corpo, isto seria um mutex global com outro nome"], ["memória do rascunho", "proporcional ao que a transação leu e escreveu"]]}},
  { code: `adopt Arcane.Stm as T
adopt Arcane.Concurrent as C

x := T.variavel(0)

action somar(i):
    cycle _ in range(0, 50):
        T.atomicamente(lambda => T.escrever(x, T.ler(x) + 1))

C.para_cada(somar, [i cycle i in range(1, 9)])

estat := T.estatisticas()
assert T.valor(x) is 400
assert estat["confirmadas"] bigger_eq 400
assert estat["conflitos"] bigger_eq 0     // o preço do otimismo, medido`, lang: 'df' },
  {"h2": "Quando usar cada peça"},
  {"table": {"head": ["Situação", "A peça"], "rows": [["contar", "`C.contador()` ou `C.atomico(0).somar(1)`"], ["uma escrita só, condicional", "`C.atomico(v).comparar_e_trocar(…)`"], ["**duas ou mais escritas que andam juntas**", "`T.atomicamente(…)`"], ["esperar por uma condição de dado", "`T.retentar()` dentro da transação"], ["proteger uma seção crítica com E/S", "`C.mutex()` — transação repete, e repetir um `out` imprimiria duas vezes"], ["passar trabalho entre threads", "`C.canal()`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Não faça E/S dentro de uma transação", "texto": "A transação pode ser **repetida**, e o que já saiu não volta: um `out`, um `IO.write` ou um `Http.post` lá dentro aconteceria duas vezes. Junte o resultado dentro da transação e faça a E/S depois dela."}},
];

const headings = [{ id: 'a-transacao', text: "A transação", level: 2 as const }, { id: 'atomicidade-metade-escrita-nao-existe', text: "Atomicidade: metade escrita não existe", level: 2 as const }, { id: 'isolamento-a-transacao-ve-a-propria-escrita', text: "Isolamento: a transação vê a própria escrita", level: 2 as const }, { id: 'composicao-duas-transacoes-viram-uma', text: "Composição: duas transações viram uma", level: 2 as const }, { id: 'esperar-sem-girar-retentar-e-ouentao', text: "Esperar sem girar: retentar e ou_entao", level: 2 as const }, { id: 'como-funciona-e-o-que-custa', text: "Como funciona, e o que custa", level: 2 as const }, { id: 'quando-usar-cada-peca', text: "Quando usar cada peça", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Memória transacional"}
      description={"Escritas que acontecem juntas ou não acontecem: variável transacional, atomicamente, retentar e ou_entao — a composição que o mutex não tem."}
      href={"/docs/concorrencia/stm"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
