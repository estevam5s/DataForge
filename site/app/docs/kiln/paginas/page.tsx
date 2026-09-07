import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Páginas HTML",
  description: "Templates, laços, escape automático e layout compartilhado.",
};

const blocos: Bloco[] = [
  {"h2": "Renderizar"},
  { code: `server site on 8080:
    views "./paginas"

    route GET "/":
        render "catalogo.html" with {
            "titulo": "Forja",
            "produtos": produtos
        }` },
  {"p": "`views` diz onde os templates moram; `render` lê um deles, preenche e encerra a rota — como `respond`."},
  {"h2": "A sintaxe do template"},
  {"table": {"head": ["Marca", "Faz"], "rows": [
    ["`{{nome}}`", "escreve o valor, **escapando HTML**"],
    ["`{{&nome}}`", "escreve sem escapar"],
    ["`{{#lista}}…{{/lista}}`", "repete para cada item"],
    ["`{{#vault}}…{{/vault}}`", "entra no vault (e some se ele for vazio)"],
    ["`{{^lista}}…{{/lista}}`", "mostra **quando está vazio**"],
    ["`{{.}}`", "o item atual, numa lista de valores simples"],
    ["`{{a.b.c}}`", "caminho aninhado"]
  ]}},
  { code: `<h1>{{titulo}}</h1>
{{#produtos}}
  <article>
    <h2>{{nome}}</h2>
    <p>{{preco_formatado}}</p>
  </article>
{{/produtos}}
{{^produtos}}<p>Nada na forja ainda.</p>{{/produtos}}` },
  {"p": "É pequena de propósito. Template que vira linguagem é código escondido onde ninguém procura — e ninguém testa. A lógica fica no `.df`."},
  {"h2": "O escape é o padrão"},
  {"p": "Um produto chamado `Bigorna <de aço>` sai como `Bigorna &lt;de aço&gt;`. Isso fecha a porta para XSS **por acidente** — a falha mais comum em página gerada por servidor."},
  {"p": "Para escrever HTML de propósito existe `{{&campo}}`, e a diferença de um caractere é o que torna a decisão visível na revisão de código. Nunca use `{{&}}` com texto vindo do visitante."},
  {"h2": "Formatar antes, não dentro"},
  { code: `action enfeitar(produto):
    yield {
        "nome": produto["nome"],
        "preco_formatado": dinheiro(produto["preco"]),
        "classe_estoque": "pouco" given produto["estoque"] smaller 5 otherwise ""
    }

route GET "/":
    render "catalogo.html" with {
        "produtos": [enfeitar(p) cycle p in produtos]
    }` },
  {"p": "A view recebe o que vai mostrar, já pronto. Formatar dentro do template exigiria lógica no template — e aí você teria escrito uma linguagem, mal."},
  {"h2": "Um layout para todas as páginas"},
  {"p": "Não há `{{> include}}`. O layout se monta com `Kiln.render_string`, que preenche um texto em vez de um arquivo:"},
  { code: `action envolver(app, titulo, conteudo, usuario):
    base := IO.read_file(app.pasta_templates + "/base.html")
    yield Kiln.render_string(base, {
        "titulo": titulo,
        "conteudo": conteudo,     // e no base.html: {{&conteudo}}
        "usuario": usuario
    })` },
  {"p": "Repare no `{{&conteudo}}`: o conteúdo já é HTML e não deve ser escapado de novo. É o único lugar de um site bem escrito onde `{{&}}` é a escolha certa — porque o que entra ali já passou pelo escape na renderização anterior."},
  {"h2": "Erros de template"},
  {"table": {"head": ["Erro", "O Kiln diz"], "rows": [
    ["pasta não declarada", "`nenhuma pasta de templates: use views`"],
    ["arquivo não existe", "`template não encontrado: x.html`"],
    ["bloco aberto e não fechado", "`bloco 'itens' aberto e nunca fechado`"]
  ]}},
  {"p": "Os três chegam como 500 com a mensagem no terminal — e o servidor continua de pé."},
  {"h2": "Um site inteiro"},
  {"p": "O projeto [loja-web](/docs/projetos) tem catálogo com filtro, ficha de produto, relatório, login e um `/relatorio.xlsx` gerado no pedido. São quatro templates, um CSS e 29 testes."},
];

const headings = [{ id: 'renderizar', text: "Renderizar", level: 2 as const }, { id: 'a-sintaxe-do-template', text: "A sintaxe do template", level: 2 as const }, { id: 'o-escape-e-o-padrao', text: "O escape é o padrão", level: 2 as const }, { id: 'formatar-antes-nao-dentro', text: "Formatar antes, não dentro", level: 2 as const }, { id: 'um-layout-para-todas-as-paginas', text: "Um layout para todas as páginas", level: 2 as const }, { id: 'erros-de-template', text: "Erros de template", level: 2 as const }, { id: 'um-site-inteiro', text: "Um site inteiro", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Páginas HTML"}
      description={"Templates, laços, escape automático e layout compartilhado."}
      href={"/docs/kiln/paginas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
