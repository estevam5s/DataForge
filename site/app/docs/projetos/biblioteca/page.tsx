// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Biblioteca publicável",
  description: "Validador de placas de veículo — com `relay`, erro que diz o motivo e o pacote pronto para o registro.",
};

const blocos: Bloco[] = [
  {"p": "Uma biblioteca é um projeto sem `main`: quem roda é o código de outra pessoa. Isso muda três coisas — o que é público precisa ser declarado, o erro precisa servir a quem não leu o seu código, e a versão passa a ser uma promessa."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`relay`", "a superfície pública, e só ela"], ["o vault de resultado", "`{ok, motivo}` em vez de `no`"], ["`dataforge pack`", "o tarball reprodutível"], ["o teste pelo **nome** do pacote", "`adopt placa`, como o usuário faria"]]}},
  {"h2": "Estrutura"},
  { code: `placa/
  forge.toml
  src/
    main.df        relay validar, formatar, tipo
  tests/
    placa_test.df  adopt placa  (pelo nome!)
  README.md`, lang: 'text' },
  { code: `[project]
name = "placa"
version = "1.0.0"
description = "Valida e formata placas brasileiras (antiga e Mercosul)"
entry = "src/main.df"
license = "MIT"
dataforge = ">=1.1"

[dependencies]`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `// Antiga: ABC-1234. Mercosul: ABC1D23.
steady ANTIGA := "^[A-Z]{3}-?[0-9]{4}$"
steady MERCOSUL := "^[A-Z]{3}[0-9][A-Z][0-9]{2}$"

action _limpar(texto):
    yield texto.trim().upper().replace(" ", "")

action tipo(texto):
    t := _limpar(texto)
    given regex_test(MERCOSUL, t):
        yield "mercosul"
    given regex_test(ANTIGA, t):
        yield "antiga"
    yield void

action validar(texto):
    given texto is void or _limpar(texto) is "":
        yield {"ok": no, "motivo": "placa vazia"}
    t := _limpar(texto)
    given len(t.replace("-", "")) is not 7:
        yield {"ok": no, "motivo": $"tem {len(t.replace('-', ''))} caracteres, e uma placa tem 7"}
    given tipo(t) is void:
        yield {"ok": no, "motivo": "nao e nem o formato antigo (ABC-1234) nem o Mercosul (ABC1D23)"}
    yield {"ok": yes, "motivo": "", "tipo": tipo(t)}

action formatar(texto):
    t := _limpar(texto).replace("-", "")
    given tipo(t) is "antiga":
        yield t[0:3] + "-" + t[3:]
    yield t

relay validar, formatar, tipo

assert validar("abc1d23")["tipo"] is "mercosul"
assert formatar("abc1234") is "ABC-1234"
assert "7" in validar("AB123")["motivo"]
assert not validar("ABC12D3")["ok"]
out validar("ABC12D3")["motivo"]`, lang: 'df', title: `src/main.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt placa as P

crucible "placa":
    trial "o motivo diz o que esta errado":
        expect P.validar("")["motivo"] is "placa vazia"

    trial "_limpar nao e publico":
        expect(lambda => P._limpar("x")).to_raise()`, lang: 'df', title: `tests/placa_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["`relay` explícito", "o `_limpar` interno vira contrato e nunca mais pode mudar"], ["o motivo em vez de `no`", "o formulário de quem usa diz *“placa inválida”* e mais nada"], ["o teste pelo nome do pacote", "a biblioteca funciona no repositório e quebra instalada"], ["`license` no manifesto", "a empresa de quem instala não pode usar"]]}},
  {"h2": "Para ir além"},
  {"list": ["O ciclo inteiro de uma biblioteca: [Escrever uma biblioteca](/docs/bibliotecas).", "Publicar no registro: [Publicar](/docs/bibliotecas/publicar).", "O desenho da API: [Desenhar a API pública](/docs/bibliotecas/api)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Biblioteca publicável"}
      description={"Validador de placas de veículo — com `relay`, erro que diz o motivo e o pacote pronto para o registro."}
      href={"/docs/projetos/biblioteca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
