// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Uma aplicação inteira",
  description: "Um controle de estoque com arquivo, tabela, validação e teste — em 70 linhas.",
};

const blocos: Bloco[] = [
  {"p": "Juntando tudo: lê e grava um arquivo, valida a entrada, mostra uma tabela e tem teste que roda sem display."},
  { code: `adopt Arcane.Janela as J
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

action gravar(itens):
    IO.write(ARQUIVO, Ser.to_json(itens))
    yield len(itens)

itens := carregar()

// ── a tela ─────────────────────────────────────────────────
action tela(t):
    t.titulo("Estoque")

    t.grupo("Entrada")
    nome := t.entrada("Produto", "")
    qtd := t.numero("Quantidade", 1, 1, 9999)
    given t.botao("Adicionar", yes):
        given nome is "":
            t.erro("o produto é obrigatório")
        orif nome in [i["nome"] cycle i in itens]:
            t.erro($"'{nome}' já está no estoque")
        otherwise:
            itens.append({"nome": nome, "qtd": qtd})
            gravar(itens)
            t.aviso($"{nome}: {qtd} em estoque")
    t.fim()

    t.separador()
    t.texto($"{len(itens)} produto(s)")
    t.tabela(["nome", "qtd"], itens)

    given len(itens) > 0 and t.botao("Esvaziar"):
        itens.clear()
        gravar(itens)

// ── rodar ou testar ────────────────────────────────────────
s := J.testar(tela)
s.digitar("Produto", "café")
s.digitar("Quantidade", 12)
s.clicar("Adicionar")
assert s.tem("café: 12 em estoque")

// o duplicado é recusado
s.clicar("Adicionar")
assert s.tem("já está no estoque")
assert len(itens) is 1

// e o arquivo foi gravado
assert IO.exists(ARQUIVO)
assert len(Ser.from_json(IO.read(ARQUIVO))) is 1
out s.texto()`, lang: 'df' },
  {"h2": "As decisões que ela carrega"},
  {"table": {"head": ["Decisão", "O que ela evita"], "rows": [["o estado mora **fora** da ação de tela", "ele seria recriado a cada reexecução, e a lista ficaria sempre vazia"], ["gravar a cada mudança", "fechar a janela perder o trabalho — não há `Ctrl-S` aqui"], ["o duplicado é recusado **antes** de gravar", "um arquivo com dois \"café\" e nenhuma forma de saber qual vale"], ["a validação devolve `t.erro`, e não levanta", "um erro que fecha a janela no meio do cadastro"], ["`defer` na pasta temporária", "lixo em disco a cada execução do exemplo"]]}},
  {"h2": "O que falta para virar produção"},
  {"list": ["**Editar e remover** — a tabela é só leitura, e `t.tabela` não tem seleção.", "**Desfazer**, que aqui seria uma pilha do estado anterior.", "**Gravação atômica**: escrever ao lado e renomear, senão um fechamento no meio da gravação deixa o arquivo pela metade.", "**Um banco** em vez de JSON, quando passar de alguns milhares de linhas — `Arcane.Database` está a um `adopt` de distância."]},
];

const headings = [{ id: 'as-decisoes-que-ela-carrega', text: "As decisões que ela carrega", level: 2 as const }, { id: 'o-que-falta-para-virar-producao', text: "O que falta para virar produção", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Uma aplicação inteira"}
      description={"Um controle de estoque com arquivo, tabela, validação e teste — em 70 linhas."}
      href={"/docs/desktop/completo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
