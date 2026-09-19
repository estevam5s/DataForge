// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_e_alvos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "WebAssembly, com precisão",
  description: "O DataForge não compila para WASM — e o que existe no lugar funciona. A diferença entre as duas frases importa.",
};

const blocos: Bloco[] = [
  {"p": "A resposta curta: **o DataForge não compila para WebAssembly**, e não há um alvo `wasm32` para o qual gerar módulo."},
  {"p": "A resposta útil é mais longa, e ela começa por separar duas coisas que costumam ser confundidas."},
  {"h2": "Compilar PARA WebAssembly · rodar EM WebAssembly"},
  {"table": {"head": ["", "Compilar para WASM", "Rodar em WASM"], "rows": [["o que é", "produzir um `.wasm` com as funções da sua linguagem", "rodar o **interpretador** dentro de um runtime WASM"], ["quem faz", "Rust, C, Zig, Go, AssemblyScript", "CPython pelo Pyodide, e portanto o DataForge junto"], ["no DataForge", "**não existe**", "**funciona**, e não é uma porta desta linguagem"], ["custo", "—", "o interpretador inteiro vai junto: alguns megabytes antes da primeira linha"]]}},
  {"callout": {"tipo": "nota", "titulo": "Rodar em WASM é rodar o CPython em WASM", "texto": "O Pyodide compila o CPython para WebAssembly e o DataForge roda em cima, como rodaria em qualquer outro CPython. É um resultado real e é a via prática — mas quem chama isso de \"DataForge compila para WASM\" está descrevendo outra coisa, e a diferença aparece no tamanho do artefato e no que o ambiente permite."}},
  {"h2": "O que o item do documento pede, item por item"},
  {"table": {"head": ["Item", "Resposta"], "rows": [["**WASM target**", "**não existe**. Emitir WASM exigiria um backend de geração de código — e a [parte 8](/docs/compilador/backend) explica por que ele não existe nem para código de máquina nativo"], ["**WASI**", "**não como alvo de compilação**. O `wasi` em `Arcane.Alvo` é o perfil de **restrições** de rodar ali dentro, não um formato de saída"], ["**linear memory**", "**não se aplica** diretamente: a memória linear é do runtime WASM que hospeda o CPython, e nenhum objeto do DataForge a alcança"], ["**imports / exports**", "**não se aplica** no sentido do módulo WASM. O análogo da linguagem é `adopt` e `relay`, e o contrato deles tem [ferramenta própria](/docs/abi/compatibilidade)"], ["**host bindings**", "o análogo existe e é real: a [ponte para o Python](/docs/tecnicas/ponte) e o [FFI com C](/docs/ffi/c) — dois jeitos de chamar o que está fora"], ["**SIMD**", "**não se aplica** — ver [o mapa de hardware](/docs/hardware/mapa)"], ["**threads**", "**não no navegador**: dependem de `SharedArrayBuffer` e de isolamento de origem, e o Pyodide as desliga por padrão. É por isso que `threads` está fora do perfil `navegador`"], ["**component model**", "**não se aplica**: sem módulo WASM, não há componente a compor"]]}},
  {"h2": "Se você quer isso hoje"},
  {"p": "O caminho que funciona é o de qualquer projeto Python no navegador: carregar o Pyodide, instalar o pacote e rodar. O que o `Arcane.Alvo` acrescenta é dizer **antes** quais linhas do seu programa não vão sobreviver ali."},
  { code: `adopt Arcane.Alvo as Alvo

// antes de tentar: o que nao roda numa aba?
// r := Alvo.conferir("app.df", "navegador")
// cycle p in r["problemas"]:
//     out $"linha {p['linha']}: {p['modulo']} precisa de {p['capacidade']}"

assert "navegador" in keys(Alvo.alvos())
assert len(Alvo.limites()) bigger_eq 3`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Por que não emitir WASM \"só para dizer que emite\"", "texto": "Seria possível gerar um `.wasm` que implementasse um subconjunto minúsculo da linguagem — literais, contas, talvez um laço. Ele não rodaria nenhum programa do repositório, e passaria a existir como uma caixa que se marca. A [parte 8](/docs/compilador/otimizacao) já mostrou o que acontece quando se mede em vez de supor: a otimização que \"devia\" render, rendeu **1,01×**. Um backend WASM parcial renderia menos que isso, e custaria uma promessa."}},
];

const headings = [{ id: 'compilar-para-webassembly-rodar-em-webassembly', text: "Compilar PARA WebAssembly · rodar EM WebAssembly", level: 2 as const }, { id: 'o-que-o-item-do-documento-pede-item-por-item', text: "O que o item do documento pede, item por item", level: 2 as const }, { id: 'se-voce-quer-isso-hoje', text: "Se você quer isso hoje", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"WebAssembly, com precisão"}
      description={"O DataForge não compila para WASM — e o que existe no lugar funciona. A diferença entre as duas frases importa."}
      href={"/docs/alvos/wasm"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
