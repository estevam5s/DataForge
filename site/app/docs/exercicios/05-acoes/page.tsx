import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "05 · Ações",
  description: "14 exercícios: aridade, recursão, closures, lambdas, decoradores e `defer`.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 05`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["049", "**Acao basica**", "escreva uma acao que soma e outra sem retorno."], ["050", "**Parametros com valor padrao**", "permita chamar a acao com menos argumentos."], ["051", "**Argumentos nomeados**", "passe argumentos fora de ordem usando o nome."], ["052", "**Verificacao de aridade**", "comprove que argumentos faltando ou sobrando disparam erro."], ["053", "**Acoes tipadas**", "anote parametros e retorno e comprove a checagem."], ["054", "**Recursao**", "fatorial, fibonacci e soma de digitos."], ["055", "**Limite de recursao**", "comprove que recursao infinita vira erro controlado."], ["056", "**Acoes de alta ordem**", "passe acoes como argumento e devolva acoes."], ["057", "**Closures**", "crie um contador que preserva estado entre chamadas."], ["058", "**Lambdas**", "use acoes anonimas em variaveis e como argumento."], ["059", "**Decoradores com mark**", "envolva uma acao com log sem alterar seu corpo."], ["060", "**defer**", "agende limpeza que roda ao sair da acao."], ["061", "**Escopo e shadow**", "entenda quando uma acao le e quando cria uma variavel."], ["062", "**Memoizacao manual**", "acelere fibonacci guardando resultados ja calculados."]]}},
  {"h2": "049 · Acao basica"},
  {"p": "Escreva uma acao que soma e outra sem retorno."},
  { code: `// Exercicio 049 — Acao basica
// Enunciado: escreva uma acao que soma e outra sem retorno.

action somar(a, b):
    yield a + b

action saudar(nome):
    out "Ola,", nome

out somar(2, 3)
saudar("Ana")

assert somar(2, 3) is 5, "soma"
assert saudar("Ana") is void, "acao sem yield devolve void"
`, title: `049_acao_basica.df` },
  {"h2": "050 · Parametros com valor padrao"},
  {"p": "Permita chamar a acao com menos argumentos."},
  { code: `// Exercicio 050 — Parametros com valor padrao
// Enunciado: permita chamar a acao com menos argumentos.

action criar_usuario(nome, papel := "leitor", ativo := yes):
    yield {"nome": nome, "papel": papel, "ativo": ativo}

out criar_usuario("Ana")
out criar_usuario("Bruno", "admin")

assert criar_usuario("Ana")["papel"] is "leitor", "padrao aplicado"
assert criar_usuario("Bruno", "admin")["papel"] is "admin", "padrao sobrescrito"
assert criar_usuario("Carla", "editor", no)["ativo"] is no, "terceiro argumento"
`, title: `050_parametros_padrao.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 12 exercícios deste módulo estão em `exercicios/05-acoes/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '049--acao-basica', text: "049 · Acao basica", level: 2 as const }, { id: '050--parametros-com-valor-padrao', text: "050 · Parametros com valor padrao", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"05 · Ações"}
      description={"14 exercícios: aridade, recursão, closures, lambdas, decoradores e `defer`."}
      href={"/docs/exercicios/05-acoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
