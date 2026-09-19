// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O ecossistema, conferido",
  description: "O inventário da implementação com uma marca por componente — e uma conferência nas duas direções, para que o mapa não possa mentir.",
};

const blocos: Bloco[] = [
  {"p": "A referência fecha com um desenho do ecossistema: `dfc` com onze fases, `dfup`, `dfpm`, um runtime de seis peças, sete ferramentas e oito alvos."},
  {"p": "Um desenho desses é o texto mais fácil de escrever num projeto — e o mais fácil de deixar envelhecer. Ele não roda, ninguém o executa, e no dia em que uma peça muda de nome o mapa passa a mentir **sem nada denunciar**."},
  {"callout": {"tipo": "nota", "titulo": "Este repositório já pagou por isso", "texto": "A tabela da biblioteca padrão esteve escrita em **três lugares**, e os três divergiram. Uma contagem de símbolos voltou a ficar errada depois de corrigida, porque alguém editou o `.tsx` gerado em vez da fonte. Um mapa do ecossistema escrito à mão seria a quarta cópia."}},
  {"h2": "As três marcas"},
  {"p": "Cada componente do desenho carrega **um de três estados**, e o terceiro é o que dá valor ao mapa:"},
  {"table": {"head": ["Marca", "Estado", "Quer dizer"], "rows": [["`[+]`", "`existe`", "a peça está aqui, com esse papel"], ["`[~]`", "`equivale`", "não há essa peça; há **outra** que responde a mesma pergunta por outro mecanismo — nomeada, com o porquê"], ["`[-]`", "`nao-existe`", "não há, e o motivo está escrito"]]}},
  {"p": "A lista é fechada de propósito. Um quarto estado seria o lugar onde \"mais ou menos\" se esconderia — e é exatamente o que se quer não ter num inventário."},
  { code: `dataforge ecossistema              # o inventario inteiro
dataforge ecossistema --ausencias  # so o que nao existe, e o motivo
dataforge ecossistema --json       # para o CI ler`, lang: 'bash' },
  {"h2": "A conferência nas duas direções"},
  {"p": "O que impede o mapa de envelhecer não é cuidado de quem escreve: é `conferir()`, e ele cobra **duas** coisas."},
  {"table": {"head": ["Direção", "O que cobra", "O que impede"], "rows": [["`faltando`", "todo caminho citado no mapa existe no disco", "a peça foi renomeada e o mapa continua apontando para o nome antigo"], ["`orfaos`", "todo módulo de `dataforge/` aparece em algum componente", "um módulo novo nasce **fora** do mapa, e o inventário fica incompleto em silêncio"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A segunda é a que importa, e foi ela que pegou o primeiro erro", "texto": "A primeira versão deste mapa citava `dataforge/stdlib/arcane_concurrent.py` em dois componentes. O arquivo se chama `arcane_paralelo.py` — a classe é que se chama `ArcaneConcurrent`. `conferir()` acusou os dois antes de qualquer teste existir. Sem ele, o mapa teria nascido mentindo em dois pontos."}},
  { code: `adopt Arcane.Ecossistema as Eco

n := Eco.numeros()
assert n["componentes"] bigger 30
assert n["nao_existem"] bigger 0

c := Eco.conferir()
assert c["ok"] is yes
assert len(c["faltando"]) is 0
assert len(c["orfaos"]) is 0
out $"{n['componentes']} componentes, {c['citados']} caminhos conferidos"`, lang: 'df' },
  {"p": "O comando **sai com 1** quando o mapa e o disco discordam. É o que faz um CI reprovar um inventário que passou a mentir — a mesma escolha do `dataforge abi`, que sai com 2 quando o contrato quebra."},
  {"h2": "Os grupos, e o que há em cada um"},
  {"p": "O `dfc` do desenho não é um binário separado aqui: o driver é o próprio `dataforge`, e **cada fase tem um comando que a mostra** — `tokens`, `ast`, `ir`, `percurso`."},
  {"table": {"head": ["Grupo", "O que existe", "O que não"], "rows": [["`dfc`", "lexer, parser, AST, HIR, verificador de tipos, MIR, dataflow, SSA, LIR", "backend LLVM e gerador de código de máquina"], ["`dfup`", "os instaladores, e `dataforge version`", "**gerenciador de versões**: não há como manter duas lado a lado nem fixar por projeto"], ["`dfpm`", "resolver com semver, `forge.lock`, integridade, empacotar, publicar", "workspace com várias peças resolvidas de uma vez"], ["Runtime", "escalonador, laço de eventos, async, threads, processos, erros", "alocador próprio e runtime bare-metal"], ["Tooling", "LSP, **depurador**, formatador, linter, testes, bench, profiler, doc", "— (o depurador é a peça que o desenho do documento não lista)"], ["Interop", "FFI para C, ponte para o Python, `Arcane.Abi`", "— (o layout binário não existe, e o **problema** dele existe)"], ["Alvos", "Linux, macOS, Windows, ARM, ARM64", "bare-metal; e WASM só na direção \"rodar em\""]]}},
  {"p": "As peças que **faltam no desenho** também estão no mapa, e a mais importante é o `Execution Engine`: o desenho supõe compilação antecipada, e por isso não tem onde pôr o interpretador. Aqui ele é o centro."},
  {"h2": "Os números saem do mesmo lugar que os publica"},
  {"p": "`numeros()` não tem um único valor escrito à mão. A contagem de símbolos usa o **mesmo levantamento** que gera a página da biblioteca."},
  {"callout": {"tipo": "perigo", "titulo": "Uma soma própria já divergiu em 112 símbolos", "texto": "Uma contagem ingênua sobre `DESCRICOES` discordou de `gerar_pagina_biblioteca.py`, que é o gerador canônico — e o número errado foi publicado no site. Duas fontes para o mesmo número é uma fonte a mais do que se pode manter."}},
  { code: `adopt Arcane.Ecossistema as Eco

n := Eco.numeros()
// tudo derivado: nada aqui e escrito a mao
assert n["modulos"] bigger 60
assert n["simbolos"] bigger 1800
assert n["comandos"] bigger 40
assert n["existem"] + n["equivalem"] + n["nao_existem"] is n["componentes"]
out $"{n['modulos']} modulos, {n['simbolos']} simbolos, {n['comandos']} comandos"`, lang: 'df' },
];

const headings = [{ id: 'as-tres-marcas', text: "As três marcas", level: 2 as const }, { id: 'a-conferencia-nas-duas-direcoes', text: "A conferência nas duas direções", level: 2 as const }, { id: 'os-grupos-e-o-que-ha-em-cada-um', text: "Os grupos, e o que há em cada um", level: 2 as const }, { id: 'os-numeros-saem-do-mesmo-lugar-que-os-publica', text: "Os números saem do mesmo lugar que os publica", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O ecossistema, conferido"}
      description={"O inventário da implementação com uma marca por componente — e uma conferência nas duas direções, para que o mapa não possa mentir."}
      href={"/docs/ecossistema/componentes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
