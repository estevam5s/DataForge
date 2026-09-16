// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Templates e a camada de visão",
  description: "A sintaxe de template do Kiln, ao lado de EJS e Handlebars — e por que ela é deliberadamente pequena.",
};

const blocos: Bloco[] = [
  {"p": "EJS, Handlebars e Jinja resolvem o mesmo problema: montar HTML a partir de dado, sem concatenar texto à mão. A diferença entre eles é **quanta linguagem cabe dentro do template** — e essa escolha decide a manutenção do projeto inteiro."},
  {"h2": "As quatro construções"},
  { code: `<h1>{{titulo}}</h1>
{{#produtos}}<article>{{nome}} — {{preco}}</article>{{/produtos}}
{{^produtos}}<p>Nada na forja.</p>{{/produtos}}
<footer>{{&html_bruto}}</footer>
`, lang: 'text', title: `views/loja.html` },
  {"table": {"head": ["Forma", "O que faz"], "rows": [["`{{x}}`", "escreve, **escapando HTML**"], ["`{{&x}}`", "escreve **sem** escapar"], ["`{{#lista}}…{{/lista}}`", "repete para cada item"], ["`{{^lista}}…{{/lista}}`", "mostra quando a lista está vazia"]]}},
  { code: `server loja at "0.0.0.0" on 8000:
    views "views"

    route GET "/":
        render "loja" with {"titulo": "Forja", "produtos": catalogo()}
`, lang: 'df' },
  {"h2": "Ao lado de EJS e Handlebars"},
  {"table": {"head": ["", "EJS", "Handlebars", "Kiln"], "rows": [["código no template", "**JavaScript inteiro**", "helpers registrados", "**nenhum**"], ["escapar por padrão", "não (`<%= %>` escapa, `<%- %>` não)", "sim", "**sim**"], ["condicional", "`if` do JS", "`{{#if}}`", "só \"vazio ou não\""], ["laço", "`for` do JS", "`{{#each}}`", "`{{#lista}}`"], ["chamar função", "sim", "helpers", "**não**"], ["parcial / include", "`include()`", "`{{> parcial}}`", "compor no `.df`"]]}},
  {"callout": {"tipo": "nota", "titulo": "A coluna que mais importa é a primeira linha", "texto": "Quando o template aceita a linguagem inteira, a lógica migra para lá — e vai junto o que não dá para testar sem renderizar HTML. Um template que só sabe escrever, repetir e checar vazio obriga a decisão a ficar no `.df`, onde há tipo, `check` e teste."}},
  {"h2": "O que fazer quando o template \"precisa\" de lógica"},
  {"p": "A resposta é sempre a mesma: decida antes, e passe o resultado pronto."},
  { code: `// em vez de tentar formatar no template:
action para_a_tela(produtos):
    yield [{"nome": p.nome,
            "preco": $"R$ {round(p.preco, 2)}",
            "esgotado": p.estoque is 0}
           cycle p in produtos]

route GET "/":
    render "loja" with {"titulo": "Forja", "produtos": para_a_tela(catalogo())}
`, lang: 'df' },
  {"p": "O ganho não é estético: `para_a_tela` é uma ação comum, e testá-la não exige servidor, socket nem HTML."},
  {"h2": "Escapar é o padrão, e isso é segurança"},
  {"p": "`{{x}}` escapa. É a diferença entre um nome de produto com `<script>` virar texto na tela ou virar código no navegador de quem visita. O `{{&x}}` existe para o caso legítimo — um trecho que você mesmo gerou — e a forma mais longa é de propósito: o inseguro tem de ser escrito de caso pensado."},
  {"h2": "A outra camada de visão"},
  {"p": "Quando a página **é** o programa — um painel, uma ferramenta interna, um relatório interativo — a resposta não é template: é a [Vitrine](/docs/vitrine), onde o `.df` de cima a baixo vira a página, sem HTML nenhum."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/kiln/paginas", "title": "Páginas HTML no Kiln", "desc": "views, layout e o que o render faz"}, {"href": "/docs/vitrine", "title": "Vitrine", "desc": "a página como programa, sem template"}, {"href": "/docs/seguranca", "title": "Segurança", "desc": "escape, CSRF, sessão e o que o framework garante"}]},
];

const headings = [{ id: 'as-quatro-construcoes', text: "As quatro construções", level: 2 as const }, { id: 'ao-lado-de-ejs-e-handlebars', text: "Ao lado de EJS e Handlebars", level: 2 as const }, { id: 'o-que-fazer-quando-o-template-precisa-de-logica', text: "O que fazer quando o template \"precisa\" de lógica", level: 2 as const }, { id: 'escapar-e-o-padrao-e-isso-e-seguranca', text: "Escapar é o padrão, e isso é segurança", level: 2 as const }, { id: 'a-outra-camada-de-visao', text: "A outra camada de visão", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Templates e a camada de visão"}
      description={"A sintaxe de template do Kiln, ao lado de EJS e Handlebars — e por que ela é deliberadamente pequena."}
      href={"/docs/modulos/templates"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
