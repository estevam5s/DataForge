// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Erros e errno",
  description: "O C não levanta: devolve -1 ou NULL, e deixa o motivo em errno. C.errno lê o motivo com nome e mensagem.",
};

const blocos: Bloco[] = [
  {"p": "Uma função C não tem exceção. Ela avisa que falhou pelo **retorno** — `-1`, `NULL`, zero — e deixa o motivo numa variável global chamada `errno`: `ENOENT` (não existe), `EACCES` (sem permissão), `EINTR` (interrompida por sinal)…"},
  { code: `adopt Arcane.C as C

libc := C.padrao()
abrir := libc.funcao("open", ["texto", "i32"], "i32")

C.zerar_errno()
fd := abrir("/este/caminho/nao/existe", 0)
assert fd is -1                              // o retorno diz QUE falhou

erro := C.errno()                            // o errno diz POR QUE
assert erro["nome"] is "ENOENT"
out erro["mensagem"]`, lang: 'df' },
  {"h2": "As regras do errno"},
  {"list": ["**Só leia depois de uma falha.** Numa chamada que deu certo, o errno pode ter qualquer valor — a norma do C não manda zerá-lo. Ler o errno de um sucesso é ler o erro de outra chamada.", "**Leia logo.** Toda biblioteca aqui é aberta com `use_errno`: o ctypes guarda uma cópia **por thread**, logo depois de cada chamada. Sem isso, o errno seria sobrescrito pela próxima coisa que o próprio Python fizesse.", "**`zerar_errno` antes, quando o retorno é ambíguo.** `strtol` devolve 0 tanto para \"0\" quanto para erro: zerar antes e olhar depois é o único jeito de distinguir."]},
  { code: `adopt Arcane.C as C

libc := C.padrao()
abrir := libc.funcao("open", ["texto", "i32"], "i32")

action abrir_ou_explicar(caminho):
    C.zerar_errno()
    fd := abrir(caminho, 0)
    given fd is -1:
        e := C.errno()
        trigger $"não abri '{caminho}': {e["mensagem"]} ({e["nome"]})"
    yield fd

motivo := void
monitor:
    abrir_ou_explicar("/nao/existe")
handle Error as e:
    motivo := e.message
assert motivo.contains("ENOENT")`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Por que não levantar sozinho", "texto": "O `ctypes` não sabe qual retorno de cada função significa falha: `-1` é erro no `open`, e um resultado válido numa função de temperatura. Quem sabe é a documentação da função — por isso a conferência fica na sua ação, como acima."}},
];

const headings = [{ id: 'as-regras-do-errno', text: "As regras do errno", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Erros e errno"}
      description={"O C não levanta: devolve -1 ou NULL, e deixa o motivo em errno. C.errno lê o motivo com nome e mensagem."}
      href={"/docs/ffi/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
