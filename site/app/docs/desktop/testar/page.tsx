// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar sem display",
  description: "A Sonda monta a mesma árvore que o Tk desenharia — e por isso ela não simula nada.",
};

const blocos: Bloco[] = [
  {"p": "Uma biblioteca de interface que só funciona com display é uma biblioteca **sem teste**: o runner do CI não tem display. A separação entre a **árvore** e o **desenho** é o que resolve isso — e ela é a mesma decisão da Vitrine."},
  { code: `adopt Arcane.Janela as J
adopt Arcane.Crucible as Crucible

itens := []

action tela(t):
    t.titulo("Lista")
    nome := t.entrada("Nome", "")
    given t.botao("Adicionar"):
        given nome is "":
            t.erro("o nome é obrigatório")
        otherwise:
            itens.append(nome)
    t.texto($"{len(itens)} item(ns)")

crucible "a tela":

    trial "o nome vazio e recusado":
        itens.clear()
        s := J.testar(tela)
        s.clicar("Adicionar")
        expect s.tem("o nome é obrigatório") is yes

    trial "adicionar conta":
        itens.clear()
        s := J.testar(tela)
        s.digitar("Nome", "café")
        s.clicar("Adicionar")
        expect s.tem("1 item(ns)") is yes

Crucible.run()`, lang: 'df' },
  {"h2": "O que a Sonda faz"},
  {"table": {"head": ["Chamada", "O quê"], "rows": [["`s.digitar(rotulo, valor)`", "preenche e **reexecuta** a tela"], ["`s.clicar(rotulo)`", "clica e reexecuta — o clique vale para uma execução"], ["`s.escolher(rotulo, valor)`", "recusa o que não está na lista"], ["`s.marcar(rotulo, yes)`", "a caixa"], ["`s.texto()`", "tudo o que a tela mostra"], ["`s.valor(rotulo)`", "o valor de um campo"], ["`s.campos()`, `s.botoes()`", "o que existe na tela"], ["`s.tabelas()`", "as tabelas, com colunas e linhas"], ["`s.arvore()`", "a árvore inteira como vault — para instantâneo"]]}},
  {"h2": "Um rótulo que não existe lista os que existem"},
  { code: `adopt Arcane.Janela as J

action tela(t):
    t.entrada("Nome")
    t.botao("Salvar")

s := J.testar(tela)

monitor:
    s.digitar("Nomee", "x")
    assert no
handle Error as e:
    out e.message
    out $"  {e.nota}"`, lang: 'df' },
  {"h2": "A árvore é dado"},
  {"p": "Guardá-la num instantâneo faz **qualquer** mudança de tela aparecer no diff do commit — inclusive a que ninguém pretendia:"},
  { code: `adopt Arcane.Janela as J

action tela(t):
    t.titulo("Cadastro")
    t.entrada("Nome")
    t.botao("Salvar")

s := J.testar(tela)
arvore := s.arvore()
assert arvore["especie"] is "raiz"
assert [f["especie"] cycle f in arvore["filhos"]] is ["titulo", "entrada", "botao"]
out arvore["filhos"][1]`, lang: 'df' },
  {"h2": "O que a Sonda NÃO prova"},
  {"list": ["**O desenho.** Se um componente não tiver ramo no desenho, a Sonda passa e a janela não mostra nada.", "**A aparência** — fonte, espaçamento, cor. Nenhum teste aqui finge isso.", "**O comportamento do Tk** — o que acontece ao redimensionar, ao colar texto grande, ao usar leitor de tela.", "Por isso existe `test_a_janela_abre_de_verdade`, que **abre** uma janela e a fecha sozinha — e que pula onde não há display."]},
  {"callout": {"tipo": "nota", "titulo": "`fechar_em` existe por causa do teste", "texto": "Uma janela que só fecha no clique não tem como ser exercitada num CI, e o que não se exercita quebra calado. `J.abrir(app, tela, void, 400)` fecha sozinha em 400 ms."}},
];

const headings = [{ id: 'o-que-a-sonda-faz', text: "O que a Sonda faz", level: 2 as const }, { id: 'um-rotulo-que-nao-existe-lista-os-que-existem', text: "Um rótulo que não existe lista os que existem", level: 2 as const }, { id: 'a-arvore-e-dado', text: "A árvore é dado", level: 2 as const }, { id: 'o-que-a-sonda-nao-prova', text: "O que a Sonda NÃO prova", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar sem display"}
      description={"A Sonda monta a mesma árvore que o Tk desenharia — e por isso ela não simula nada."}
      href={"/docs/desktop/testar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
