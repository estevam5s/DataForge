// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Textos e char*",
  description: "UTF-8 na ida, o NULL que vira void na volta, e o texto que o C alocou e alguém precisa liberar.",
};

const blocos: Bloco[] = [
  {"p": "No C, texto é um ponteiro para bytes terminados em zero — sem codificação declarada e sem tamanho. Declarado como `texto`, o parâmetro vai em **UTF-8** com o zero no fim, e o retorno volta como texto da linguagem, lido até o primeiro zero."},
  { code: `adopt Arcane.C as C

libc := C.padrao()
tamanho := libc.funcao("strlen", ["texto"], "tamanho")
comparar := libc.funcao("strcmp", ["texto", "texto"], "i32")
ambiente := libc.funcao("getenv", ["texto"], "texto")

assert tamanho("café") is 5                       // BYTES em UTF-8, não letras
assert comparar("abc", "abd") smaller 0
assert ambiente("NAO_EXISTE_DE_JEITO_NENHUM") is void   // o NULL do C`, lang: 'df' },
  {"h2": "Três armadilhas"},
  {"table": {"head": ["Armadilha", "O que acontece"], "rows": [["o C conta **bytes**", "`strlen(\"café\")` é 5: o `é` ocupa dois"], ["um zero no meio", "o C para ali: `\"a\\x00b\"` chega como `\"a\"`"], ["texto alocado pelo C", "`strdup`, `getline`: quem recebe **libera** — do lado de cá, com a função de liberar da própria biblioteca"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O texto de retorno é uma cópia", "texto": "O retorno `texto` é **copiado** para um texto da linguagem na hora. Se a função devolveu memória que ela alocou (`strdup`), essa memória continua lá — a cópia não a libera. Declare o retorno como `ponteiro`, leia com `ponteiro.texto()`, e chame o `free` da biblioteca."}},
];

const headings = [{ id: 'tres-armadilhas', text: "Três armadilhas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Textos e char*"}
      description={"UTF-8 na ida, o NULL que vira void na volta, e o texto que o C alocou e alguém precisa liberar."}
      href={"/docs/ffi/textos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
