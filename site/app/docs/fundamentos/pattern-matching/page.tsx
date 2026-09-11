import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pattern matching",
  description: "match estrutural: literais, tipos, sequências, records, vaults, enums, alternativas e guardas.",
};

const blocos: Bloco[] = [
  {"h2": "A ideia"},
  {"p": "O `match` do DataForge compara **estruturas**, não só valores. Um único bloco identifica o formato do dado e extrai suas partes:"},
  { code: `action descrever(v):
    match v:
        point 0:
            yield "zero"
        point 1 or 2 or 3:
            yield "pequeno"
        point Integer as n when n bigger 100:
            yield $"grande: {n}"
        point Integer:
            yield "inteiro"
        point String as s:
            yield $"texto de {len(s)} letras"
        point [a, b]:
            yield $"par ({a}, {b})"
        point [primeiro, ...resto]:
            yield $"lista de {len(resto) + 1}"
        point Ponto(x, y):
            yield $"ponto ({x}, {y})"
        point {"tipo": t}:
            yield $"vault do tipo {t}"
        point Status.Ativo:
            yield "ligado"
        point _:
            yield "outro"` },
  {"h2": "A convenção que organiza tudo"},
  {"table": {"head": ["Escrita", "Significa"], "rows": [["`point n` (minúscula)", "**captura** — casa com tudo, liga a `n`"], ["`point Integer` (Maiúscula)", "**tipo** — casa se for daquele tipo"], ["`point Status.Ativo`", "**valor** — casa por igualdade"], ["`point _`", "**curinga** — casa com tudo, sem ligar nome"], ["`point [a, b]`", "**sequência**, por comprimento"], ["`point {\"k\": v}`", "**mapa**, parcial"], ["`point P(x, y)`", "record por posição"], ["`point P(nome := n)`", "record por nome"], ["`point A or B`", "alternativa"], ["`point p as tudo`", "apelido para o valor inteiro"]]}},
  {"p": "Minúscula captura, maiúscula testa o tipo. Sem essa convenção, `point Integer` seria ambíguo: comparar com uma variável chamada `Integer` ou testar o tipo?"},
  {"h2": "Padrões de tipo"},
  { code: `point Integer as n:
    yield $"inteiro {n}"` },
  {"p": "Faz duas coisas de uma vez: **testa** que o valor é um Integer e **liga** `n` já com aquele tipo garantido. É o *type narrowing* do TypeScript, aqui como sintaxe de primeira classe."},
  {"p": "Aceita todos os tipos das anotações, mais o nome de qualquer record, blueprint ou enum. `Number` casa com `Integer` **ou** `Float`; `Any` casa com tudo."},
  {"h2": "Padrões de sequência"},
  { code: `point []:                    # exatamente vazia
point [unico]:               # exatamente um item
point [a, b]:                # exatamente dois
point [primeiro, ...resto]:  # um ou mais
point ["mover", direcao, n]: # literal + capturas` },
  {"callout": {"tipo": "nota", "texto": "Um `Vault` é iterável, mas **não** casa com `[…]` — ele casa com `{…}`. Sem essa separação, `point [a, b]` capturaria dicionários de duas chaves por acidente."}},
  {"h3": "Cabeça e cauda: o padrão recursivo"},
  { code: `action somar(lista):
    match lista:
        point []:
            yield 0
        point [cabeca, ...cauda]:
            yield cabeca + somar(cauda)` },
  {"p": "Dois casos e a função está completa. É como se escreve sobre listas em Haskell, Elixir e Erlang. Para listas grandes, prefira `>> distill` — a recursão consome pilha."},
  {"h2": "Padrões de mapa e record"},
  { code: `point {"metodo": "GET", "rota": r}:
    yield $"lendo {r}"

point Usuario(nome := n, idade := i) when i smaller 18:
    yield $"{n} é menor"` },
  {"p": "O casamento de mapa é **parcial**: o vault precisa ter as chaves citadas, mas pode ter outras. Essa é a escolha certa para dados de fora — um JSON de API sempre traz campos que você não usa."},
  {"h2": "Guardas com when"},
  { code: `action faixa(n):
    match n:
        point Integer as v when v smaller 0:
            yield "negativo"
        point 0:
            yield "zero"
        point Integer as v when v smaller_eq 9:
            yield "unidade"
        point Integer:
            yield "grande"` },
  {"p": "Se a guarda falha, o `match` **continua** para o próximo `point`. Por isso o encadeamento acima funciona sem repetir o teste de tipo."},
  {"h3": "A guarda enxerga o que o padrão ligou"},
  { code: `point Pedido(itens := i, total := t) when len(i) is 0 and t bigger 0:
    yield "inconsistente: total sem itens"` },
  {"p": "O padrão extrai; a guarda relaciona. Você acabou de expressar uma **regra de negócio** como um único caso do `match`."},
  {"h2": "Por que when e não given"},
  {"p": "`given` já é o ternário (`a given c otherwise b`). Usar a mesma palavra numa guarda criaria ambiguidade real no parser: em `point n given x`, ele não saberia se `given` abre uma guarda ou um ternário. `when` resolve isso."},
  {"h2": "Três regras que evitam surpresa"},
  {"list": ["Os `point` são testados **de cima para baixo**; o primeiro que casa vence.", "Ordene do **específico ao geral** — uma captura no topo torna tudo abaixo inalcançável.", "Mantenha um `default`: a exaustividade ainda não é verificada."]},
  { code: `match n:
    point x:              # captura tudo
        yield "pegou tudo"
    point 5:              # INALCANÇÁVEL
        yield "nunca chega aqui"` },
];

const headings = [{ id: 'a-ideia', text: "A ideia", level: 2 as const }, { id: 'a-convencao-que-organiza-tudo', text: "A convenção que organiza tudo", level: 2 as const }, { id: 'padroes-de-tipo', text: "Padrões de tipo", level: 2 as const }, { id: 'padroes-de-sequencia', text: "Padrões de sequência", level: 2 as const }, { id: 'cabeca-e-cauda-o-padrao-recursivo', text: "Cabeça e cauda: o padrão recursivo", level: 3 as const }, { id: 'padroes-de-mapa-e-record', text: "Padrões de mapa e record", level: 2 as const }, { id: 'guardas-com-when', text: "Guardas com when", level: 2 as const }, { id: 'a-guarda-enxerga-o-que-o-padrao-ligou', text: "A guarda enxerga o que o padrão ligou", level: 3 as const }, { id: 'por-que-when-e-nao-given', text: "Por que when e não given", level: 2 as const }, { id: 'tres-regras-que-evitam-surpresa', text: "Três regras que evitam surpresa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pattern matching"}
      description={"match estrutural: literais, tipos, sequências, records, vaults, enums, alternativas e guardas."}
      href={"/docs/fundamentos/pattern-matching"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
