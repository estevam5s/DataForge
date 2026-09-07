import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "12 · Records e enums",
  description: "6 exercícios: imutabilidade, `with`, métodos e enums com valores.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 12`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["127", "**Records**", "declare um record, construa instancias e comprove a igualdade estrutural."], ["128", "**Imutabilidade e with**", "comprove que um record nao muda, e crie copias alteradas com with."], ["129", "**Records com metodos**", "adicione comportamento a um record sem abrir mao da imutabilidade."], ["130", "**Enums**", "declare um conjunto fechado de valores e use seus membros com seguranca."], ["131", "**Enums com valores**", "associe dados a cada membro e converta de ida e volta."], ["132", "**Enums com match**", "use pattern matching para tratar cada membro e garantir cobertura."]]}},
  {"h2": "127 · Records"},
  {"p": "Declare um record, construa instancias e comprove a igualdade estrutural."},
  { code: `// Exercicio 127 — Records
// Enunciado: declare um record, construa instancias e comprove a igualdade estrutural.

record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"

// Construcao posicional e nomeada
a := Usuario("Ana", 30)
b := Usuario(nome := "Bruno", idade := 25, email := "b@x.com")

out a
out b
out a.nome, a.idade, a.email

// Igualdade e estrutural: mesmos campos, mesmo valor
out Usuario("Ana", 30) is Usuario("Ana", 30)
out Usuario("Ana", 30) is Usuario("Ana", 31)

assert a.email is "sem@email", "campo com valor padrao"
assert Usuario("Ana", 30) is Usuario("Ana", 30), "igualdade estrutural"
assert Usuario("Ana", 30) isnt Usuario("Ana", 31), "campos diferentes"
assert typeof(a) is "Usuario", "typeof devolve o nome do record"

// Campo obrigatorio ausente
faltou := no
monitor:
    Usuario("Carla")
handle e:
    faltou := yes
    out "erro:", e.message
assert faltou is yes, "idade e obrigatoria"

// Tipo errado no campo
tipo_errado := no
monitor:
    Usuario(42, 30)
handle e:
    tipo_errado := yes
    out "erro:", e.message
assert tipo_errado is yes, "nome precisa ser String"
`, title: `127_record_basico.df` },
  {"h2": "128 · Imutabilidade e with"},
  {"p": "Comprove que um record nao muda, e crie copias alteradas com with."},
  { code: `// Exercicio 128 — Imutabilidade e with
// Enunciado: comprove que um record nao muda, e crie copias alteradas com with.

record Conta:
    titular: String
    saldo: Number

original := Conta("Ana", 1000)

// Tentar mudar um campo e erro
bloqueou := no
monitor:
    original.saldo := 2000
handle e:
    bloqueou := yes
    out e.message

assert bloqueou is yes, "record e imutavel"
assert original.saldo is 1000, "o valor original nao mudou"

// 'with' produz uma copia com os campos trocados
depositado := original with {"saldo": original.saldo + 500}
out original
out depositado

assert original.saldo is 1000, "o original continua intacto"
assert depositado.saldo is 1500, "a copia tem o novo valor"
assert depositado.titular is "Ana", "os demais campos vieram junto"

// Encadear transformacoes lendo de cima para baixo
action depositar(conta, valor):
    yield conta with {"saldo": conta.saldo + valor}

action sacar(conta, valor):
    guard valor smaller_eq conta.saldo, "saldo insuficiente"
    yield conta with {"saldo": conta.saldo - valor}

final := sacar(depositar(depositar(original, 200), 300), 100)
out final
assert final.saldo is 1400, "1000 +200 +300 -100"
assert original.saldo is 1000, "nada disso tocou no original"

// Campo inexistente no with
erro := no
monitor:
    original with {"limite": 5000}
handle e:
    erro := yes
    out e.message
assert erro is yes, "with recusa campo que nao existe"
`, title: `128_record_imutavel.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/12-records-e-enums/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '127--records', text: "127 · Records", level: 2 as const }, { id: '128--imutabilidade-e-with', text: "128 · Imutabilidade e with", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"12 · Records e enums"}
      description={"6 exercícios: imutabilidade, `with`, métodos e enums com valores."}
      href={"/exercicios/12-records-e-enums"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
