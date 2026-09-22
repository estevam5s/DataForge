// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "FFI: chamar C",
  description: "Quando uma biblioteca nativa é o único caminho — e o que custa atravessar a fronteira.",
};

const blocos: Bloco[] = [
  {"p": "`Arcane.C` chama funções de bibliotecas nativas — a `libc`, a `libm`, um `.so`/`.dylib`/`.dll` qualquer — sem compilar nada: roda sobre o `ctypes` da biblioteca padrão do Python. É a porta para o que só existe em C: um driver, uma biblioteca de áudio, o código legado da empresa."},
  { code: `adopt Arcane.C as C

libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
assert raiz(2.0) bigger 1.414 and raiz(2.0) smaller 1.415`, lang: 'df' },
  {"table": {"head": ["Precisa de", "Use", "Não FFI"], "rows": [["uma biblioteca Python (numpy, pandas)", "—", "[`adopt Python.numpy`](/docs/tecnicas/ponte)"], ["um programa de linha de comando", "—", "`Arcane.Process`"], ["ler um formato binário", "—", "[`Arcane.Estrutura`](/docs/estruturas)"], ["uma função que só existe em C", "**`Arcane.C`**", ""]]}},
  {"callout": {"tipo": "perigo", "titulo": "A fronteira não tem rede", "texto": "Do lado de cá, todo acesso é conferido. Do lado do C, não: uma assinatura errada, um ponteiro solto ou um tamanho trocado corrompem memória, e o processo pode morrer sem mensagem nenhuma. Tudo nesta seção é sobre reduzir esse risco — e ele nunca vai a zero."}},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/ffi/c", "title": "Chamar C", "desc": "carregar, declarar a assinatura, chamar"}, {"href": "/docs/ffi/tipos", "title": "Os tipos do C", "desc": "qual tipo daqui para qual de lá, e o long que muda de tamanho"}, {"href": "/docs/ffi/textos", "title": "Textos e char*", "desc": "codificação, NULL e quem libera"}, {"href": "/docs/ffi/erros", "title": "Erros e errno", "desc": "o -1, o NULL e o ENOENT"}, {"href": "/docs/ffi/ponteiros", "title": "Ponteiros e memória crua", "desc": "alocar, andar e liberar"}, {"href": "/docs/ffi/callbacks", "title": "Callbacks", "desc": "o C chamando uma ação DataForge"}, {"href": "/docs/ffi/bibliotecas", "title": "Achar a biblioteca", "desc": "Linux, macOS e Windows"}, {"href": "/docs/ffi/seguranca", "title": "Segurança na fronteira", "desc": "o que corrompe memória, e como evitar"}, {"href": "/docs/ffi/desempenho", "title": "Custo de uma chamada", "desc": "quando vale atravessar, e quando não"}, {"href": "/docs/ffi/mapa", "title": "FFI: o mapa", "desc": "tudo o que existe, e o que não"}]},
];

const headings = [{ id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"FFI: chamar C"}
      description={"Quando uma biblioteca nativa é o único caminho — e o que custa atravessar a fronteira."}
      href={"/docs/ffi"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
