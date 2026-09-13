// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Html",
  description: "Ler HTML de verdade: seletor CSS, tabela como dado, e as duas defesas contra XSS.",
};

const blocos: Bloco[] = [
  {"p": "Ler uma página — um preço, uma tabela, os links — só dava por expressão regular, e **HTML não é regular**. A marcação que funciona no teste quebra no primeiro atributo fora de ordem, na primeira tag sem fechar, no primeiro `<br>` no meio."},
  {"h2": "Seletor CSS"},
  { code: `adopt Arcane.Html as Html

doc := Html.ler(pagina)

out doc.achar("#p1 h2").texto
out [n.texto cycle n in doc.achar_todos("div.produto > h2")]
out doc.achar("a[href]").atributo("href")`, lang: 'df' },
  {"table": {"head": ["Escrita", "Casa"], "rows": [["`div`", "a tag"], ["`.classe`", "quem tem a classe"], ["`#id`", "quem tem o id"], ["`[attr]` · `[attr=valor]`", "por atributo"], ["`a b`", "`b` em qualquer lugar dentro de `a`"], ["`a > b`", "`b` filho **direto** de `a`"]]}},
  {"p": "É CSS, e não XPath: `div.preco > span` é o que quem escreve HTML já sabe de cor."},
  {"h2": "O texto junta com espaço"},
  { code: `<span class="preco"><b>R$</b> <span>450,00</span></span>`, lang: 'text' },
  { code: `out doc.achar(".preco").texto        // "R$ 450,00"`, lang: 'df' },
  {"p": "Colado, isso viraria `R$450,00`. Com espaço é o que a página **mostra** — e é o que quem extrai quer."},
  {"h2": "Extrair"},
  { code: `out doc.links("https://forja.br/loja/")
// [{texto: Ver, destino: https://forja.br/produto/1, titulo: }]

out doc.tabela()
// {cabecalho: [Item, Preço], linhas: [[Bigorna, 450], [Marreta, 75]]}

out doc.imagens()`, lang: 'df' },
  {"h2": "As duas defesas"},
  {"h3": "Escapar — antes de mostrar"},
  { code: `respond html $"<p>{Html.escapar(comentario)}</p>"`, lang: 'df' },
  {"p": "É a defesa contra XSS que mais se esquece: um texto que veio de fora, escrito direto na página, é código."},
  {"h3": "Limpar — tirar toda a marcação"},
  { code: `assert Html.limpar("<p>ok</p><script>roubar()</script>") is "ok"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Ele tira o conteúdo do script também", "texto": "Um `limpar` que só tira as **tags** deixa o corpo do `<script>` como texto — e aí o \"texto limpo\" contém exatamente o código que se queria tirar."}},
  {"h3": "Podar — deixar alguma marcação"},
  {"p": "Para comentário e conteúdo de usuário, onde negrito e link fazem sentido:"},
  { code: `seguro := Html.podar(comentario)
// <p>, <b>, <a>, <ul>… passam; <script>, <iframe>, <style> somem`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "A lista é de permitidas", "texto": "Uma lista de **proibidas** esquece a próxima tag perigosa que o navegador inventar. E um `href` que começa com `javascript:` é script com outro nome — ele vira um `<a>` sem destino."}},
  {"h2": "HTML real não é bem formado"},
  {"p": "Tag sem fechar, tag fechada que ninguém abriu, `<br>` solto: o leitor engole tudo isso, porque a página que você quer ler está cheia disso e derrubar a leitura não serve a ninguém."},
];

const headings = [{ id: 'seletor-css', text: "Seletor CSS", level: 2 as const }, { id: 'o-texto-junta-com-espaco', text: "O texto junta com espaço", level: 2 as const }, { id: 'extrair', text: "Extrair", level: 2 as const }, { id: 'as-duas-defesas', text: "As duas defesas", level: 2 as const }, { id: 'escapar-antes-de-mostrar', text: "Escapar — antes de mostrar", level: 3 as const }, { id: 'limpar-tirar-toda-a-marcacao', text: "Limpar — tirar toda a marcação", level: 3 as const }, { id: 'podar-deixar-alguma-marcacao', text: "Podar — deixar alguma marcação", level: 3 as const }, { id: 'html-real-nao-e-bem-formado', text: "HTML real não é bem formado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Html"}
      description={"Ler HTML de verdade: seletor CSS, tabela como dado, e as duas defesas contra XSS."}
      href={"/docs/biblioteca/html"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
