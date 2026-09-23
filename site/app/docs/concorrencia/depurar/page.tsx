// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Depurar uma corrida",
  description: "O defeito que some quando você olha — e as quatro técnicas que funcionam mesmo assim.",
};

const blocos: Bloco[] = [
  {"p": "Uma condição de corrida tem a pior propriedade possível para depuração: **ela some quando se olha**. Acrescentar um `out` muda o tempo, o depurador serializa as threads, e o defeito não reproduz — o que leva à conclusão errada de que ele foi corrigido."},
  {"h2": "1. Aumentar a janela, de propósito"},
  {"p": "Se você suspeita de um ler-modificar-escrever, **alargue** o intervalo entre ler e escrever. Um defeito que acontece em 1 de 10 mil passa a acontecer em 9 de 10:"},
  { code: `adopt Arcane.Concurrent as C

estado := {"n": 0}

action somar_com_janela():
    cycle i from 1 to 50:
        lido := estado["n"]
        sleep(1)                  // a janela, alargada de propósito
        estado["n"] := lido + 1

parallel:
    somar_com_janela()
    somar_com_janela()

// Com a janela aberta, a perda aparece quase sempre.
out $"esperado 100, obtido {estado['n']}"
assert estado["n"] <= 100`, lang: 'df' },
  {"p": "Isto é uma técnica de **investigação**, e não um teste: o teste que fica é o que usa a trava, e ele precisa passar sempre."},
  {"h2": "2. Contar, em vez de olhar"},
  { code: `adopt Arcane.Concurrent as C

// Um contador atômico não perde, e por isso serve de RÉGUA: ele diz
// quantas vezes o trecho rodou de verdade.
feitas := C.contador(0)
estado := {"n": 0}

action trabalho():
    cycle i from 1 to 500:
        feitas.somar(1)
        estado["n"] := estado["n"] + 1

parallel:
    trabalho()
    trabalho()

out $"rodou {feitas.valor()} vezes, e o estado marcou {estado['n']}"
assert feitas.valor() is 1000`, lang: 'df' },
  {"p": "A régua é o que transforma \"acho que perdeu atualização\" em \"rodou mil vezes e o estado marcou 987\" — e a segunda frase aponta para a linha."},
  {"h2": "3. Repetir muitas vezes, e olhar a distribuição"},
  { code: `adopt Arcane.Concurrent as C

action rodada():
    estado := {"n": 0}
    action somar():
        cycle i from 1 to 300:
            estado["n"] := estado["n"] + 1
    parallel:
        somar()
        somar()
    yield estado["n"]

resultados := [rodada() cycle i in range(0, 5)]
distintos := len(set(resultados))
out $"5 rodadas, {distintos} resultado(s) distinto(s): {sorted(resultados)}"

// Um resultado que MUDA entre rodadas idênticas é a assinatura de
// uma corrida — e um que não muda não prova ausência.
assert distintos >= 1`, lang: 'df' },
  {"h2": "4. O depurador, com a ressalva"},
  {"table": {"head": ["Ferramenta", "Serve para", "Não serve para"], "rows": [["`dataforge debug`", "ver o estado de **uma** thread parada", "reproduzir a corrida — ele a serializa"], ["vigia (`w saldo`)", "descobrir **quem** mudou o valor", "o mesmo: a parada muda o tempo"], ["`C.contador`", "contar sem perder", "dizer onde"], ["um `out` com id da thread", "ver a **ordem** que aconteceu", "casos raros: o `out` tem trava por dentro"]]}},
  { code: `adopt Arcane.Concurrent as C

// O id da thread no registro é o que deixa reconstruir a ordem.
linhas := []
action trabalho(nome):
    cycle i from 1 to 3:
        linhas.append($"{nome}:{i}")

parallel:
    trabalho("a")
    trabalho("b")

assert len(linhas) is 6
out linhas`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A correção não é 'pôr um sleep'", "texto": "Um `sleep` que faz o defeito sumir **não corrigiu nada** — ele mudou a probabilidade. O defeito volta numa máquina mais rápida, com mais carga, ou num dia em que o disco está lento. A correção é uma trava, um atômico, uma transação, ou um desenho em que o estado tem um dono só."}},
  {"h2": "Onde procurar primeiro"},
  {"list": ["**`v[\"n\"] := v[\"n\"] + 1`** em qualquer lugar alcançado por duas threads — é o caso nº 1, e o `check` avisa.", "**Uma rota do Kiln** que escreve em estado de fora: a concorrência ali é invisível.", "**`remove`, `pop`, `insert`, `sort`** — eles leem para decidir o que escrever.", "**Duas travas em ordens diferentes** — não é perda de atualização, é impasse, e o sintoma é um travamento.", "**Um recurso compartilhado sem dono claro** — se você não consegue dizer quem é o dono, provavelmente não há um."]},
];

const headings = [{ id: '1-aumentar-a-janela-de-proposito', text: "1. Aumentar a janela, de propósito", level: 2 as const }, { id: '2-contar-em-vez-de-olhar', text: "2. Contar, em vez de olhar", level: 2 as const }, { id: '3-repetir-muitas-vezes-e-olhar-a-distribuicao', text: "3. Repetir muitas vezes, e olhar a distribuição", level: 2 as const }, { id: '4-o-depurador-com-a-ressalva', text: "4. O depurador, com a ressalva", level: 2 as const }, { id: 'onde-procurar-primeiro', text: "Onde procurar primeiro", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Depurar uma corrida"}
      description={"O defeito que some quando você olha — e as quatro técnicas que funcionam mesmo assim."}
      href={"/docs/concorrencia/depurar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
