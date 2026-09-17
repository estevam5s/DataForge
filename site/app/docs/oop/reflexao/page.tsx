// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Reflexão",
  description: "Arcane.Reflexo: descobrir campos, métodos, modificadores, herança e anotações; invocar por nome; criar tipos em execução; desenhar o diagrama de classes.",
};

const blocos: Bloco[] = [
  {"p": "Reflexão é o programa olhando para os próprios tipos. `Arcane.Reflexo` responde o que a declaração diz — e passa pelas **mesmas regras** que o código comum: um `private` continua private quando o nome chega por texto."},
  { code: `adopt Arcane.Reflexo as R

contract Identificavel:
    get id() -> Integer

abstract blueprint Pessoa with Identificavel:
    readonly id := 0
    nome: String := ""
    abstract action papel()

blueprint Aluno extends Pessoa:
    mark @Coluna("matricula")
    matricula := ""
    override action papel():
        yield "aluno"

assert R.especie(Identificavel) is "contract"
assert R.mro(Aluno)[1] is Pessoa
assert Aluno in R.herdeiros(Pessoa)
assert R.contratos(Aluno) is ["Identificavel"]
assert "readonly" in R.modificadores(Aluno, "id")
assert R.anotacoes(Aluno, "matricula")[0]["args"] is ["matricula"]

nomes := [m["nome"] cycle m in R.metodos(Aluno)]
assert "papel" in nomes

a := spawn Aluno()
assert R.invocar(a, "papel") is "aluno"
R.escrever(a, "nome", "Ana")
assert R.ler(a, "nome") is "Ana"
assert R.cumpre(a, Identificavel)`, lang: 'df' },
  {"h2": "A API"},
  {"table": {"head": ["Grupo", "Funções"], "rows": [["tipos", "`tipo`, `nome`, `especie`, `molde`"], ["membros", "`campos`, `metodos`, `propriedades`, `operadores`, `estaticos`, `membros`, `modificadores`, `anotacoes`, `documentacao`, `sugerir`"], ["herança", "`maes`, `mro`, `herdeiros`, `descendentes`, `traits`, `contratos`, `descende`, `e_instancia`, `meta`, `meta_instancia`"], ["registro", "`blueprints`, `procurar`"], ["dinâmico", "`instanciar`, `tem`, `ler`, `escrever`, `invocar`, `cumpre`, `faltando`, `definir_metodo`, `criar_blueprint`"], ["inspeção", "`inspecionar`, `diagrama`, `hierarquia`"]]}},
  {"h2": "Tipos criados em execução"},
  {"p": "`criar_blueprint` monta um tipo a partir de um vault, pelas regras de uma declaração escrita: mãe `final` recusa, contrato não cumprido recusa. Um método é um lambda que recebe o objeto como primeiro argumento."},
  { code: `adopt Arcane.Reflexo as R

Ponto := R.criar_blueprint("Ponto", {
    "campos": {"x": 0, "y": 0},
    "metodos": {"norma": lambda p => sqrt(p.x ** 2 + p.y ** 2)},
})

p := R.instanciar(Ponto)
p.x := 3
p.y := 4
assert p.norma() is 5.0
assert R.procurar("Ponto") is Ponto`, lang: 'df' },
  {"h2": "Diagrama de classes"},
  { code: `adopt Arcane.Reflexo as R

abstract blueprint Forma:
    abstract action area()
blueprint Circulo(raio: Float) extends Forma:
    action area():
        yield 3.14 * self.raio ** 2

texto := R.diagrama(Forma)
assert "Forma <|-- Circulo" in texto
out texto`, lang: 'df' },
  {"p": "A saída é Mermaid, que o GitHub e a maioria dos editores de Markdown desenham. O mesmo diagrama sai sem rodar nada com `dataforge oop src/ --diagrama`."},
  {"callout": {"tipo": "perigo", "titulo": "Reflexão tem custo", "texto": "Cada chamada por texto passa pela busca completa de membro, de visibilidade e de ganchos — o caminho rápido do interpretador não se aplica. Use para framework, serialização e ferramenta; no laço quente, chame o método."}},
];

const headings = [{ id: 'a-api', text: "A API", level: 2 as const }, { id: 'tipos-criados-em-execucao', text: "Tipos criados em execução", level: 2 as const }, { id: 'diagrama-de-classes', text: "Diagrama de classes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Reflexão"}
      description={"Arcane.Reflexo: descobrir campos, métodos, modificadores, herança e anotações; invocar por nome; criar tipos em execução; desenhar o diagrama de classes."}
      href={"/docs/oop/reflexao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
