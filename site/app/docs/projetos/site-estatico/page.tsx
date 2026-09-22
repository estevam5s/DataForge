// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gerador de site estático",
  description: "Markdown para HTML com modelo, índice gerado e o texto sempre escapado.",
};

const blocos: Bloco[] = [
  {"p": "Um gerador de site é um compilador pequeno: a entrada são arquivos de texto, a saída são páginas, e no meio há uma árvore. As duas decisões que importam são escapar **tudo** que vem do texto antes de montar HTML, e gerar o índice dos mesmos dados que geram as páginas — uma segunda lista sempre diverge."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`lines` + `match`", "cabeçalho, lista e parágrafo"], ["escape de HTML", "o `<` do texto não vira tag"], ["modelo com `$\"…\"`", "a moldura comum de toda página"], ["o índice dos mesmos dados", "nenhuma página fica fora do menu"]]}},
  {"h2": "Estrutura"},
  { code: `blog/
  conteudo/
    *.md
  modelos/
    pagina.html
  src/
    markdown.df    texto -> html
    gerar.df       le a pasta, escreve saida/
  saida/           (gerado — nao versione)`, lang: 'text' },
  { code: `[project]
name = "blog"
version = "0.1.0"
description = "Gerador de site"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `action escapar(t):
    yield t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\"", "&quot;")

action em_linha(t):
    t := escapar(t)
    yield regex_sub("\\\\*\\\\*(.+?)\\\\*\\\\*", "<strong>\\\\1</strong>", t)

action html_de(markdown):
    saida := []
    em_lista := no
    cycle linha in markdown.lines():
        l := linha.trim()
        given em_lista and not l.startswith("- "):
            saida.append("</ul>")
            em_lista := no
        given l is "":
            skip
        orif l.startswith("## "):
            saida.append($"<h2>{em_linha(l[3:])}</h2>")
        orif l.startswith("# "):
            saida.append($"<h1>{em_linha(l[2:])}</h1>")
        orif l.startswith("- "):
            given not em_lista:
                saida.append("<ul>")
                em_lista := yes
            saida.append($"<li>{em_linha(l[2:])}</li>")
        otherwise:
            saida.append($"<p>{em_linha(l)}</p>")
    given em_lista:
        saida.append("</ul>")
    yield "\\n".join(saida)

action pagina(titulo, corpo, menu):
    yield $"<!doctype html><title>{escapar(titulo)}</title><nav>{menu}</nav><main>{corpo}</main>"

POSTS := [
    {"slug": "ola", "titulo": "Ola", "texto": "# Ola\\n\\nPrimeiro **post**."},
    {"slug": "lista", "titulo": "Uma lista", "texto": "# Lista\\n\\n- um\\n- dois <script>"}
]

menu := "".join(POSTS >> morph p: $"<a href=\\"/{p['slug']}.html\\">{escapar(p['titulo'])}</a>")
site := {}
cycle p in POSTS:
    site[p["slug"] + ".html"] := pagina(p["titulo"], html_de(p["texto"]), menu)

assert "<strong>post</strong>" in site["ola.html"]
assert "<li>dois &lt;script&gt;</li>" in site["lista.html"]
assert "<script>" not in site["lista.html"]
assert site["ola.html"].count("<a href") is len(POSTS)
out site["lista.html"]`, lang: 'df', title: `src/markdown.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/markdown as M

crucible "markdown":
    trial "a lista fecha no fim do arquivo":
        expect M.html_de("- a") is "<ul>\\n<li>a</li>\\n</ul>"`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["escapar **antes** de montar", "um post com `<script>` roda no navegador de quem lê"], ["o menu sai da lista de posts", "o post novo existe e não aparece no site"], ["a lista fecha quando o bloco termina", "o resto da página fica dentro de um `<ul>`"], ["`saida/` fora do git", "cada build gera um diff de milhares de linhas"]]}},
  {"h2": "Para ir além"},
  {"list": ["O escape por destino (atributo, URL, CSS): [Entrada e saída](/docs/seguranca/entrada).", "Servir a pasta gerada com o Kiln: [Estáticos](/docs/kiln/estaticos).", "Recompilar ao salvar: [`dataforge watch`](/docs/cli/watch)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gerador de site estático"}
      description={"Markdown para HTML com modelo, índice gerado e o texto sempre escapado."}
      href={"/docs/projetos/site-estatico"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
