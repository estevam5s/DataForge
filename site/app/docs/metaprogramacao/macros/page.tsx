// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/metaprogramacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Macros: a árvore como dado",
  description: "Ler o corpo de uma ação, percorrer, transformar, gerar código e derivar métodos — com higiene explícita.",
};

const blocos: Bloco[] = [
  {"p": "Um **decorador** troca o valor: recebe a ação pronta e devolve outra coisa. O que ele não alcança é o **corpo** — e metade da metaprogramação que vale a pena é sobre o corpo: instrumentar cada instrução, derivar um método a partir dos campos, gerar uma ação a partir de um esquema."},
  {"h2": "A árvore é um vault"},
  { code: `adopt Arcane.Macro as M

action somar(a, b):
    yield a + b

arvore := M.arvore(somar)

assert arvore["tipo"] is "ActionDeclaration"
assert arvore["parametros"] is ["a", "b"]
assert arvore["corpo"][0]["tipo"] is "YieldStatement" `, lang: 'df' },
  {"p": "Ela é um dado comum: percorre com `cycle`, casa com `match`, serializa em JSON e atravessa processo — sem que nada disso precise conhecer a classe do nó. É o mesmo raciocínio do `Quadro` e da ponte para o Python."},
  {"h2": "citar: texto vira árvore"},
  { code: `adopt Arcane.Macro as M

arvore := M.citar("x * 2 + 1")
assert arvore["tipo"] is "BinaryOp"
assert M.texto(arvore) is "x * 2 + 1" `, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "'texto' é aproximado, e o nome não esconde", "texto": "A fonte original não é guardada: o texto é reconstruído da árvore para ler, comparar e depurar — não para ser byte a byte igual ao que foi escrito."}},
  {"h2": "Reescrever o corpo"},
  { code: `adopt Arcane.Macro as M

action dobro(x):
    yield x * 2

action trocar(nodo):
    given nodo["tipo"] is "BinaryOp" and nodo["op"] is "*":
        yield M.citar("x + x")
    yield nodo

trocada := M.reescrever(dobro, trocar)

assert dobro(5) is 10
assert trocada(5) is 10        // o corpo é outro, o resultado é o mesmo`, lang: 'df' },
  {"p": "A árvore original **não** é tocada: `transformar` devolve uma nova. Uma macro que mutasse o que recebeu mudaria a ação de quem chamou."},
  {"h2": "Gerar código"},
  { code: `adopt Arcane.Macro as M

corpo := M.citar("a * 10")
gerada := M.acao("dez_vezes", ["a"], corpo)

assert gerada(4) is 40
assert M.arvore(gerada)["nome"] is "dez_vezes"

// e o atalho, num passo só
pronta := M.compilar("a + b", "soma", ["a", "b"])
assert pronta(2, 3) is 5`, lang: 'df' },
  {"h2": "Higiene: não capturar o nome de quem chamou"},
  {"p": "A macro que gera um temporário chamado `temp` quebra o código de quem já tinha um `temp`. `nome_fresco` e `renomear` existem para isso, e são **explícitos**: fazer higiene sozinho exigiria saber o que é \"de dentro\", e essa decisão é de quem escreve a macro."},
  { code: `adopt Arcane.Macro as M

corpo := M.citar("temporario + 1")
limpo := M.renomear(corpo, "temporario", M.nome_fresco("temporario"))

assert M.texto(limpo) isnt M.texto(corpo)
assert "__temporario_" in M.texto(limpo)`, lang: 'df' },
  {"h2": "Macro de atributo: derivar"},
  {"p": "Em vez de escrever `__str__` e `__eq__` à mão em cada blueprint, os **campos que já existem** geram os dois:"},
  { code: `adopt Arcane.Macro as M

mark @M.derivar("texto", "igualdade")
blueprint Ponto:
    x := 1
    y := 2

a := spawn Ponto()
b := spawn Ponto()

assert $"{a}" is "Ponto(x=1, y=2)"
assert a is b`, lang: 'df' },
  {"table": {"head": ["Derivável", "Gera"], "rows": [["`texto`", "`__str__` com os campos, no formato `Nome(campo=valor, …)`"], ["`igualdade`", "`__eq__` comparando todos os campos"], ["`ordem`", "`__lt__` pelo primeiro campo"], ["`vault`", "`para_vault()` com os campos"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A macro roda na CARGA", "texto": "O decorador é aplicado uma vez, quando a declaração é lida — e não a cada chamada. Reescrever o corpo por chamada seria pagar a metaprogramação em tempo de execução, para sempre."}},
  {"h2": "A superfície"},
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`M.arvore(acao)`", "a árvore da ação (ou do blueprint) como dado"], ["`M.citar(texto)`", "texto vira árvore"], ["`M.texto(arvore)`", "árvore vira texto (aproximado)"], ["`M.percorrer(arvore, visitante)`", "chama o visitante em cada nó"], ["`M.transformar(arvore, acao)`", "árvore nova, com cada nó passado pela ação"], ["`M.substituir` · `M.renomear`", "troca por tipo de nó, ou nome de identificador"], ["`M.nome_fresco(base)`", "um nome que o código de fora não tem"], ["`M.acao(nome, params, corpo)` · `M.compilar(texto, …)`", "gera a ação"], ["`M.reescrever(acao, transformador)`", "ação nova, corpo transformado"], ["`M.derivar(…)`", "a macro de atributo"]]}},
];

const headings = [{ id: 'a-arvore-e-um-vault', text: "A árvore é um vault", level: 2 as const }, { id: 'citar-texto-vira-arvore', text: "citar: texto vira árvore", level: 2 as const }, { id: 'reescrever-o-corpo', text: "Reescrever o corpo", level: 2 as const }, { id: 'gerar-codigo', text: "Gerar código", level: 2 as const }, { id: 'higiene-nao-capturar-o-nome-de-quem-chamou', text: "Higiene: não capturar o nome de quem chamou", level: 2 as const }, { id: 'macro-de-atributo-derivar', text: "Macro de atributo: derivar", level: 2 as const }, { id: 'a-superficie', text: "A superfície", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Macros: a árvore como dado"}
      description={"Ler o corpo de uma ação, percorrer, transformar, gerar código e derivar métodos — com higiene explícita."}
      href={"/docs/metaprogramacao/macros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
