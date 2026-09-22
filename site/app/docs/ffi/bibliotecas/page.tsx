// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Achar a biblioteca",
  description: "O nome do arquivo em cada sistema, onde ele é procurado, e o que fazer quando não acha.",
};

const blocos: Bloco[] = [
  {"p": "A mesma biblioteca tem três nomes: `libz.so.1` no Linux, `libz.dylib` no macOS, `zlib1.dll` no Windows. `C.carregar(\"z\")` procura pelo nome curto no lugar em que o sistema procura, e aceita também o caminho completo."},
  { code: `adopt Arcane.C as C

libc := C.padrao()                  // libc, ou msvcrt no Windows
assert libc.tem("strlen")
assert not libc.tem("funcao_que_nao_existe")

falhou := no
monitor:
    C.carregar("biblioteca_que_nao_existe_aqui")
handle RuntimeError as e:
    falhou := yes
    out e.message
assert falhou`, lang: 'df' },
  {"table": {"head": ["Sistema", "Arquivo", "Onde procura", "Se não achar"], "rows": [["Linux", "`libNOME.so`", "`/usr/lib`, `/lib`, `LD_LIBRARY_PATH`", "instale o pacote `-dev`"], ["macOS", "`libNOME.dylib`", "`/usr/lib`, Homebrew, `DYLD_LIBRARY_PATH`", "`brew install NOME`, ou o caminho completo"], ["Windows", "`NOME.dll`", "a pasta do programa, `PATH`", "ponha a pasta da DLL no `PATH`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`tem` antes de `funcao`", "texto": "A mesma biblioteca muda entre versões: uma função nova numa versão, removida em outra. `libc.tem(\"nome\")` pergunta sem levantar, e deixa o programa escolher outro caminho em vez de morrer na primeira chamada."}},
  {"p": "`C.do_processo()` abre os símbolos do próprio processo — o `dlopen(NULL)` —, e `C.matematica()` resolve a `libm`, que no macOS mora dentro da `libSystem`."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Achar a biblioteca"}
      description={"O nome do arquivo em cada sistema, onde ele é procurado, e o que fazer quando não acha."}
      href={"/docs/ffi/bibliotecas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
