// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_interno.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "HIR — a árvore sem açúcar",
  description: "O que é açúcar de escrita na linguagem, o que só parece, e a prova de que abrir um não muda o resultado.",
};

const blocos: Bloco[] = [
  {"p": "A árvore que o parser entrega tem cento e quarenta formas de nó. Parte delas é **conveniência de escrita**: `orif` é um `given` deitado, `soma += 1` é `soma := soma + 1`. Cada forma é um caso a mais em todo analisador que percorre a árvore — e é assim que uma análise fica certa num caminho e errada no outro sem ninguém ver."},
  {"p": "O HIR é a mesma árvore com menos formas. Cinco açúcares são abertos:"},
  {"table": {"head": ["Nome", "O que abre"], "rows": [["`orif-aninhado`", "a corrente de `orif` vira `given`/`otherwise` aninhado"], ["`composta-simples`", "`x += 1` vira `x := x + 1` — **só** quando o alvo é um nome"], ["`pertence-negado`", "`x not in xs` vira `not (x in xs)`"], ["`perform-para-persist`", "`perform … persist c` vira a primeira volta mais o laço"], ["`sinal-de-literal`", "`-5`, hoje um `UnaryOp` sobre `5`, vira o literal `-5`"]]}},
  { code: `adopt Arcane.Compilador as K

fonte := "soma := 0\\ncycle i in [1, 2, 3]:\\n    soma += i\\nout -3 not in [1, 2]\\n"

assert K.acucares(fonte) is {"composta-simples": 1, "pertence-negado": 1,
                             "sinal-de-literal": 1}

// e no HIR o 'orif' deixou de existir: virou um 'given' dentro do 'otherwise'
com_orif := "given a:\\n    out 1\\norif b:\\n    out 2\\n"
de_fora := K.hir(com_orif)["corpo"][0]

assert de_fora["tipo"] is "GivenBlock"
assert de_fora["otherwise_body"][0]["tipo"] is "GivenBlock"
assert len(de_fora["orif_blocks"]) is 0`, lang: 'df' },
  {"h2": "A prova não é a forma da árvore: é a saída"},
  {"p": "Um desaçucaramento errado **não levanta erro** — ele muda o resultado. Por isso a garantia é medida do único jeito que vale: exercícios do repositório rodam nas duas formas, e a saída é comparada caractere por caractere."},
  { code: `n := 0
perform:
    n += 1
persist n smaller 4
assert n is 4`, lang: 'df', title: `O perform, e o que ele vira` },
  { code: `m := yes                    // a marca garante a primeira volta
n := 0
persist m or n smaller 4:   // 'or' curto-circuita: na 1a volta 'n' nao e lido
    m := no
    n += 1
assert n is 4`, lang: 'df', title: `O HIR equivalente, escrito à mão` },
  {"callout": {"tipo": "nota", "titulo": "Por que a marca, e não duplicar o corpo", "texto": "`corpo; persist c: corpo` parece mais simples e está **errado**: um `halt` na primeira cópia não estaria dentro de laço nenhum e escaparia do laço inteiro. A marca mantém o corpo dentro do `persist`, e `halt`, `skip` e `yield` continuam valendo."}},
  {"h2": "O que só PARECE açúcar"},
  {"p": "Esta lista vale mais que a de cima: é o que impede alguém de \"simplificar\" a árvore e mudar a linguagem sem notar. Cada entrada tem o motivo ao lado, e há teste cobrando o motivo."},
  {"table": {"head": ["Forma", "Por que não é açúcar"], "rows": [["`cycle i from 0 to 3`", "`range` **materializa** a lista: um laço de um milhão de voltas viraria uma lista de um milhão de itens, e o laço de contador existe justamente para não pagar isso"], ["`a given c otherwise b`", "o ternário é **expressão** e o `given` é **instrução**; trocar um pelo outro exigiria uma temporária, que muda o escopo"], ["`a ?? b`", "a forma com ternário avaliaria `a` **duas vezes**, e o lado esquerdo de um `??` costuma ser uma chamada"], ["`x?.y`", "o mesmo: `f()?.campo` chamaria `f` duas vezes"], ["`$\"{x:.2f}\"`", "o formato depois dos dois-pontos **não existe** como operador na linguagem"], ["`[e cycle x in xs]`", "compreensão é expressão com escopo próprio; virar laço exigiria instrução, e o valor teria de sair por uma variável"], ["`mark @f`", "`g := f(g)` seria **errado**: um decorador que devolve `void` não substitui o alvo, e é isso que deixa `@Rota(\"/x\")` só anotar"], ["`xs >> morph …`", "os estágios são preguiçosos e os verbos de quadro pedem o **quadro**, não a lista"]]}},
  {"h2": "Resolução de nomes"},
  {"p": "A outra metade do HIR: de onde vem cada nome que um corpo menciona — parâmetro, local, livre (vem de fora) ou embutido."},
  { code: `adopt Arcane.Compilador as K

fonte := "fora := 10\\naction somar(a, b):\\n    local := a + b\\n    yield local + fora + sqrt(4)\\n"

somar := [c cycle c in K.resolucao(fonte) given c["nome"] is "somar"][0]
assert somar["parametros"] is ["a", "b"]
assert somar["locais"] is ["local"]
assert somar["livres"] is ["fora"]
assert somar["embutidos"] is ["sqrt"]`, lang: 'df' },
  {"p": "Um nome **livre** é o que a ação lê e não cria. É a mesma pergunta que a [travessia de processo](/docs/concorrencia/mapa) faz para saber o que levar para outro núcleo, e a que o aviso de [escrita concorrente](/docs/tecnicas/analise-estatica) faz para saber o que uma `thread` alcança."},
];

const headings = [{ id: 'a-prova-nao-e-a-forma-da-arvore-e-a-saida', text: "A prova não é a forma da árvore: é a saída", level: 2 as const }, { id: 'o-que-so-parece-acucar', text: "O que só PARECE açúcar", level: 2 as const }, { id: 'resolucao-de-nomes', text: "Resolução de nomes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"HIR — a árvore sem açúcar"}
      description={"O que é açúcar de escrita na linguagem, o que só parece, e a prova de que abrir um não muda o resultado."}
      href={"/docs/compilador/hir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
