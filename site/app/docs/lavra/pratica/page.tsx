// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Na prática",
  description: "CRUD, banco de dados, DDD, testes, documentação, Docker, CI e como organizar um projeto Lavra.",
};

const blocos: Bloco[] = [
  {"h2": "A organização de um projeto"},
  { code: `minha-api/
    forge.toml
    src/
        main.df              sobe o servidor
        esquema.df           monta o esquema e devolve
        tipos/
            usuario.df       record + tipo + campos + resolvedores
            pedido.df
        dominio/
            preco.df         a REGRA, sem saber que existe Lavra
            estoque.df
        infra/
            banco.df         as consultas SQL
    consultas/
        painel.lavra         as consultas guardadas
    tests/
        esquema_test.df
        usuario_test.df`, lang: 'text' },
  {"p": "A regra que faz a diferença: **`dominio/` não importa `Arcane.Lavra`**. O cálculo de preço não muda porque a API mudou de forma, e um teste de domínio não precisa montar esquema nenhum."},
  { code: `// dominio/preco.df — sem uma linha de Lavra
action preco_final(produto, cupom):
    base := produto.preco
    given cupom isnt void and cupom.valido:
        base := base * (1.0 - cupom.desconto)
    yield round(base, 2)

relay preco_final`, lang: 'df' },
  { code: `// tipos/produto.df — a casca fina que liga os dois
adopt ../dominio/preco as Preco

action preco_de(produto, args, ctx):
    yield Preco.preco_final(produto, buscar_cupom(args["cupom"]))

Lavra.campo(esq, "Produto", "preco_final", "Float!",
    args := {"cupom": "String"}, resolve := preco_de)`, lang: 'df' },
  {"h2": "CRUD completo"},
  { code: `// ── ler ──
Lavra.busca(esq, "produto", "Produto", args := {"id": "Integer!"},
    resolve := lambda r, a, ctx => Banco.achar(ctx["banco"], "produtos", a["id"]))

Lavra.busca(esq, "produtos", "PaginaProduto!",
    args := {"primeiros": {"tipo": "Integer", "padrao": 20},
             "depois": "String",
             "busca": "String"},
    resolve := listar_produtos)

// ── criar ──
Lavra.mudanca(esq, "criarProduto", "Produto!",
    args := {"dados": "NovoProduto!"}, resolve := criar_produto)

// ── alterar ──
Lavra.mudanca(esq, "alterarProduto", "Produto!",
    args := {"id": "Integer!", "dados": "AlteraProduto!"},
    resolve := alterar_produto)

// ── apagar ──
Lavra.mudanca(esq, "apagarProduto", "Boolean!",
    args := {"id": "Integer!"}, resolve := apagar_produto)`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Três entradas, não uma", "texto": "`NovoProduto` exige nome e preço; `AlteraProduto` tem tudo opcional, porque alterar um campo não é reenviar o objeto. Usar a mesma entrada nos dois obrigaria a tornar tudo opcional — e aí a criação deixaria de ser conferida."}},
  {"h2": "Com banco de dados"},
  { code: `adopt Arcane.Database as Banco

action listar_produtos(raiz, args, ctx):
    consulta := Banco.select(ctx["banco"], "produtos")
    given args["busca"] isnt void:
        consulta := Banco.search(consulta, args["busca"])
    yield Lavra.pagina(Banco.todos(consulta),
                       primeiros := args["primeiros"],
                       depois := args["depois"])

action criar_produto(raiz, args, ctx):
    yield Banco.transacao(ctx["banco"], lambda => gravar(ctx, args["dados"]))`, lang: 'df' },
  {"p": "A transação é do `Arcane.Database`, e não do Lavra: a venda gravada com o estoque não baixado é o mesmo problema em qualquer camada, e ele já está resolvido embaixo."},
  {"callout": {"tipo": "perigo", "titulo": "Ordenação que vem de fora vai crua para o SQL", "texto": "`ordem: \"nome\"` numa consulta chega ao `ORDER BY`. O `Arcane.Database` recusa o que não parece nome de coluna — mas o esquema resolve melhor: declare `ordem` como um **enum**, e o que não for um dos valores nem chega ao resolvedor."}},
  {"h2": "Testes"},
  { code: `adopt Arcane.Crucible as Crucible
adopt ../src/esquema as E

crucible "o esquema":
    trial "fecha":
        Lavra.conferir(E.montar())

    trial "toda busca tem resolvedor":
        esq := E.montar()
        descricao := Lavra.descrever(esq)
        cycle campo in descricao["busca"]["campos"]:
            assert campo["tipo"] isnt "", $"{campo['nome']} sem tipo"

crucible "usuario":
    trial "traz só o que foi pedido":
        c := Lavra.local(E.montar())
        dados := c.dados("busca:
    usuario(id: 1):
        nome")
        assert dados["usuario"] is {"nome": "Ana"}

    trial "o campo que não existe é recusado":
        problemas := Lavra.validar(E.montar(), "busca:
    usuario(id: 1):
        nomee")
        assert len(problemas) is 1
        assert "nome" in problemas[0]["dica"]`, lang: 'df' },
  {"p": "Três coisas valem um teste próprio, e são as que mais quebram:"},
  {"list": ["**O esquema fecha.** Um `conferir` no teste é o que impede uma subida quebrada.", "**O N+1 não voltou.** Conte as idas ao banco, e não o resultado: um lote que devolve o valor certo e consulta cinquenta vezes passa em qualquer teste que só olhe os dados.", "**A consulta guardada ainda vale.** Valide cada arquivo de `consultas/` contra o esquema atual; é assim que uma mudança que quebra o cliente aparece na CI."]},
  { code: `crucible "as consultas guardadas ainda valem":
    cycle arquivo in IO.list_dir("consultas"):
        trial arquivo:
            problemas := Lavra.validar(E.montar(), IO.read($"consultas/{arquivo}"))
            assert len(problemas) is 0, $"{arquivo}: {problemas}"`, lang: 'df' },
  {"h2": "Documentação"},
  {"p": "A do esquema sai do esquema — `descricao` em cada campo, e `Lavra.descrever` ou `Lavra.texto_do_esquema` para lê-la. Uma página escrita à mão ao lado envelheceria em silêncio, que é o defeito que este projeto persegue em todo lugar."},
  { code: `Lavra.campo(esq, "Produto", "preco_final", "Float!",
    args := {"cupom": "String"},
    resolve := preco_de,
    descricao := "O preço com o cupom aplicado. Sem cupom, é o preço de tabela.")

Lavra.campo(esq, "Produto", "preco_antigo", "Float",
    obsoleto := "use 'preco_final'; este some na 2.0")`, lang: 'df' },
  {"p": "Um campo `obsoleto` continua funcionando e **aparece na validação** como aviso. É como se tira um campo sem quebrar quem ainda o usa: primeiro ele avisa, depois some."},
  {"h2": "Convivendo com REST"},
  {"p": "Os dois no mesmo app, sem escolher:"},
  { code: `server api on 8080:
    route GET "/saude":
        respond json {"ok": yes}

    route POST "/webhooks/pagamento":
        respond 200 json processar(body)

Lavra.montar(api, esq, "/lavra")`, lang: 'df' },
  {"p": "Webhook, upload e download continuam REST — e devem. Um webhook é chamado por quem não conhece o seu esquema; um download é um arquivo, não um grafo."},
  {"h2": "Docker e CI"},
  { code: `dataforge devops dockerfile
dataforge devops compose
dataforge devops ci`, lang: 'bash' },
  {"p": "O que muda para uma API Lavra:"},
  {"list": ["**`--host=0.0.0.0`** no `ignite`. O padrão é `127.0.0.1`, que de dentro do container significa o próprio container — e o sintoma engana: o log diz \"no ar\" e o `curl` de fora não recebe nada.", "**O esquema em texto entra no repositório.** `Lavra.texto_do_esquema` num arquivo versionado faz cada mudança aparecer no diff.", "**A CI valida as consultas guardadas** contra o esquema do commit. É o que transforma \"quebrou o app\" em \"a revisão não passou\"."]},
  { code: `# .github/workflows/ci.yml
- name: o esquema nao mudou sem aviso
  run: |
    dataforge run scripts/exportar_esquema.df > /tmp/atual.lavra
    diff -u esquema.lavra /tmp/atual.lavra`, lang: 'yaml' },
  {"h2": "Boas práticas"},
  {"table": {"head": ["Faça", "Porque"], "rows": [["Declare os três limites", "a consulta funda é a forma mais barata de derrubar o servidor"], ["Use `!` onde a promessa é real", "um `!` que às vezes é void é pior que não ter `!`"], ["Autorize no **campo**, não na busca", "num grafo, todo caminho é uma porta"], ["Um lote por relacionamento", "o N+1 não aparece em teste que só olha o resultado"], ["Pagine por cursor", "paginar por posição faz itens sumirem"], ["Entrada separada da saída", "o mesmo tipo nos dois lados deixa de conferir os dois"], ["Desligue a introspecção em produção", "o esquema é um mapa para quem for procurar"], ["Versione o esquema em texto", "a quebra aparece na revisão, e não no app"]]}},
  {"cards": [{"href": "/docs/exercicios/33-lavra", "title": "Os exercícios", "desc": "Três programas que rodam e provam o que esta página afirma."}, {"href": "/docs/lavra/desempenho", "title": "Desempenho", "desc": "O N+1, medido."}, {"href": "/docs/lavra/seguranca", "title": "Segurança", "desc": "O que um servidor de consulta tem de diferente."}]},
];

const headings = [{ id: 'a-organizacao-de-um-projeto', text: "A organização de um projeto", level: 2 as const }, { id: 'crud-completo', text: "CRUD completo", level: 2 as const }, { id: 'com-banco-de-dados', text: "Com banco de dados", level: 2 as const }, { id: 'testes', text: "Testes", level: 2 as const }, { id: 'documentacao', text: "Documentação", level: 2 as const }, { id: 'convivendo-com-rest', text: "Convivendo com REST", level: 2 as const }, { id: 'docker-e-ci', text: "Docker e CI", level: 2 as const }, { id: 'boas-praticas', text: "Boas práticas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Na prática"}
      description={"CRUD, banco de dados, DDD, testes, documentação, Docker, CI e como organizar um projeto Lavra."}
      href={"/docs/lavra/pratica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
