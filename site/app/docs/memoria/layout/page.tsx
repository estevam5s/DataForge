// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/memoria_posse.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Memória e layout",
  description: "O que dá para medir: bytes por objeto, slots contra dicionário, o coletor, referências fracas e o que é assunto de linguagem compilada.",
};

const blocos: Bloco[] = [
  {"p": "Alinhamento, padding, ABI e cache line são assunto de uma linguagem com **layout fixo**. Aqui o objeto é do interpretador, e a pergunta que muda o desenho de um programa é outra: **quanto custa um objeto**, e o que fazer a respeito."},
  {"h2": "slots: a diferença medida"},
  {"p": "Sem `slots`, cada objeto carrega um dicionário próprio. Com `slots`, os campos viram uma lista indexada — medido neste repositório: **64% menos memória por objeto**."},
  { code: `adopt Arcane.Memoria as Mem

blueprint Compacta:
    slots x, y
    x := 1
    y := 2

blueprint Solta:
    x := 1
    y := 2

com := Mem.layout(Compacta)
sem := Mem.layout(Solta)

assert com["slots"] and not sem["slots"]
assert com["campos"] is ["x", "y"]
assert com["bytes"] smaller sem["bytes"]

comparacao := Mem.comparar_layout(Compacta, Solta)
assert comparacao["menor"] is "Compacta"
assert comparacao["economia_percentual"] bigger 20`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "O número sai de objetos de verdade", "texto": "`Mem.layout` cria objetos e os mede, em vez de calcular sobre o código: um palpite sobre memória é sempre otimista. Quando o blueprint precisa de argumentos para nascer, ele diz isso em vez de inventar um número."}},
  {"h2": "Quanto ocupa um valor"},
  { code: `adopt Arcane.Memoria as Mem

pequeno := Mem.tamanho([1, 2])
grande := Mem.tamanho([1, 2, "um texto bem maior para ocupar espaco"])

assert grande bigger pequeno
assert Mem.tamanho("x") bigger 0`, lang: 'df' },
  {"p": "A conta soma o objeto **e tudo que só ele alcança**, com guarda de ciclo — é a pergunta que interessa antes de guardar um milhão de linhas na memória."},
  {"h2": "O coletor, e o que ele não promete"},
  { code: `adopt Arcane.Memoria as Mem

blueprint Conexao:
    nome := ""

c := spawn Conexao()
assert Mem.vivos(Conexao) is 1

c := void
assert Mem.vivos(Conexao) is 0

estat := Mem.estatisticas()
assert estat["ativo"]
assert len(estat["geracoes"]) is 3`, lang: 'df' },
  {"p": "O coletor libera **quando quiser**. Para o recurso que precisa fechar numa hora certa, a resposta é [`Arcane.Posse`](/docs/memoria/posse) — `soltar()` e `P.com(…)` rodam o finalizador naquele instante."},
  {"h2": "Referência fraca: observar sem segurar"},
  { code: `adopt Arcane.Memoria as Mem

blueprint Sessao:
    id := 0

s := spawn Sessao()
fraca := Mem.fraca(s)
cache := Mem.mapa_fraco()
cache.definir(s, "dados caros")

assert fraca.viva() and cache.tamanho is 1

s := void
assert not fraca.viva()
assert cache.tamanho is 0          // o cache não segurou nada`, lang: 'df' },
  {"h2": "O que é assunto de linguagem compilada"},
  {"table": {"head": ["Item", "Aqui"], "rows": [["stack frames", "existem como **quadros de chamada**: o stack trace os mostra, e o teto é de mil (a recursão de cauda não tem teto)"], ["heap allocation", "toda alocação é do Python; não há escolha entre pilha e heap"], ["object layout, struct layout, enum layout", "o que existe é `slots` contra dicionário, e isso é **medível** (acima)"], ["alignment, padding, cache lines", "não se aplicam: não há layout fixo para alinhar"], ["ABI, representação de ponteiro", "não se aplicam: não há binário nem endereço exposto"], ["endianness", "existe onde importa — em `Arcane.Bytes.empacotar`/`desempacotar`, na fronteira do arquivo e da rede"], ["nullability", "é `void`, com `??` e `?.`; e uma união `String | Void` diz isso no tipo"], ["zero-sized types", "não existem: todo valor ocupa alguma coisa"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Quando o custo de memória é o problema de verdade", "texto": "Antes de reprojetar, meça: `Mem.layout` para o objeto, `Mem.tamanho` para o dado, e `dataforge profile` para o tempo. Depois disso, as três saídas que funcionam aqui são `slots` no blueprint, `stream action` para não materializar a coleção inteira, e a travessia de processo quando o trabalho é de CPU."}},
];

const headings = [{ id: 'slots-a-diferenca-medida', text: "slots: a diferença medida", level: 2 as const }, { id: 'quanto-ocupa-um-valor', text: "Quanto ocupa um valor", level: 2 as const }, { id: 'o-coletor-e-o-que-ele-nao-promete', text: "O coletor, e o que ele não promete", level: 2 as const }, { id: 'referencia-fraca-observar-sem-segurar', text: "Referência fraca: observar sem segurar", level: 2 as const }, { id: 'o-que-e-assunto-de-linguagem-compilada', text: "O que é assunto de linguagem compilada", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Memória e layout"}
      description={"O que dá para medir: bytes por objeto, slots contra dicionário, o coletor, referências fracas e o que é assunto de linguagem compilada."}
      href={"/docs/memoria/layout"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
