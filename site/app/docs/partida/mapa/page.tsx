// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_e_seguranca.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Partida e segurança: o mapa",
  description: "Item por item das partes 13 e 15 da referência Deep Tech — bootstrapping, TLS, pilha, globais, modelo de segurança e unsafe.",
};

const blocos: Bloco[] = [
  {"h2": "58 · Antes do `main()` (parte 13)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["runtime initialization", "as sete fases, nomeadas e em ordem", "[A partida](/docs/partida/inicio)"], ["static constructors", "`comptime` — roda na carga, numa caixa sem E/S", "[comptime](/docs/metaprogramacao/comptime)"], ["global variables", "`steady`, e o hoisting das declarações de topo", "[A partida](/docs/partida/inicio)"], ["runtime services", "os `adopt`, **cronometrados** um a um", "[A partida](/docs/partida/inicio)"], ["boot / loader, stack setup, stack probes", "**não se aplica**: quem faz o boot é o CPython", "—"]]}},
  {"h2": "59 · Thread Local Storage (parte 13)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["thread-local variables", "`I.local` / `I.meu`", "[Por thread](/docs/partida/por-thread)"], ["**TLS initialization**", "uma ação que **constrói** o valor, uma vez por thread", "[Por thread](/docs/partida/por-thread)"], ["**TLS destructors**", "`ao_terminar`, quando a thread é coletada", "[Por thread](/docs/partida/por-thread)"], ["runtime thread state", "`_por_thread` no interpretador: pilha e profundidade já eram por thread", "[Pilha](/docs/partida/pilha)"], ["thread-local allocators", "**não se aplica**: quem aloca é o CPython", "—"]]}},
  {"h2": "60 · Stack (parte 13)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["stack frames", "`I.quadros()` — ação, linha e arquivo", "[Pilha](/docs/partida/pilha)"], ["stack overflow detection", "teto de mil quadros, com as duas saídas na mensagem", "[Pilha](/docs/partida/pilha)"], ["coroutine / fiber stacks", "as [fibras](/docs/runtime/fibras) são **sem pilha**", "[Fibras](/docs/runtime/fibras)"], ["stack allocation, probes, guards, growth", "**não se aplica**: a pilha é a do CPython", "—"]]}},
  {"h2": "61 · Variáveis globais (parte 13)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["static/constant initialization", "`steady`, e `comptime` para o que é calculado", "[comptime](/docs/metaprogramacao/comptime)"], ["lazy initialization", "o modificador `lazy` em campo de blueprint", "[Modificadores](/docs/oop/modificadores)"], ["initialization ordering", "a ordem do arquivo; **ciclo é erro do `check`**, com a cadeia inteira na mensagem", "[Carga](/docs/modulos/carga)"], ["destruction", "`defer` de topo roda no fim, na ordem inversa", "[A partida](/docs/partida/inicio)"], ["global constructors (C++)", "**não se aplica**", "—"]]}},
  {"h2": "65 · Modelo de segurança (parte 15)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["memory safety", "**por construção**: não há ponteiro na linguagem, e o coletor responde pela memória. A exceção é [`Arcane.C`](/docs/ffi/c), e ela é declarada", "[FFI](/docs/ffi/c)"], ["type safety", "`dataforge check`, que **atravessa arquivos**", "[Análise](/docs/tecnicas/analise-estatica)"], ["thread safety", "**não automática, e medida**: duas threads escrevendo no mesmo nome perderam 40.425 de 80.000. O `check` avisa (`escrita-concorrente`), e `Arcane.Stm` dá escritas que acontecem juntas", "[STM](/docs/concorrencia/stm)"], ["bounds checking", "em execução sempre, e antes de rodar quando se prova (`indice-fora-do-alcance`)", "[Análises](/docs/compilador/analises)"], ["null safety", "`??`, `?.`, e o `talvez-nao-definida` do fluxo", "[Análises](/docs/compilador/analises)"], ["**integer overflow policies**", "**não há overflow**: o inteiro é de precisão arbitrária. Uma classe inteira de bug não existe aqui — e o preço é a conta ser mais lenta que uma de 64 bits", "[Tipos](/docs/tipos)"], ["resource safety", "[`Arcane.Posse`](/docs/memoria/posse): liberação determinística, e o `check` cobra o recurso não solto", "[Posse](/docs/memoria/posse)"], ["**capability boundaries**", "`Arcane.Capacidade`", "[Capacidade](/docs/seguranca/capacidade)"]]}},
  {"h2": "66 · `unsafe` (parte 15)"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["raw pointers, manual allocation", "`Arcane.C`: `ponteiro`, `alocar`, `liberar`", "[Ponteiros](/docs/ffi/ponteiros)"], ["FFI", "o módulo inteiro **é** a região insegura", "[FFI](/docs/ffi/c)"], ["minimizar regiões `unsafe`", "não há bloco `unsafe` a marcar: **o módulo é a fronteira**, e a documentação diz isso em vez de espalhar uma palavra pelo código", "[FFI](/docs/ffi/mapa)"], ["validar entradas", "a assinatura é **declarada** e a lista de tipos é fechada; o ponteiro nulo é conferido", "[Chamar C](/docs/ffi/c)"], ["encapsular APIs inseguras", "`P.com(P.dono(C.alocar(n), …))` — o bloco sai no fim do escopo, inclusive no caminho de erro", "[Ponteiros](/docs/ffi/ponteiros)"], ["documentar precondições", "`expects` / `promises` / `invariant`, cobrados em execução", "[Contratos](/docs/oop/contratos)"], ["assembly, SIMD, MMIO, kernel", "**não se aplica** — ver [o mapa de hardware](/docs/hardware/mapa)", "—"]]}},
  {"h2": "O resumo honesto"},
  {"p": "A **parte 13 rendeu** o que dependia do runtime da linguagem (fases visíveis, TLS com finalizador, a pilha que se pergunta) e deixou de fora o que é do CPython (boot, stack probes, guards). A **parte 15 já estava quase toda pronta** — segurança de memória é por construção, e a ausência de *overflow* de inteiro elimina uma classe de bug inteira —, e o que faltava era a **fronteira de capacidade**, que agora existe com os limites escritos em voz alta."},
];

const headings = [{ id: '58-antes-do-main-parte-13', text: "58 · Antes do `main()` (parte 13)", level: 2 as const }, { id: '59-thread-local-storage-parte-13', text: "59 · Thread Local Storage (parte 13)", level: 2 as const }, { id: '60-stack-parte-13', text: "60 · Stack (parte 13)", level: 2 as const }, { id: '61-variaveis-globais-parte-13', text: "61 · Variáveis globais (parte 13)", level: 2 as const }, { id: '65-modelo-de-seguranca-parte-15', text: "65 · Modelo de segurança (parte 15)", level: 2 as const }, { id: '66-unsafe-parte-15', text: "66 · `unsafe` (parte 15)", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Partida e segurança: o mapa"}
      description={"Item por item das partes 13 e 15 da referência Deep Tech — bootstrapping, TLS, pilha, globais, modelo de segurança e unsafe."}
      href={"/docs/partida/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
