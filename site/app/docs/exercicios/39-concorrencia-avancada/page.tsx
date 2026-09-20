// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "39 · Concorrência avançada",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 39`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[257](#257-memoria-transacional-cas-e-estruturas-sem-trava)", "**Memoria transacional, CAS e estruturas sem trava**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "257 · Memoria transacional, CAS e estruturas sem trava"},
  { code: `// O problema esta medido neste repositorio: duas threads somando na
// mesma variavel entregaram 40.425 de 80.000, em silencio.
//
// O mutex resolve UMA secao critica. O que ele nao resolve e COMPOR:
// transferir de uma conta para outra sao duas escritas que precisam
// acontecer juntas — e com mutex isso vira ordem de aquisicao, que
// ninguem consegue verificar.

adopt Arcane.Stm as T
adopt Arcane.Concurrent as C
adopt Arcane.Collections as Col

// ── o incremento que nao se perde ──
total := T.variavel(0)

action somar_muitas(i):
    cycle _ in range(0, 200):
        T.atomicamente(lambda => T.escrever(total, T.ler(total) + 1))

C.para_cada(somar_muitas, [i cycle i in range(1, 41)])
assert T.valor(total) is 8000  // 40 threads x 200, nada perdido

// ── atomicidade: metade escrita nao existe ──
a := T.variavel(10)
b := T.variavel(10)

action quebrar_no_meio():
    T.escrever(a, 999)
    trigger "no meio"

monitor:
    T.atomicamente(quebrar_no_meio)
    assert no
handle Error as e:
    assert e.message is "no meio"

assert T.valor(a) is 10 and T.valor(b) is 10

// ── isolamento: a transacao le a propria escrita ──
x := T.variavel(1)

action ler_e_escrever():
    primeiro := T.ler(x)
    T.escrever(x, 5)
    yield [primeiro, T.ler(x)]

assert T.atomicamente(ler_e_escrever) is [1, 5]
assert T.valor(x) is 5

// ── composicao: aninhar e achatar ──
p := T.variavel(1)
q := T.variavel(1)

action dobrar_p():
    T.escrever(p, T.ler(p) * 2)

action dobrar_q():
    T.escrever(q, T.ler(q) * 2)

action as_duas():
    dobrar_p()  // ja e transacional
    dobrar_q()  // esta tambem

T.atomicamente(as_duas)  // e as duas viram UMA
assert T.valor(p) is 2 and T.valor(q) is 2

// ── esperar sem girar ──
fila := T.variavel([])
reserva := T.variavel(["de reserva"])

action da_fila():
    itens := T.ler(fila)
    given len(itens) is 0:
        T.retentar()  // vazia: dorme ate mudar
    yield itens[0]

action da_reserva():
    yield T.ler(reserva)[0]

assert T.atomicamente(lambda => T.ou_entao(da_fila, da_reserva)) is "de reserva"

// ler fora de transacao e recusado: nao teria garantia nenhuma
monitor:
    T.escrever(x, 9)
    assert no
handle RuntimeError as e:
    assert "transa" in e.message

// ── CAS: a troca condicional ──
atomo := C.atomico(10)
assert atomo.comparar_e_trocar(10, 20)  // ainda era 10
assert not atomo.comparar_e_trocar(10, 30)  // ja nao e
assert atomo.trocar(99) is 20  // devolve o ANTERIOR
assert atomo.pegar() is 99

// o contador sem trava, escrito com CAS
contador := C.atomico(0)

action incrementar():
    persist yes:
        atual := contador.pegar()
        given contador.comparar_e_trocar(atual, atual + 1):
            halt

action trabalhar(i):
    cycle _ in range(0, 200):
        incrementar()

C.para_cada(trabalhar, [i cycle i in range(1, 11)])
assert contador.pegar() is 2000

// ── estruturas sem trava ──
f := C.fila_sem_trava()

action produzir(i):
    cycle j in range(0, 100):
        f.por(i * 1000 + j)

C.para_cada(produzir, [i cycle i in range(1, 9)])
assert f.tamanho() is 800

vistos := []
persist f.tamanho() bigger 0:
    item := f.tirar()
    given item isnt void:
        vistos.append(item)

assert len(vistos) is 800
assert len(Col.set(vistos)) is 800  // nada duplicado

pilha := C.pilha_sem_trava()
pilha.por(1)
pilha.por(2)
assert pilha.tirar() is 2 and pilha.tirar() is 1
assert pilha.tirar() is void  // vazia: void, e nao erro

anel := C.anel(3)
cycle i from 1 to 5:
    anel.por(i)
assert anel.tudo() is [3, 4, 5]  // o mais velho sai quando enche

// ── executor e promessa ──
executor := C.executor(4)

action dobro(n):
    yield n * 2

tarefas := [executor.submeter(dobro, i) cycle i in range(1, 4)]
assert [C.esperar(t) cycle t in tarefas] is [2, 4, 6]
assert executor.mapear(dobro, [10, 20]) is [20, 40]
executor.fechar()
assert not executor.aberto()

promessa := C.promessa()

action cumprir_depois(i):
    promessa.cumprir("pronto")

C.rodar(cumprir_depois, 1)
assert promessa.esperar(3000) is "pronto"

// uma promessa que falha leva a falha a quem espera
ruim := C.promessa()
ruim.falhar("deu ruim")
monitor:
    ruim.esperar(1000)
    assert no
handle Error as e:
    assert "deu ruim" in e.message

out "257 ok"`, lang: 'df', title: `exercicios/39-concorrencia-avancada/257_stm_e_atomicos.df` },
  {"h3": "O problema, medido"},
  {"p": "Duas threads somando na mesma variável entregaram **40.425 de 80.000** neste repositório — em silêncio. O `mutex` resolve **uma** seção crítica. O que ele não resolve é **compor**: transferir de uma conta para outra são duas escritas que precisam acontecer juntas, e com mutex isso vira ordem de aquisição — uma regra que ninguém consegue verificar, e cuja violação é impasse."},
  {"h3": "A transação"},
  {"p": "`T.atomicamente(acao)` roda a ação num **rascunho**: tudo o que ela lê guarda a versão, e tudo o que ela escreve fica de lado. No fim, sob uma trava curta, ela confere se alguma variável lida mudou. Se mudou, descarta e tenta de novo; se não, publica tudo de uma vez."},
  {"p": "Quatro consequências:"},
  {"p": "1. **atomicidade** — um erro no meio não deixa metade escrita, e o erro sobe (engoli-lo seria o oposto de atomicidade); 2. **isolamento** — a transação lê a própria escrita, não a dos outros; 3. **composição** — aninhar é achatar: duas ações transacionais dentro de uma terceira são **uma** transação; 4. **conflito custa repetição**, e não dado errado. As estatísticas dizem quanto."},
  {"h3": "Esperar sem girar"},
  {"p": "`T.retentar()` diz \"não dá para seguir com o que existe agora\". A transação é abandonada e **dorme** até alguma variável que ela leu mudar. `T.ou_entao(a, b)` tenta a segunda quando a primeira pede para esperar — é a composição de duas operações bloqueantes, que um mutex não tem."},
  {"h3": "Nunca faça E/S dentro de uma transação"},
  {"p": "Ela pode ser **repetida**, e o que já saiu não volta: um `out`, um `IO.write` ou um `Http.post` lá dentro aconteceria duas vezes. Junte o resultado dentro e faça a E/S depois."},
  {"h3": "CAS: a peça de baixo"},
  {"p": "`comparar_e_trocar(esperado, novo)` troca **só se** o valor ainda for o que você leu. O laço clássico — leia, calcule, troque se ninguém mexeu — é como se escreve qualquer atualização sem trava."},
  {"h3": "O que \"sem trava\" quer dizer aqui"},
  {"p": "`append` e `popleft` de um `deque` acontecem inteiros em C: não há janela entre ler e escrever. Isso está medido — quatro threads com 5 mil `append` cada entregaram 20.000 de 20.000."},
  {"p": "O que **não** é indivisível é qualquer sequência escrita em DataForge: `v[\"n\"] := v[\"n\"] + 1` perde atualização. Ali a resposta é `atomico`, `mutex` ou transação."},
  {"p": "E `lock-free` não é `wait-free`: o laço de CAS repete quando há disputa, e uma thread azarada pode repetir muitas vezes."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/39-concorrencia-avancada/257_stm_e_atomicos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '257-memoria-transacional-cas-e-estruturas-sem-trava', text: "257 · Memoria transacional, CAS e estruturas sem trava", level: 2 as const }, { id: 'o-problema-medido', text: "O problema, medido", level: 3 as const }, { id: 'a-transacao', text: "A transação", level: 3 as const }, { id: 'esperar-sem-girar', text: "Esperar sem girar", level: 3 as const }, { id: 'nunca-faca-es-dentro-de-uma-transacao', text: "Nunca faça E/S dentro de uma transação", level: 3 as const }, { id: 'cas-a-peca-de-baixo', text: "CAS: a peça de baixo", level: 3 as const }, { id: 'o-que-sem-trava-quer-dizer-aqui', text: "O que \"sem trava\" quer dizer aqui", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"39 · Concorrência avançada"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/39-concorrencia-avancada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
