// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Telas, menus e atalhos",
  description: "Navegar entre telas com parâmetros, a barra de menus, atalhos que viram Cmd no macOS, status, notificação e a tabela com seleção.",
};

const blocos: Bloco[] = [
  {"h2": "Telas e navegação"},
  {"p": "Cada tela é uma ação que recebe `t`. A **primeira registrada** é a que abre. `t.ir(nome, parametros)` troca de tela e empilha; `t.voltar()` desempilha. Os dois **acabam a tela ali** — o que vem depois deles não roda."},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

clientes := [{"id": 1, "nome": "Ana"}, {"id": 2, "nome": "Bruno"}]
app := B.app("CRM", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")

action lista(t):
    t.titulo("Clientes")
    cycle c in clientes:
        given t.botao(c["nome"]):
            t.ir("cliente", {"id": c["id"]})

action cliente(t):
    id := t.parametro("id")
    t.titulo($"Cliente {id}")
    given t.botao("Voltar"):
        t.voltar()

app.tela("lista", lista)
app.tela("cliente", cliente)

s := B.testar(app)
s.clicar("Bruno")
assert s.tela_atual() is "cliente"
assert s.tem("Cliente 2")
s.clicar("Voltar")
assert s.tela_atual() is "lista"`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Uma tela nova começa limpa", "texto": "Voltar a uma tela de cadastro não traz o que foi digitado na visita anterior. E uma tela que chama `t.ir()` sem condição, mandando para outra que manda de volta, é recusada depois de 16 trocas — com a dica de pôr o `t.ir()` dentro de um `given`, em vez de travar a aplicação."}},
  {"h2": "Menus e atalhos"},
  {"p": "`B.item(rótulo, comando, atalho)` cria um item; `t.comando(\"novo\")` é `yes` na execução em que ele foi escolhido — pelo menu ou pelo atalho, que são o mesmo evento."},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

app := B.app("Editor", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")
app.menu("Arquivo", [
    B.item("Novo", "novo", atalho := "Ctrl+N"),
    B.item("Salvar", "salvar", atalho := "Ctrl+S"),
    B.separador(),
    B.item("Exportar PDF", "pdf", atalho := "Ctrl+Shift+E"),
])
app.menu("Ajuda", [B.item("Sobre", "sobre")])

eventos := []

action tela(t):
    t.titulo("Documento")
    cycle c in ["novo", "salvar", "pdf", "sobre"]:
        given t.comando(c):
            eventos.append(c)

app.tela("doc", tela)

s := B.testar(app)
s.atalho("Cmd+S")                   // Cmd e Ctrl são o mesmo atalho
s.atalho("ctrl+shift+e")            // a grafia é normalizada
s.menu("Ajuda", "Sobre")
assert eventos is ["salvar", "pdf", "sobre"]
out s.menus()`, lang: 'df' },
  {"table": {"head": ["Escrito", "No macOS", "No Windows e no Linux"], "rows": [["`Ctrl+N`", "⌘N", "Ctrl+N"], ["`Ctrl+Shift+S`", "⌘⇧S", "Ctrl+Shift+S"], ["`Alt+F4`", "⌥F4", "Alt+F4"]]}},
  {"p": "O programa escreve `Ctrl` **uma vez**, e no macOS ele vira Cmd sozinho: um atalho que existisse num sistema só obrigaria a ramificar o código. Dois itens com o mesmo atalho são **recusados** — só um deles rodaria, e qual dependeria da ordem."},
  {"h2": "Status, notificação e atualizar"},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

tarefas := ["ler", "escrever", "revisar"]
app := B.app("Tarefas", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")

action tela(t):
    t.lista(tarefas)
    t.status($"{len(tarefas)} tarefa(s)")
    given t.botao("Concluir a primeira"):
        tarefas.remove(tarefas[0])
        t.notificar("concluída")
        t.atualizar()               // o status acima já tinha sido calculado

app.tela("t", tela)

s := B.testar(app)
s.clicar("Concluir a primeira")
assert s.status() is "2 tarefa(s)"
assert s.notificacoes() is ["concluída"]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Por que `t.atualizar()`", "texto": "Um clique vale para UMA execução. O status foi calculado **antes** de a tarefa sair da lista — sem `t.atualizar()`, a barra diria 3 depois de concluir uma. Ele roda a tela de novo, sem o evento e sem apagar os campos."}},
  {"p": "Na janela, a notificação aparece no topo e some sozinha em três segundos; o status fica na barra de baixo."},
  {"h2": "Tabela com seleção"},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

pedidos := [{"n": 101, "total": 30}, {"n": 102, "total": 45}]
app := B.app("Pedidos", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")

action tela(t):
    escolhido := t.tabela(["n", "total"], pedidos, selecionar := yes)
    given escolhido is void:
        t.texto("escolha um pedido")
    otherwise:
        t.texto($"pedido {escolhido["n"]}: R$ {escolhido["total"]}")

app.tela("t", tela)

s := B.testar(app)
assert s.tem("escolha um pedido")
s.selecionar(1)
assert s.tem("pedido 102: R$ 45")`, lang: 'df' },
  {"p": "Ela devolve **o que foi passado** — o vault inteiro, e não o texto da célula —, ou `void` enquanto nada foi escolhido. Uma seleção que aponta para além da lista (ela encolheu) volta a `void`, em vez de devolver outra linha."},
];

const headings = [{ id: 'telas-e-navegacao', text: "Telas e navegação", level: 2 as const }, { id: 'menus-e-atalhos', text: "Menus e atalhos", level: 2 as const }, { id: 'status-notificacao-e-atualizar', text: "Status, notificação e atualizar", level: 2 as const }, { id: 'tabela-com-selecao', text: "Tabela com seleção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Telas, menus e atalhos"}
      description={"Navegar entre telas com parâmetros, a barra de menus, atalhos que viram Cmd no macOS, status, notificação e a tabela com seleção."}
      href={"/docs/desktop/telas-e-menus"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
