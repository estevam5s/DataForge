// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/metaprogramacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "DSLs",
  description: "Combinadores de análise para escrever uma linguagem pequena: gramática própria, falha com posição e o resultado como Resultado.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem já tem duas formas de DSL **interna**: palavra contextual no parser (as onze do Kiln, os seis verbos do Quadro) e objeto com operadores. As duas exigem mexer no DataForge ou desenhar uma API."},
  {"p": "O que faltava era a DSL **externa**: ler um texto que segue uma gramática sua — uma regra de preço, um filtro de busca, um formato de configuração — sem trazer dependência nem escrever um analisador à mão com índice e `persist`."},
  {"h2": "Uma gramática em quatro linhas"},
  { code: `adopt Arcane.Dsl as D

numero := D.mapear(D.numero(), lambda t => cast t as Integer)
soma := D.mapear(D.seq([numero, D.texto("+"), numero]),
                 lambda partes => partes[0] + partes[2])

r := D.analisar(soma, "2+3")
assert r.deu_certo() and r.valor() is 5`, lang: 'df' },
  {"p": "O resultado é um [`Resultado`](/docs/tipos/resultado), e não uma exceção: texto de fora falha o tempo todo, e obrigar `monitor` em volta de cada análise faria o caminho normal ser o do erro."},
  {"h2": "A falha diz onde"},
  { code: `adopt Arcane.Dsl as D

r := D.analisar(D.numero(), "abc")

assert r.falhou()
assert r.erro()["posicao"] is 0
assert "numero" in r.erro()["esperado"]`, lang: 'df' },
  {"p": "\"Não deu certo\" não ajuda ninguém a consertar a linha 3 de um arquivo de configuração. A falha traz posição, o que era esperado e o trecho em volta."},
  {"h2": "Os combinadores"},
  {"table": {"head": ["Grupo", "Símbolos"], "rows": [["básicos", "`texto`, `numero`, `nome`, `entre_aspas`, `espaco`, `simbolo`, `qualquer_de`, `ate`"], ["combinar", "`seq`, `ou`, `muitos`, `opcional`, `separado_por`"], ["transformar", "`mapear`, `exigir` (troca a mensagem de falha)"], ["recursão", "`adiado(lambda => regra)`, `gramatica(regras, inicial)`"], ["rodar", "`analisar(regra, texto)` → `Resultado`"]]}},
  { code: `adopt Arcane.Dsl as D

palavra := D.ou([D.texto("sim"), D.texto("nao")])
lista := D.muitos(D.seq([palavra, D.opcional(D.texto(","))]))

r := D.analisar(lista, "sim,nao,sim")
assert r.deu_certo() and len(r.valor()) is 3`, lang: 'df' },
  {"h2": "Uma calculadora inteira"},
  { code: `adopt Arcane.Dsl as D

numero := D.mapear(D.numero(), lambda t => cast t as Float)
operador := D.ou([D.texto("+"), D.texto("-"), D.texto("*")])

action aplicar(partes):
    esquerda := partes[0]
    cycle par in partes[1]:
        given par[0] is "+":
            esquerda := esquerda + par[1]
        orif par[0] is "-":
            esquerda := esquerda - par[1]
        otherwise:
            esquerda := esquerda * par[1]
    yield esquerda

expressao := D.mapear(D.seq([numero, D.muitos(D.seq([operador, numero]))]),
                      aplicar)

assert D.analisar(expressao, "2+3*4").valor() is 20.0
assert D.analisar(expressao, "10-4").valor() is 6.0`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O espaço é explícito", "texto": "Um combinador que pulasse espaço sozinho decidiria por quem escreve a gramática — e em formato de largura fixa é exatamente o que não se quer. `D.espaco()` e `D.simbolo(x)` existem para quem quer o comportamento comum."}},
  {"h2": "Qual DSL usar"},
  {"table": {"head": ["Quando", "A forma"], "rows": [["a linguagem é o DataForge, com vocabulário próprio", "blueprint com operadores, pipeline (`>>`) e ação de alta ordem"], ["o texto vem de fora e tem gramática sua", "`Arcane.Dsl` — esta página"], ["você quer palavra nova **na linguagem**", "palavra contextual no parser (é como o Kiln e o Quadro fazem) — e isso é mexer no DataForge"], ["gerar código a partir de dado", "[`Arcane.Macro`](/docs/metaprogramacao/macros)"]]}},
];

const headings = [{ id: 'uma-gramatica-em-quatro-linhas', text: "Uma gramática em quatro linhas", level: 2 as const }, { id: 'a-falha-diz-onde', text: "A falha diz onde", level: 2 as const }, { id: 'os-combinadores', text: "Os combinadores", level: 2 as const }, { id: 'uma-calculadora-inteira', text: "Uma calculadora inteira", level: 2 as const }, { id: 'qual-dsl-usar', text: "Qual DSL usar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"DSLs"}
      description={"Combinadores de análise para escrever uma linguagem pequena: gramática própria, falha com posição e o resultado como Resultado."}
      href={"/docs/metaprogramacao/dsl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
