// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Uma aplicação inteira",
  description: "Um controle de estoque com arquivo, menus, atalhos, confirmação, exportação e teste.",
};

const blocos: Bloco[] = [
  {"p": "Juntando tudo: lê e grava um arquivo, tem menu com atalhos, lista e cadastro em telas separadas, confirma antes de apagar, exporta CSV por um diálogo, lembra a última pasta — e é testada sem display."},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.Serialization as Ser
adopt Arcane.IO as IO
adopt Arcane.OS as OS

// ── onde o dado mora ───────────────────────────────────────
pasta := $"{OS.temp_dir()}/df-estoque-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)
ARQUIVO := $"{pasta}/estoque.json"

action carregar():
    given not IO.exists(ARQUIVO):
        yield []
    yield Ser.from_json(IO.read(ARQUIVO))

action gravar(lista):
    IO.write(ARQUIVO, Ser.to_json(lista))

itens := carregar()

// ── a aplicação ────────────────────────────────────────────
app := B.app("Estoque", pasta_de_config := $"{pasta}/config")
app.menu("Arquivo", [
    B.item("Novo produto", "novo", atalho := "Ctrl+N"),
    B.separador(),
    B.item("Exportar CSV…", "exportar", atalho := "Ctrl+E"),
])

action lista(t):
    t.titulo("Estoque")
    escolhido := t.tabela(["nome", "qtd"], itens, selecionar := yes)
    t.status($"{len(itens)} produto(s)")
    given t.comando("novo") or t.botao("Novo produto", yes):
        t.ir("novo")
    given escolhido isnt void and t.botao("Excluir") and t.confirmar($"Excluir {escolhido["nome"]}?"):
        itens.remove(escolhido)
        gravar(itens)
        t.notificar("excluído")
        t.atualizar()
    given t.comando("exportar"):
        destino := t.salvar_arquivo("estoque.csv", ["csv"])
        given destino isnt void:
            linhas := ["nome,qtd"] + [$"{i["nome"]},{i["qtd"]}" cycle i in itens]
            IO.write(destino, join("\\n", linhas))
            t.guardar_pref("ultimo_export", destino)
            t.notificar($"exportado: {destino}")

action novo(t):
    t.titulo("Novo produto")
    nome := t.entrada("Produto")
    qtd := t.numero("Quantidade", 1, 1, 9999)
    given t.botao("Salvar", yes):
        given nome is "":
            t.erro("o produto é obrigatório")
        orif nome in [i["nome"] cycle i in itens]:
            t.erro($"'{nome}' já está no estoque")
        otherwise:
            itens.append({"nome": nome, "qtd": qtd})
            gravar(itens)
            t.voltar()
    given t.botao("Cancelar"):
        t.voltar()

app.tela("lista", lista)
app.tela("novo", novo)

// ── testar (com display: B.rodar(app)) ─────────────────────
s := B.testar(app)
s.atalho("Ctrl+N")
s.digitar("Produto", "café")
s.digitar("Quantidade", 12)
s.clicar("Salvar")
assert s.tela_atual() is "lista"

s.atalho("Ctrl+N")
s.digitar("Produto", "café")
s.clicar("Salvar")
assert s.tem("já está no estoque")        // o duplicado é recusado
s.clicar("Cancelar")

s.responder($"{pasta}/saida.csv")
s.menu("Arquivo", "Exportar CSV…")
assert IO.read($"{pasta}/saida.csv") is "nome,qtd\\ncafé,12"
assert app.preferencias.ler("ultimo_export") is $"{pasta}/saida.csv"

s.selecionar(0)
s.responder(yes)
s.clicar("Excluir")
assert s.status() is "0 produto(s)"
assert len(Ser.from_json(IO.read(ARQUIVO))) is 0
out "estoque: ok"`, lang: 'df' },
  {"h2": "As decisões que ela carrega"},
  {"table": {"head": ["Decisão", "O que ela evita"], "rows": [["o estado mora **fora** das telas", "ele seria recriado a cada reexecução, e a lista ficaria sempre vazia"], ["gravar a cada mudança", "fechar a janela e perder o trabalho"], ["confirmar **antes** de excluir, com `and`", "o diálogo abrir em toda reexecução, e não só no clique"], ["`t.atualizar()` depois de excluir", "a barra de status mostrar a contagem de antes"], ["a validação devolve `t.erro`, e não levanta", "um erro que fecha a janela no meio do cadastro"], ["`defer` na pasta temporária", "lixo em disco a cada execução do exemplo"]]}},
  {"h2": "O que falta para virar produção"},
  {"list": ["**Desfazer**, que aqui seria uma pilha do estado anterior.", "**Um banco** em vez de JSON, quando passar de alguns milhares de linhas — `Arcane.Database` está a um `adopt` de distância.", "**Assinar** o executável — ver [Empacotar](/docs/desktop/empacotar)."]},
];

const headings = [{ id: 'as-decisoes-que-ela-carrega', text: "As decisões que ela carrega", level: 2 as const }, { id: 'o-que-falta-para-virar-producao', text: "O que falta para virar produção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Uma aplicação inteira"}
      description={"Um controle de estoque com arquivo, menus, atalhos, confirmação, exportação e teste."}
      href={"/docs/desktop/completo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
