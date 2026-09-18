// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/memoria_posse.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Memória determinística: o mapa",
  description: "Item por item da parte 3 da referência Deep Tech — ownership, borrow checker, lifetimes, smart pointers e layout — cruzado com o que o DataForge tem, e o que não tem por decisão.",
};

const blocos: Bloco[] = [
  {"p": "A terceira parte de uma referência Deep Tech descreve o gerenciamento **determinístico** de memória: ownership, borrow checker, lifetimes, smart pointers e layout. Ela foi escrita para uma linguagem compilada com memória manual. O DataForge é interpretado e tem coletor — então a pergunta certa não é \"como copiar Rust\", e sim **o que dessa disciplina continua valendo aqui**."},
  {"callout": {"tipo": "atencao", "titulo": "A diferença que muda tudo", "texto": "Num interpretador com coleta automática, um valor **nunca** vira endereço inválido: não há use-after-free, dangling pointer nem double free de memória. O que sobra — e continua caro — é o **recurso** (arquivo, conexão, cadeado) e o **aliasing** (dois donos escrevendo no mesmo objeto). É exatamente isso que `Arcane.Posse` cobre."}},
  {"h2": "12 · Ownership"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["modelo de ownership, propriedade exclusiva", "`P.dono(valor, ao_soltar)` — **opt-in**: vale para o que você declara", "[Posse](/docs/memoria/posse)"], ["movimentação", "`mover()`: quem move, perde; usar depois é erro, e o `check` acusa antes (`posse-movida`)", "[Posse](/docs/memoria/posse)"], ["cópia e clone", "`copiar()` (mesmo valor) e `clonar()` (cópia) — a distinção é explícita", "[Posse](/docs/memoria/posse)"], ["borrowing, aliasing, mutabilidade", "`usar`/`mudar` no dono e `ler`/`escrever` na célula: muitos leem OU um escreve", "[Posse](/docs/memoria/posse)"], ["destrutores, RAII", "`soltar()` roda o finalizador **agora**; `P.com` e `P.com_escopo` soltam até no erro", "[Escopo](/docs/memoria/escopo)"], ["regras de acesso", "cobradas quando roda; o `check` prova o subconjunto que o fluxo de um arquivo permite", "[Posse](/docs/memoria/posse)"]]}},
  {"h2": "13 · Borrow checker"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["regras de empréstimo, referência compartilhada e mutável", "`ler` (N) XOR `escrever` (1), cobrado em execução — como o `RefCell`", "[Posse](/docs/memoria/posse)"], ["exclusividade de mutabilidade, aliasing seguro", "a célula recusa escrever no meio de uma leitura, com a mensagem dizendo quem está lendo", "[Posse](/docs/memoria/posse)"], ["análise de dataflow", "o `check` segue o fluxo de um arquivo: move, solta, devolve, passa adiante", "[Análise estática](/docs/tecnicas/analise-estatica)"], ["diagnósticos", "`posse-movida` (erro), `recurso-vazado` e `emprestimo-escapa` (avisos)", "[Posse](/docs/memoria/posse)"], ["verificação em tempo de compilação", "**não existe**: não há inferência de região. A garantia é em execução, e a prova estática é o que o literal e o fluxo permitem", "—"], ["NLL (non-lexical lifetimes)", "**não se aplica**, e na prática o efeito é o mesmo: o empréstimo acaba no fim do **corpo** que o recebeu, e não no fim do bloco", "[Posse](/docs/memoria/posse)"]]}},
  {"h2": "14 · Lifetimes"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["tempo de vida de um recurso", "o **escopo**: `P.escopo()` solta tudo na ordem inversa; `defer` faz o mesmo sem objeto novo", "[Escopo](/docs/memoria/escopo)"], ["lifetime de um empréstimo", "o corpo de `usar`/`mudar`/`ler`/`escrever`; pedi-lo fora dele devolve um empréstimo já encerrado", "[Posse](/docs/memoria/posse)"], ["lifetimes explícitos (`'a`), elisão, bounds", "**não existem**: não há região a anotar, porque não há como um valor virar endereço inválido", "—"], ["lifetimes em structs, funções e traits", "**não se aplicam** pelo mesmo motivo; o que existe é a posse do recurso guardado num campo", "—"], ["subtyping, covariância, contravariância, invariância", "**não existem** como declaração: a herança dá subtipagem de valor, e coleção genérica é conferida item a item", "[Generics](/docs/tipos/genericos)"]]}},
  {"h2": "15 · Smart pointers"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["`Box<T>`", "`P.dono(valor)` — posse exclusiva com destrutor", "[Posse](/docs/memoria/posse)"], ["`Rc<T>`", "`P.compartilhado(valor)` — contagem determinística", "[Posse](/docs/memoria/posse)"], ["`Arc<T>`, atomic reference counting", "`P.atomico(valor)` — a mesma coisa, válida entre threads", "[Posse](/docs/memoria/posse)"], ["weak references", "`P.fraco(c)` (responde `Talvez`) e `Mem.fraca(obj)` / `Mem.mapa_fraco()`", "[Layout](/docs/memoria/layout)"], ["ciclos de referência", "acontecem, e são **mostrados**: um ciclo forte não chega a zero; a volta fraca o quebra", "[Posse](/docs/memoria/posse)"], ["referências", "toda variável já é uma: o valor é um objeto, e a atribuição não copia", "[Variáveis](/docs/variaveis)"], ["ponteiros crus, heap, stack", "**não existem**: não há endereço exposto nem escolha de onde o valor mora", "—"]]}},
  {"h2": "16 · Memória e layout"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["stack frames", "quadros de chamada, com teto de mil; `yield f(…)` vira salto e não tem teto", "[Ações](/docs/acoes)"], ["object/struct layout", "`slots` contra dicionário — **medido**: `Mem.layout` e `Mem.comparar_layout`", "[Layout](/docs/memoria/layout)"], ["heap allocation", "toda alocação é do runtime; não há escolha", "—"], ["alignment, padding, cache lines, ABI", "**não se aplicam**: não há layout fixo nem binário", "[Layout](/docs/memoria/layout)"], ["endianness", "existe onde importa: `Arcane.Bytes.empacotar`/`desempacotar`, na fronteira do arquivo e da rede", "[Arcane.Bytes](/docs/biblioteca/bytes)"], ["nullability", "`void`, com `??` e `?.`; e a união `String | Void` diz isso no tipo", "[Tipos nomeados](/docs/tipos-nomeados)"], ["zero-sized types", "**não existem**: todo valor ocupa alguma coisa", "—"], ["enum layout", "um membro de `enum` é um objeto com nome, valor e índice — sem representação binária escolhida", "[Records e enums](/docs/fundamentos/records)"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das cinco seções da parte 3, **três** têm resposta de verdade aqui — ownership, disciplina de empréstimo e smart pointers —, porque elas falam de *protocolo*, e protocolo existe em qualquer linguagem. As outras duas — lifetimes anotados e layout binário — falam de *representação*, e representação é assunto de quem compila."},
  {"p": "O que o DataForge oferece no lugar delas: liberação determinística onde importa (`soltar`, `com`, `escopo`), medida real de custo por objeto (`Mem.layout`), e a travessia de processo quando o problema é CPU e não memória."},
];

const headings = [{ id: '12-ownership', text: "12 · Ownership", level: 2 as const }, { id: '13-borrow-checker', text: "13 · Borrow checker", level: 2 as const }, { id: '14-lifetimes', text: "14 · Lifetimes", level: 2 as const }, { id: '15-smart-pointers', text: "15 · Smart pointers", level: 2 as const }, { id: '16-memoria-e-layout', text: "16 · Memória e layout", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Memória determinística: o mapa"}
      description={"Item por item da parte 3 da referência Deep Tech — ownership, borrow checker, lifetimes, smart pointers e layout — cruzado com o que o DataForge tem, e o que não tem por decisão."}
      href={"/docs/memoria/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
