// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar sem display",
  description: "A Sonda usa a aplicação inteira — telas, menus, atalhos, diálogos — sem abrir janela, e por isso roda no CI.",
};

const blocos: Bloco[] = [
  {"p": "Uma biblioteca de interface que só funciona com display é uma biblioteca **sem teste**: o runner do CI não tem display. A separação entre a **árvore** e o **desenho** resolve isso — a Sonda monta a mesma árvore que o Tk desenharia, e por isso ela não simula nada."},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.Crucible as Crucible
adopt Arcane.OS as OS

itens := []
app := B.app("Lista", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")
app.menu("Editar", [B.item("Limpar", "limpar", atalho := "Ctrl+L")])

action tela(t):
    nome := t.entrada("Nome")
    given t.botao("Adicionar"):
        given nome is "":
            t.erro("o nome é obrigatório")
        otherwise:
            itens.append(nome)
    given t.comando("limpar") and t.confirmar("Limpar a lista?"):
        itens.clear()
    t.status($"{len(itens)} item(ns)")

app.tela("t", tela)

crucible "a lista":
    trial "o nome vazio é recusado":
        s := B.testar(app)
        s.clicar("Adicionar")
        expect s.tem("o nome é obrigatório") is yes

    trial "o atalho limpa, depois de confirmar":
        s := B.testar(app)
        s.digitar("Nome", "café")
        s.clicar("Adicionar")
        s.responder(yes)
        s.atalho("Ctrl+L")
        expect len(itens) is 0

Crucible.run()`, lang: 'df' },
  {"h2": "O que a Sonda faz"},
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`s.digitar(rotulo, valor)` · `s.marcar` · `s.escolher`", "preenche um campo e roda a tela"], ["`s.clicar(rotulo)`", "clica — o clique vale para UMA execução"], ["`s.menu(titulo, item)` · `s.atalho(\"Ctrl+N\")`", "o comando, pelo menu ou pelo teclado"], ["`s.selecionar(linha)`", "escolhe a linha de uma tabela selecionável"], ["`s.responder(valor)`", "a resposta do PRÓXIMO diálogo"], ["`s.tela_atual()` · `s.status()` · `s.notificacoes()`", "onde está e o que mostrou"], ["`s.texto()` · `s.tem(texto)` · `s.valor(rotulo)`", "o conteúdo da tela"], ["`s.menus()` · `s.dialogos_pedidos()` · `s.arvore()`", "a estrutura, como dado"]]}},
  {"p": "Um rótulo que não existe lista os que existem — `nao ha botao 'Salvr'` vem com `os botoes sao: Salvar, Cancelar`. É a mesma mensagem da Janela e da Vitrine."},
  {"h2": "O que a Sonda NÃO prova"},
  {"list": ["**O desenho.** Por isso existe `test_a_janela_de_verdade_tem_menu_status_e_navega`, que monta a janela no Tk, aciona o menu **pelo próprio Tk** (`menu.invoke`) e confere os widgets — e que pula onde não há display.", "**A aparência** — fonte, espaçamento, cor. Nenhum teste aqui finge isso.", "**O diálogo nativo** do sistema: a Sonda prova a pergunta e o que a tela faz com a resposta, não o seletor de arquivos do Finder."]},
];

const headings = [{ id: 'o-que-a-sonda-faz', text: "O que a Sonda faz", level: 2 as const }, { id: 'o-que-a-sonda-nao-prova', text: "O que a Sonda NÃO prova", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar sem display"}
      description={"A Sonda usa a aplicação inteira — telas, menus, atalhos, diálogos — sem abrir janela, e por isso roda no CI."}
      href={"/docs/desktop/testar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
