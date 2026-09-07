import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "14 · Pattern matching",
  description: "6 exercícios: literais, tipos, sequências, records, vaults e guardas.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 14`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["139", "**Padroes basicos**", "case por literal, capture com um nome e use o curinga."], ["140", "**Padroes de tipo**", "case pelo tipo do valor e ligue o resultado ja tipado."], ["141", "**Padroes de sequencia**", "desmonte listas por posicao, com cabeca, cauda e tamanho fixo."], ["142", "**Padroes de record e vault**", "extraia campos direto no padrao, por posicao ou por nome."], ["143", "**Guardas e ligacao com as**", "combine condicoes e apelidos para casos precisos."], ["144", "**Projeto: validador de dados**", "junte padroes de tipo, sequencia e vault num validador de esquema."]]}},
  {"h2": "139 · Padroes basicos"},
  {"p": "Case por literal, capture com um nome e use o curinga."},
  { code: `// Exercicio 139 — Padroes basicos
// Enunciado: case por literal, capture com um nome e use o curinga.

action classificar(v):
    match v:
        point 0:
            yield "zero"
        point 1 or 2 or 3:
            yield "pequeno"
        point "sim" or "yes":
            yield "afirmativo"
        point void:
            yield "vazio"
        point n:
            yield $"outro: {n}"

cycle v in [0, 2, "sim", void, 99]:
    out classificar(v)

assert classificar(0) is "zero", "literal"
assert classificar(3) is "pequeno", "alternativa com or"
assert classificar("yes") is "afirmativo", "texto"
assert classificar(void) is "vazio", "void"
assert classificar(99) is "outro: 99", "captura"

// O curinga _ casa com tudo e nao liga nome
action tem_valor(v):
    match v:
        point void:
            yield no
        point _:
            yield yes

assert tem_valor(void) is no, "void"
assert tem_valor(0) is yes, "zero e um valor"
assert tem_valor("") is yes, "texto vazio e um valor"

// A ordem importa: o primeiro que casa vence
action ordem(n):
    match n:
        point x:
            yield "pegou tudo"
        point 5:
            yield "nunca chega aqui"

assert ordem(5) is "pegou tudo", "captura antes de literal engole tudo"
out "cuidado: uma captura no topo torna os demais inalcancaveis"
`, title: `139_padroes_basicos.df` },
  {"h2": "140 · Padroes de tipo"},
  {"p": "Case pelo tipo do valor e ligue o resultado ja tipado."},
  { code: `// Exercicio 140 — Padroes de tipo
// Enunciado: case pelo tipo do valor e ligue o resultado ja tipado.

record Ponto:
    x: Integer
    y: Integer

action descrever(v):
    match v:
        point Integer as n when n smaller 0:
            yield $"inteiro negativo ({n})"
        point Integer as n:
            yield $"inteiro {n}"
        point Float as d:
            yield $"decimal {d}"
        point String as s:
            yield $"texto de {len(s)} letras"
        point Boolean:
            yield "booleano"
        point Cluster as c:
            yield $"lista com {len(c)} itens"
        point Vault:
            yield "dicionario"
        point Ponto as p:
            yield $"ponto ({p.x}, {p.y})"
        point Void:
            yield "nada"
        default:
            yield "tipo desconhecido"

valores := [7, -3, 2.5, "abc", yes, [1, 2], {"a": 1}, Ponto(3, 4), void]
cycle v in valores:
    out descrever(v)

assert descrever(7) is "inteiro 7", "Integer"
assert descrever(-3) is "inteiro negativo (-3)", "guarda antes do geral"
assert descrever(2.5) is "decimal 2.5", "Float"
assert descrever(Ponto(3, 4)) is "ponto (3, 4)", "record por tipo"
assert descrever(void) is "nada", "Void"

// Number aceita Integer e Float
action e_numero(v):
    match v:
        point Number:
            yield yes
        default:
            yield no

assert e_numero(1) is yes, "Integer e Number"
assert e_numero(1.5) is yes, "Float e Number"
assert e_numero("1") is no, "texto nao e Number"

// Any casa com tudo, inclusive void
action sempre(v):
    match v:
        point Any:
            yield "casou"
assert sempre(void) is "casou", "Any casa ate com void"
`, title: `140_padroes_de_tipo.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/14-pattern-matching/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '139--padroes-basicos', text: "139 · Padroes basicos", level: 2 as const }, { id: '140--padroes-de-tipo', text: "140 · Padroes de tipo", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"14 · Pattern matching"}
      description={"6 exercícios: literais, tipos, sequências, records, vaults e guardas."}
      href={"/docs/exercicios/14-pattern-matching"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
