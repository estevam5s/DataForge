// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_e_alvos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "ABI, ligador e alvos: o mapa",
  description: "Item por item das partes 18 e 19 da referência Deep Tech — ABI, linker, executáveis, WebAssembly e targets especializados.",
};

const blocos: Bloco[] = [
  {"p": "Duas partes que parecem inteiramente \"não se aplica\" — e não são. O que transfere delas não é o binário: é o **contrato** e a **restrição de ambiente**, que existem em qualquer linguagem que se distribua."},
  {"h2": "72 · ABI"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["**binary compatibility**", "a **superfície** é o contrato, e `dataforge abi` diz o que quebrou", "[Compatibilidade](/docs/abi/compatibilidade)"], ["**versioning**", "o veredito de semver que a mudança **exige** — antes era escolhido a olho", "[Compatibilidade](/docs/abi/compatibilidade)"], ["**symbol naming**", "o `relay` decide o que é público; o mapa diz de onde vem cada nome", "[Símbolos](/docs/abi/simbolos)"], ["calling conventions", "reais, mas **só na fronteira com o C**: `ctypes` aplica a ABI da plataforma", "[FFI](/docs/ffi/c)"], ["struct layout", "`C.estrutura` dá tamanho, alinhamento e deslocamento de verdade — inclusive o padding", "[Chamar C](/docs/ffi/c)"], ["enum representation", "`C.enumeracao`: inteiro com nome, que é o que atravessa", "[Chamar C](/docs/ffi/c)"], ["platform-specific ABI", "vem do `ctypes`, que segue a do sistema", "[FFI](/docs/ffi/mapa)"], ["register / stack conventions", "**não se aplica**: não há registrador alcançável", "—"]]}},
  {"h2": "73 · Linker"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["**symbol resolution**", "`resolucao.py` — onde mora o módulo de um `adopt`, e **a única cópia** dessa regra; o mapa é o relatório dela", "[Símbolos](/docs/abi/simbolos)"], ["dynamic linking", "`C.carregar` abre `.so`, `.dylib` e `.dll` em tempo de execução — é `dlopen` de verdade", "[FFI](/docs/ffi/c)"], ["\"linkar\" dependências", "`forge_modules/`, `forge.lock` e a resolução com semver do gerenciador", "[Pacotes](/docs/cli/pacotes)"], ["detecção de ciclo", "erro do `check`, com a **cadeia inteira** na mensagem — busca em largura, para achar o ciclo mais curto", "[Carga](/docs/modulos/carga)"], ["static linking, relocations, sections", "**não se aplica**: não há passo de ligação, e nada é relocado"], ["ELF, PE/COFF, Mach-O", "os binários do release **são** esses formatos — produzidos pelo PyInstaller, não pelo DataForge", "[Download](/download)"], ["linker scripts", "**não se aplica**"]]}},
  {"h2": "74 · Executáveis"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["executables", "o release constrói para **quatro** plataformas e roda os exercícios *pelo binário* em cada uma", "[Download](/download)"], ["static libraries", "o análogo é o **pacote**: `dataforge pack` produz um tarball reprodutível (`mtime=0`, uid/gid zerados), senão o sha256 mudaria a cada empacotamento", "[Pacotes](/docs/cli/pacotes)"], ["dynamic libraries", "do lado de consumo: `Arcane.C`", "[FFI](/docs/ffi/c)"], ["entry points", "`forge.toml` declara a entrada; `dataforge run` sem arquivo a usa", "[forge.toml](/docs/cli/forge-toml)"], ["**debug symbols**", "o análogo é a informação de posição: linha, coluna e `span` em **todo** nó e **todo** erro — é ela que desenha a seta", "[Erros](/docs/erros)"], ["stripping", "**não se aplica**, e a razão é boa: tirar a informação de posição não economizaria nada que importe, e a mensagem de erro é metade do valor da linguagem"], ["object files, relocations, sections", "**não se aplica**"]]}},
  {"h2": "75 · WebAssembly"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["WASM target, WASI como saída", "**não existe** — e a diferença entre *compilar para* e *rodar em* está escrita", "[WebAssembly](/docs/alvos/wasm)"], ["**rodar em WASM**", "**funciona**, pelo Pyodide: é rodar o CPython em WebAssembly", "[WebAssembly](/docs/alvos/wasm)"], ["host bindings", "o análogo existe: a ponte para o Python e o FFI com C", "[Ponte](/docs/tecnicas/ponte)"], ["threads no navegador", "**não**, e o perfil `navegador` diz por quê (SharedArrayBuffer e isolamento de origem)", "[Portabilidade](/docs/alvos/portabilidade)"], ["linear memory, imports/exports, SIMD, component model", "**não se aplica** sem módulo WASM", "[WebAssembly](/docs/alvos/wasm)"]]}},
  {"h2": "76 · Targets especializados"},
  {"table": {"head": ["Alvo", "Resposta"], "rows": [["**server**", "é o alvo padrão, e onde tudo foi medido"], ["**desktop / CLI**", "sim: quatro plataformas no release, com instalador gráfico no Windows"], ["**WebAssembly**", "rodando o CPython, não compilando — ver acima"], ["**serverless**", "o perfil `funcao` existe e diz o que não sobrevive: processo, thread longa, biblioteca nativa"], ["**mobile**", "**não há porta**. Existe CPython em Android e iOS, e nada disso foi testado aqui — dizer \"sim\" sem ter rodado seria inventar"], ["**embedded / bare-metal / kernel**", "**não se aplica** — ver [o mapa de hardware](/docs/hardware/mapa)"], ["**game engines**", "**não se aplica**: o laço de renderização precisa de milissegundos previsíveis, e um interpretador de árvore com GC não os dá"], ["**HPC / scientific computing**", "**pela ponte**: `adopt Python.numpy` traz a conta vetorizada de verdade, e `P.map_processos` usa mais de um núcleo. O que o DataForge não faz é ser o laço numérico"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das duas partes, **a 18 rendeu mais do que parecia**: ABI não é sobre bytes, é sobre **contrato** — e o contrato existe aqui, quebra do mesmo jeito e agora tem ferramenta que o confere. A **19 rendeu o perfil de restrições**, que responde a pergunta real (\"roda no navegador?\") sem prometer um backend que não existe."},
  {"callout": {"tipo": "nota", "titulo": "O que estas duas partes entregaram", "texto": "Dois módulos (`Arcane.Abi`, `Arcane.Alvo`), dois comandos (`dataforge abi`, `dataforge alvo`), onze regras de compatibilidade nomeadas com o que fazer em cada uma, seis perfis de alvo com o **porquê** de cada ausência — e um terceiro balde para o caso que a superfície não decide, em vez de uma resposta inventada."}},
];

const headings = [{ id: '72-abi', text: "72 · ABI", level: 2 as const }, { id: '73-linker', text: "73 · Linker", level: 2 as const }, { id: '74-executaveis', text: "74 · Executáveis", level: 2 as const }, { id: '75-webassembly', text: "75 · WebAssembly", level: 2 as const }, { id: '76-targets-especializados', text: "76 · Targets especializados", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"ABI, ligador e alvos: o mapa"}
      description={"Item por item das partes 18 e 19 da referência Deep Tech — ABI, linker, executáveis, WebAssembly e targets especializados."}
      href={"/docs/abi/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
