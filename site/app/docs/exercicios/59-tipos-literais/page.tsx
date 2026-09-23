// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "59 · Tipos literais",
  description: "2 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 59`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[398](#398-tipos-literais-o-valor-que-vira-tipo)", "**Tipos literais: o valor que vira tipo**", "declare um 'type' cujos valores sao literais e veja onde"], ["[399](#399-o-metodo-que-nao-existe-acusado-antes-de-rodar)", "**O metodo que nao existe, acusado antes de rodar**", "rode o proprio 'check' sobre arquivos que voce escreve e"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "398 · Tipos literais: o valor que vira tipo"},
  {"p": "**Enunciado.** declare um 'type' cujos valores sao literais e veja onde"},
  { code: `// ele e cobrado — o 'check' prova com o literal na mao, a fronteira
// cobra o resto, e 'yes' nao se confunde com 1.

type Estado := "ativo" | "inativo" | "suspenso"
type Nivel  := 1 | 2 | 3
type Ligado := yes

out "== 1. a fronteira confere =="

action mudar(e: Estado) -> String:
    yield e

assert mudar("ativo") is "ativo"
assert mudar("suspenso") is "suspenso"
out "   'ativo' e 'suspenso' passam"

out ""
out "== 2. o que nao esta na lista e recusado =="

recusados := 0
monitor:
    mudar("excluido")
handle Error as e:
    recusados := recusados + 1

monitor:
    mudar("")
handle Error as e:
    recusados := recusados + 1

assert recusados is 2
out $"   {recusados} valores de fora da lista recusados"

out ""
out "== 3. numero e booleano tambem sao literais =="

action nivel(n: Nivel) -> Integer:
    yield n * 10

assert nivel(1) is 10
assert nivel(3) is 30

l: Ligado := yes
assert l is yes
out "   Nivel 1|2|3 e Ligado yes"

out ""
out "== 4. 'yes' e '1' NAO se confundem =="

// Em Python 'True == 1'. Sem conferir o TIPO, um 'type Ligado := yes'
// aceitaria o numero 1 calado — um valor que ninguem escreveu passando
// por um tipo que existe justamente para nao deixar.
action ligar(v: Ligado) -> Boolean:
    yield v

pegou := no
monitor:
    ligar(1)
handle Error as e:
    pegou := yes
assert pegou
out "   o numero 1 nao passa por um tipo 'yes'"

out ""
out "== 5. a base de uma uniao de literais e conhecida =="

// 'e' e um String para o analisador — e e isso que permite concatenar
// e declarar '-> String'. Sem essa leitura, a forma mais natural de
// usar o recurso seria acusada de devolver o que nao declarou.
action rotulo(e: Estado) -> String:
    yield e + "!"

assert rotulo("ativo") is "ativo!"
out "   String + String, dentro de um tipo literal"

out ""
out "== 6. uma uniao MISTA nao tem base unica =="

// '"auto" | Integer' aceita os dois, e o analisador cala em vez de
// escolher uma base: escolher faria ele aprovar o que a execucao
// recusa.
type Modo := "auto" | Integer

action usar(m: Modo) -> String:
    yield str(m)

assert usar("auto") is "auto"
assert usar(3) is "3"
out "   'auto' e 3, os dois legitimos"

out ""
out "ok — 398"`, lang: 'df', title: `exercicios/59-tipos-literais/398_tipo_literal.df` },
  {"h3": "O que ele resolve"},
  {"p": "Uma lista fechada de valores é a coisa mais comum que existe num programa: o estado de um pedido, o método HTTP, o nível de um log. Antes do tipo literal ela era escrita assim:"},
  { code: `action mudar(e):
    given e is not "ativo" and e is not "inativo":
        trigger $"estado invalido: {e}"
    ...`, lang: 'df' },
  {"p": "Em toda fronteira. E esquecida numa delas — que é onde o dado errado entra."},
  {"h3": "A forma"},
  { code: `type Estado := "ativo" | "inativo" | "suspenso"`, lang: 'df' },
  {"p": "Texto, inteiro, decimal e booleano podem ser literais. `void` fica de fora de propósito: `Void` já é o tipo dele, e `type T := void` seria uma segunda forma de dizer a mesma coisa."},
  {"h3": "Onde ele é cobrado"},
  {"table": {"head": ["Momento", "O que acontece"], "rows": [["`dataforge check`, com o **literal** na mão", "acusa, e lista os valores que valem"], ["`dataforge check`, com uma variável", "**cala** — não há o que provar"], ["execução, em toda fronteira", "recusa, nomeando o tipo e o que chegou"]]}},
  {"p": "O silêncio do meio é o recurso. Um `String` que veio de `input()` não prova nada, e acusá-lo recusaria justamente o código para o qual o tipo existe: ler a entrada e passá-la adiante, deixando a fronteira decidir."},
  {"h3": "Duas armadilhas"},
  {"p": "**`yes` e `1` não se confundem.** Em Python `True == 1` é verdadeiro. Sem conferir o *tipo* junto com a igualdade, um `type Ligado := yes` aceitaria o número 1 calado."},
  {"p": "**As aspas fazem parte do tipo.** Sem elas, `type T := \"Integer\"` e `type T := Integer` virariam a mesma string — e o primeiro, que só aceita a palavra `\"Integer\"`, passaria a aceitar qualquer número."},
  {"h3": "Quando usar `enum` em vez disto"},
  {"p": "Quando o valor é um conceito do domínio com nome próprio, quando você quer método, `.name`, `.value`, ou exaustividade no `match`. O tipo literal é para quando o valor **é** o dado — vem de um JSON, de uma coluna, de um `?estado=`."},
  {"h2": "399 · O metodo que nao existe, acusado antes de rodar"},
  {"p": "**Enunciado.** rode o proprio 'check' sobre arquivos que voce escreve e"},
  { code: `// veja o que ele acusa num texto e num cluster — e onde ele CALA, que
// e a metade que custa mais.

adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Process as Proc

pasta := $"{OS.temp_dir()}/df-399-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)

action conferir(codigo):
    caminho := $"{pasta}/prova.df"
    IO.write(caminho, codigo)
    r := Proc.run(["dataforge", "check", caminho])
    yield r["stdout"] + r["stderr"]

out "== 1. o que existe continua funcionando =="

nome := "ana"
assert nome.upper() is "ANA"
assert nome.length() is 3

xs := [1, 2, 3]
xs.append(4)
assert len(xs) is 4
out "   upper, length e append: normais"

out ""
out "== 2. o erro de digitacao vira erro do analisador =="

saida := conferir("""nome := "ana"
out nome.uppper()
""")
assert "uppper" in saida
assert "upper" in saida
out "   'uppper' acusado, com 'upper' na sugestao"

saida := conferir("""xs := [1, 2, 3]
out xs.apend(4)
""")
assert "apend" in saida
assert "append" in saida
out "   'apend' acusado, com 'append' na sugestao"

out ""
out "== 3. e a forma SEM chamar tambem =="

// Ler o metodo sem chamar e legitimo ('f := xs.append'), entao o erro
// aqui e o mesmo: o nome nao existe naquele tipo.
saida := conferir("""nome := "ana"
f := nome.uppper
out f
""")
assert "uppper" in saida
out "   'f := nome.uppper' tambem"

out ""
out "== 4. onde ele CALA, e por que =="

// Um Vault fica de FORA: 'v.cidade' cai na CHAVE quando ela existe, e
// acusar exigiria saber as chaves — que um vault montado em execucao
// nao tem.
saida := conferir("""v := {"cidade": "Floripa"}
v["uf"] := "SC"
out v.uf
""")
assert "sem erros" in saida
out "   vault: o membro pode ser uma chave, entao ele cala"

// E 'length' nao mora na tabela — ele e tratado a parte no
// interpretador. Sem essa linha, a forma que a propria doc ensina
// viraria um falso alarme.
saida := conferir("""nome := "ana"
out nome.length()
""")
assert "sem erros" in saida
out "   'length' continua valendo"

// Um nome comecando com '_' e combinado entre quem escreveu, nao um
// engano.
saida := conferir("""nome := "ana"
out nome._interno
""")
assert "sem erros" in saida
out "   nome com '_' na frente: combinado, nao engano"

out ""
out "ok — 399"`, lang: 'df', title: `exercicios/59-tipos-literais/399_metodo_embutido.df` },
  {"h3": "A medida que motivou isto"},
  {"p": "Quinze erros que **falham em execução**, conferidos contra o que o `dataforge check` pegava antes de rodar. Ele pegava oito. Dos sete silêncios, quatro eram o mesmo caso em tipos diferentes:"},
  { code: `nome := "ana"
out nome.naoExiste()      // passava limpo, e estourava em execução`, lang: 'df' },
  {"p": "O mesmo erro num `record` era acusado desde sempre, **com sugestão**. A forma mais comum de erro de digitação que existe numa linguagem era a que escapava."},
  {"h3": "A lista vem do interpretador"},
  {"p": "As tabelas de método de texto e de cluster moram em `dataforge/interpreter.py`, e o analisador as **lê de lá**. Uma segunda lista divergiria no primeiro método novo — e a divergência não daria erro: ela faria o analisador acusar um método que *funciona*, que é o falso alarme que ensina a desligar a verificação inteira."},
  {"h3": "Onde ele cala"},
  {"table": {"head": ["Cala sobre", "Porque"], "rows": [["um **Vault**", "`v.cidade` cai na chave quando ela existe"], ["um objeto de `adopt Python.x`", "ali o membro é resolvido pelo Python"], ["um nome começando com `_`", "é combinado, não um engano"], ["um tipo que ele não inferiu", "a regra de sempre: sem prova, silêncio"]]}},
  {"h3": "A calibragem"},
  {"p": "Zero falso alarme nas cinco pastas do repositório — `examples`, `exercicios`, `projetos`, `packages` e `trilha`, 532 arquivos. Um analisador que acusa código que funciona é desligado no mesmo dia, e junto com ele vão os achados de verdade."},
  {"h3": "`length` é chamado"},
  {"p": "`nome.length` devolve a *ação*, não o número: ele está na tabela de métodos como qualquer outro. A forma é `nome.length()`."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/59-tipos-literais/398_tipo_literal.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '398-tipos-literais-o-valor-que-vira-tipo', text: "398 · Tipos literais: o valor que vira tipo", level: 2 as const }, { id: 'o-que-ele-resolve', text: "O que ele resolve", level: 3 as const }, { id: 'a-forma', text: "A forma", level: 3 as const }, { id: 'onde-ele-e-cobrado', text: "Onde ele é cobrado", level: 3 as const }, { id: 'duas-armadilhas', text: "Duas armadilhas", level: 3 as const }, { id: 'quando-usar-enum-em-vez-disto', text: "Quando usar `enum` em vez disto", level: 3 as const }, { id: '399-o-metodo-que-nao-existe-acusado-antes-de-rodar', text: "399 · O metodo que nao existe, acusado antes de rodar", level: 2 as const }, { id: 'a-medida-que-motivou-isto', text: "A medida que motivou isto", level: 3 as const }, { id: 'a-lista-vem-do-interpretador', text: "A lista vem do interpretador", level: 3 as const }, { id: 'onde-ele-cala', text: "Onde ele cala", level: 3 as const }, { id: 'a-calibragem', text: "A calibragem", level: 3 as const }, { id: 'length-e-chamado', text: "`length` é chamado", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"59 · Tipos literais"}
      description={"2 exercícios: ."}
      href={"/docs/exercicios/59-tipos-literais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
