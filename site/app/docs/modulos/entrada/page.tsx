// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O ponto de entrada",
  description: "app.df monta, main.df sobe — e por que importar um módulo não pode ter efeito.",
};

const blocos: Bloco[] = [
  {"p": "Todo código no topo de um módulo roda no `adopt`. Por isso um módulo que **sobe um servidor** no topo trava qualquer teste que o importe: o teste nunca termina. A regra é separar quem **monta** de quem **roda**."},
  { code: `projeto/
  forge.toml       entry = "src/main.df"
  src/
    app.df         monta: rotas, regras — sem efeito no topo
    main.df        roda: le o ambiente, 'ignite', 'OS.exit'
  tests/
    app_test.df    adopt ../src/app — e nada sobe`, lang: 'text' },
  { code: `// app.df — so declara
adopt Kiln
server api on 0:
    route GET "/":
        respond json {"ok": yes}

// main.df — o unico com efeito
//     adopt ./app as App
//     ignite App.api at "0.0.0.0"

r := Kiln.test(api, "GET", "/")
assert r["status"] is 200`, lang: 'df' },
  {"table": {"head": ["No topo de um módulo", "Pode?"], "rows": [["declarar ações, records, constantes", "sim"], ["abrir uma conexão **preguiçosa**", "sim — uma ação que abre no primeiro uso"], ["subir servidor, ler `input`, `OS.exit`", "**não** — só no ponto de entrada"], ["imprimir", "evite: aparece em todo teste que importar"]]}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O ponto de entrada"}
      description={"app.df monta, main.df sobe — e por que importar um módulo não pode ter efeito."}
      href={"/docs/modulos/entrada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
