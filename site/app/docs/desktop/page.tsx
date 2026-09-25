// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Aplicações de mesa",
  description: "Bigorna: o framework de aplicações de mesa — várias telas, menus com atalhos, diálogos nativos e preferências, em macOS, Windows e Linux, com zero dependência.",
};

const blocos: Bloco[] = [
  {"p": "A **Bigorna** é o framework de aplicações de mesa do DataForge. Ela desenha janelas **nativas** com o Tk, que vem na biblioteca padrão do Python — nada para instalar em macOS, Windows ou Linux — e acrescenta o que uma aplicação de verdade tem em volta da tela: navegação, barra de menus, atalhos, diálogos do sistema, barra de status e preferências salvas."},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

produtos := [{"nome": "café", "qtd": 12}]

app := B.app("Estoque", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")
app.menu("Arquivo", [B.item("Novo produto", "novo", atalho := "Ctrl+N")])

action lista(t):
    t.titulo("Produtos")
    t.tabela(["nome", "qtd"], produtos)
    t.status($"{len(produtos)} produto(s)")
    given t.comando("novo"):
        t.ir("novo")

action novo(t):
    t.titulo("Novo produto")
    nome := t.entrada("Nome")
    given t.botao("Salvar"):
        produtos.append({"nome": nome, "qtd": 0})
        t.voltar()

app.tela("lista", lista)
app.tela("novo", novo)

// Com display: B.rodar(app) abre a janela. Aqui, a Sonda usa a MESMA
// aplicação sem abrir nada — é assim que ela roda no CI.
s := B.testar(app)
s.atalho("Ctrl+N")                  // no macOS, Cmd+N — o mesmo atalho
s.digitar("Nome", "açúcar")
s.clicar("Salvar")
assert s.tela_atual() is "lista"
assert s.status() is "2 produto(s)"
out s.texto()`, lang: 'df' },
  {"h2": "O que ela acrescenta à Janela"},
  {"p": "`Arcane.Janela` desenha **uma** tela. A Bigorna usa a mesma tela — os mesmos 22 componentes, a mesma árvore — e acrescenta o que vem em volta:"},
  {"table": {"head": ["Peça", "Como se escreve", "Página"], "rows": [["várias telas", "`app.tela(\"novo\", novo)` · `t.ir(\"novo\")` · `t.voltar()`", "[Telas e menus](/docs/desktop/telas-e-menus)"], ["barra de menus", "`app.menu(\"Arquivo\", [B.item(...)])`", "[Telas e menus](/docs/desktop/telas-e-menus)"], ["atalhos de teclado", "`atalho := \"Ctrl+N\"` — vira Cmd+N no macOS", "[Telas e menus](/docs/desktop/telas-e-menus)"], ["diálogos do sistema", "`t.confirmar(...)` · `t.abrir_arquivo()` · `t.salvar_arquivo()`", "[Diálogos](/docs/desktop/dialogos)"], ["status e notificação", "`t.status(\"3 itens\")` · `t.notificar(\"salvo\")`", "[Telas e menus](/docs/desktop/telas-e-menus)"], ["tabela com seleção", "`linha := t.tabela(..., selecionar := yes)`", "[Telas e menus](/docs/desktop/telas-e-menus)"], ["preferências", "`t.pref(\"tema\")` · `t.guardar_pref(\"tema\", \"escuro\")`", "[Preferências e tema](/docs/desktop/preferencias-e-tema)"], ["tema", "`B.app(..., tema := \"escuro\")`", "[Preferências e tema](/docs/desktop/preferencias-e-tema)"]]}},
  {"h2": "A forma: o programa roda de novo"},
  {"p": "Como na Vitrine, **cada tela roda de novo a cada interação**, e o estado sobrevive. Um clique, um item de menu e um atalho são **eventos**: valem para uma execução só, e por isso um formulário não é salvo duas vezes. É o que dispensa callback e diffing — e o que torna a aplicação testável."},
  {"table": {"head": ["", "Callback (Tk cru, Qt)", "Reexecução (Bigorna)"], "rows": [["onde mora o estado", "espalhado em widgets", "no vault da tela"], ["ler um campo", "`entry.get()`", "`nome := t.entrada(\"Nome\")`"], ["redesenhar", "você lembra de fazer", "acontece"], ["testar", "precisa de display e de robô", "`B.testar(app)`"], ["o custo", "—", "a tela roda inteira a cada evento"]]}},
  {"h2": "Começar"},
  { code: `$ dataforge desktop novo estoque
$ cd estoque
$ dataforge test                     # a aplicação inteira, sem abrir janela
$ dataforge desktop rodar src/main.df
$ dataforge desktop empacotar src/main.df --nome=Estoque`, lang: 'bash' },
  {"p": "O esqueleto separa `src/tela.df` (a aplicação montada) de `src/main.df` (que abre a janela) pelo mesmo motivo do Kiln: um teste que importasse o módulo que abre a janela **nunca terminaria**. E ele já sai com quatro testes — atalho, menu, validação e exclusão confirmada — que passam no primeiro `dataforge test`."},
  {"h2": "O que ela NÃO é"},
  {"list": ["Não há arrastar-e-soltar, animação, ícone na bandeja do sistema nem janela transparente: o Tk não os tem de forma portável, e prometer um recurso que funciona num sistema só é pior que não prometer.", "Para **painel de dados**, a [Vitrine](/docs/vitrine), no navegador. Para o **celular**, a [Brasa](/docs/mobile).", "Para a mesma regra de negócio nos três, ver [Multiplataforma](/docs/multiplataforma)."]},
  {"cards": [{"title": "Telas e menus", "desc": "navegação, menus, atalhos, status, notificação e seleção.", "href": "/docs/desktop/telas-e-menus"}, {"title": "Diálogos", "desc": "confirmar, abrir e salvar arquivo — e o teste que responde.", "href": "/docs/desktop/dialogos"}, {"title": "Preferências e tema", "desc": "a pasta certa de cada sistema, e claro/escuro.", "href": "/docs/desktop/preferencias-e-tema"}, {"title": "Testar sem display", "desc": "a Sonda, e o que ela não prova.", "href": "/docs/desktop/testar"}, {"title": "Empacotar", "desc": ".app, .exe e binário.", "href": "/docs/desktop/empacotar"}, {"title": "Uma aplicação inteira", "desc": "estoque com arquivo, menus e teste.", "href": "/docs/desktop/completo"}]},
];

const headings = [{ id: 'o-que-ela-acrescenta-a-janela', text: "O que ela acrescenta à Janela", level: 2 as const }, { id: 'a-forma-o-programa-roda-de-novo', text: "A forma: o programa roda de novo", level: 2 as const }, { id: 'comecar', text: "Começar", level: 2 as const }, { id: 'o-que-ela-nao-e', text: "O que ela NÃO é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Aplicações de mesa"}
      description={"Bigorna: o framework de aplicações de mesa — várias telas, menus com atalhos, diálogos nativos e preferências, em macOS, Windows e Linux, com zero dependência."}
      href={"/docs/desktop"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
