import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "11 · Tipos e checagem",
  description: "6 exercícios: anotações, ações tipadas, `typeof`, `cast` e `dataforge check`.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 11`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["121", "**Anotacoes de tipo**", "declare variaveis com tipo e comprove que o valor errado e recusado."], ["122", "**Acoes com tipos**", "anote parametros e retorno, e veja o erro apontar o parametro exato."], ["123", "**typeof e conversao**", "descubra o tipo de qualquer valor e converta entre tipos com seguranca."], ["124", "**Analise estatica**", "escreva erros de proposito e confirme que o dataforge check os encontra."], ["125", "**Tipos dentro de colecoes**", "combine anotacoes com listas e dicionarios, e valide o conteudo."], ["126", "**Tipagem gradual com Any**", "use Any quando o tipo depende do uso, e estreite depois com typeof."]]}},
  {"h2": "121 · Anotacoes de tipo"},
  {"p": "Declare variaveis com tipo e comprove que o valor errado e recusado."},
  { code: `// Exercicio 121 — Anotacoes de tipo
// Enunciado: declare variaveis com tipo e comprove que o valor errado e recusado.

// Tipos simples
idade: Integer := 30
nome: String := "Ana"
altura: Float := 1.72
ativo: Boolean := yes
notas: Cluster := [8, 9, 10]
config: Vault := {"tema": "escuro"}

out idade, nome, altura, ativo
out notas, config

// Integer serve onde se espera Float — a conversao e segura
media: Float := 8

// O contrario nao vale
recusou := no
monitor:
    quantidade: Integer := 3.5
handle e:
    recusou := yes
    out "recusado:", e.message

assert recusou is yes, "Float nao entra onde se espera Integer"
assert media is 8, "Integer entra onde se espera Float"
assert typeof(idade) is "Integer", "tipo de idade"
assert typeof(config) is "Vault", "tipo de config"
`, title: `121_anotacoes_basicas.df` },
  {"h2": "122 · Acoes com tipos"},
  {"p": "Anote parametros e retorno, e veja o erro apontar o parametro exato."},
  { code: `// Exercicio 122 — Acoes com tipos
// Enunciado: anote parametros e retorno, e veja o erro apontar o parametro exato.

action area_retangulo(largura: Number, altura: Number) -> Float:
    yield largura * altura * 1.0

action saudar(nome: String, vezes: Integer := 1) -> String:
    yield (nome + " ").repeat(vezes).trim()

action primeiro_item(itens: Cluster) -> Any:
    given len(itens) is 0:
        yield void
    yield itens[0]

out area_retangulo(3, 4)
out saudar("oi", 3)
out primeiro_item([10, 20]), primeiro_item([])

// O erro nomeia o parametro
erro := ""
monitor:
    area_retangulo("tres", 4)
handle e:
    erro := e.message
    out erro

assert area_retangulo(3, 4) is 12.0, "area"
assert saudar("oi", 2) is "oi oi", "repeticao"
assert primeiro_item([]) is void, "lista vazia devolve void"
assert "largura" in erro, "a mensagem nomeia o parametro errado"
`, title: `122_acoes_tipadas.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/11-tipos-e-checagem/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '121--anotacoes-de-tipo', text: "121 · Anotacoes de tipo", level: 2 as const }, { id: '122--acoes-com-tipos', text: "122 · Acoes com tipos", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"11 · Tipos e checagem"}
      description={"6 exercícios: anotações, ações tipadas, `typeof`, `cast` e `dataforge check`."}
      href={"/docs/exercicios/11-tipos-e-checagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
