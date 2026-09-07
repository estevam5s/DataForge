import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "16 · Módulos e projetos",
  description: "6 exercícios: `adopt`/`relay`, camadas, `forge.toml` e testes.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 16`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["151", "**Modulos com adopt e relay**", "importe um modulo local e comprove que relay controla o que sai."], ["152", "**Imports seletivos e apelidos**", "traga so os simbolos que voce usa, com o nome que preferir."], ["153", "**Organizando um projeto**", "estruture codigo em modulos com responsabilidades separadas."], ["154", "**Manifesto e ferramentas**", "conheca o forge.toml e os comandos de projeto."], ["155", "**Testes automatizados**", "escreva testes que o dataforge test descobre e executa."], ["156", "**Projeto: biblioteca completa**", "escreva um modulo publicavel com interface, testes e documentacao."]]}},
  {"h2": "151 · Modulos com adopt e relay"},
  {"p": "Importe um modulo local e comprove que relay controla o que sai."},
  { code: `// Exercicio 151 — Modulos com adopt e relay
// Enunciado: importe um modulo local e comprove que relay controla o que sai.

// Importa o modulo inteiro sob um nome
adopt geometria as geo

out geo.PI
out $"circulo de raio 2: {round(geo.area_circulo(2), 4)}"
out $"retangulo 3x4: {geo.area_retangulo(3, 4)}"

assert round(geo.area_circulo(1), 5) is 3.14159, "area do circulo"
assert geo.area_retangulo(3, 4) is 12, "area do retangulo"

// O que nao esta no relay nao atravessa
escondido := no
monitor:
    out geo._arredondar(1.23456)
handle e:
    escondido := yes
    out $"bloqueado: {e.message}"

assert escondido is yes, "_arredondar nao foi exportado"

// Modulo inexistente dispara ImportError, nao devolve vazio
falhou := no
monitor:
    adopt Arcane.NaoExiste as x
    out x
handle e:
    falhou := yes
    out $"erro: {e.type}"

assert falhou is yes, "modulo inexistente dispara"

// A stdlib se importa do mesmo jeito
adopt Arcane.Math as Math
out $"sqrt(144) = {Math.sqrt(144)}"
assert Math.sqrt(144) is 12.0, "stdlib"
`, title: `151_adopt_e_relay.df` },
  {"h2": "152 · Imports seletivos e apelidos"},
  {"p": "Traga so os simbolos que voce usa, com o nome que preferir."},
  { code: `// Exercicio 152 — Imports seletivos e apelidos
// Enunciado: traga so os simbolos que voce usa, com o nome que preferir.

// Forma compacta: Modulo.{nomes}
adopt geometria.{area_circulo, PI}

out $"PI = {PI}"
out $"area = {round(area_circulo(1), 4)}"
assert round(area_circulo(1), 4) is 3.1416, "usado sem prefixo"

// Forma explicita, com apelido
adopt {realcar as destacar, linha} from textos

out destacar("titulo")
out linha("=", 24)
assert destacar("x") is "[x]", "apelido funciona"
assert linha("*", 3) is "***", "importado direto"

// Tambem vale para a stdlib
adopt Arcane.Math.{sqrt, factorial}
out $"sqrt(81) = {sqrt(81)}  5! = {factorial(5)}"
assert sqrt(81) is 9.0, "sqrt sem prefixo"
assert factorial(5) is 120, "factorial sem prefixo"

// Pedir um simbolo que o modulo nao exporta e erro claro
erro := ""
monitor:
    adopt geometria.{nao_existe}
handle e:
    erro := e.message
    out $"erro: {erro}"

assert "does not export" in erro, "a mensagem explica"
assert "area_circulo" in erro, "e lista o que existe"

// O modulo inteiro e o seletivo convivem
adopt geometria as geo
assert geo.PI is PI, "mesmo valor pelos dois caminhos"
out "os dois estilos coexistem"
`, title: `152_imports_seletivos.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/16-modulos-e-projetos/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '151--modulos-com-adopt-e-relay', text: "151 · Modulos com adopt e relay", level: 2 as const }, { id: '152--imports-seletivos-e-apelidos', text: "152 · Imports seletivos e apelidos", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"16 · Módulos e projetos"}
      description={"6 exercícios: `adopt`/`relay`, camadas, `forge.toml` e testes."}
      href={"/docs/exercicios/16-modulos-e-projetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
