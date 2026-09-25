// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Uma regra, três plataformas",
  description: "A mesma regra de negócio na web (Vitrine), na mesa (Bigorna) e no celular (Brasa) — escrita uma vez, testada uma vez.",
};

const blocos: Bloco[] = [
  {"p": "Os três frameworks de interface do DataForge têm a **mesma forma** — o programa da tela roda de cima para baixo, de novo a cada interação — e isso não é coincidência: é o que deixa a regra de negócio morar num módulo **sem interface nenhuma**, usado igual pelos três."},
  {"table": {"head": ["", "Vitrine", "Bigorna", "Brasa"], "rows": [["onde roda", "navegador", "janela nativa (Tk)", "celular (PWA)"], ["para", "painel e aplicação de dados", "ferramenta de mesa", "aplicativo no bolso"], ["navegação", "páginas", "telas, menus e atalhos", "abas e voltar"], ["testar", "`V.testar`", "`B.testar`", "`Br.testar`"], ["distribuir", "servidor", "`.app`, `.exe`, binário", "PWA por HTTPS"]]}},
  {"h2": "A regra, uma vez"},
  { code: `// estoque.df — nenhum adopt de interface aqui dentro.
record Produto:
    nome: String
    qtd: Integer

action baixar(p: Produto, quanto: Integer) -> Produto:
    given quanto bigger p.qtd:
        trigger $"só há {p.qtd} de {p.nome}"
    yield p with {"qtd": p.qtd - quanto}

action resumo(itens) -> String:
    yield $"{len(itens)} produto(s), {sum([i.qtd cycle i in itens])} unidades"

p := baixar(Produto("café", 12), 2)
assert p.qtd is 10
assert resumo([p]) is "1 produto(s), 10 unidades"
out "a regra não sabe onde vai aparecer"`, lang: 'df' },
  {"h2": "As três telas"},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V
adopt Arcane.OS as OS

record Produto:
    nome: String
    qtd: Integer

action resumo(itens) -> String:
    yield $"{len(itens)} produto(s), {sum([i.qtd cycle i in itens])} unidades"

estoque := [Produto("café", 12), Produto("açúcar", 3)]

// ── na mesa ──
mesa := B.app("Estoque", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")
action tela_mesa(t):
    t.titulo("Estoque")
    t.tabela(["nome", "qtd"], [{"nome": p.nome, "qtd": p.qtd} cycle p in estoque])
    t.status(resumo(estoque))
mesa.tela("inicio", tela_mesa)

// ── no celular ──
celular := Br.app("Estoque")
action tela_celular():
    Br.topo("Estoque")
    Br.lista(estoque, titulo := "nome", detalhe := "qtd")
    V.texto(resumo(estoque))
Br.tela("/", tela_celular)

// ── as duas, testadas contra a MESMA regra ──
assert B.testar(mesa).status() is "2 produto(s), 15 unidades"
assert Br.testar(celular).tem("2 produto(s), 15 unidades")
out "uma regra, duas telas, o mesmo resultado"`, lang: 'df' },
  {"p": "Num projeto de verdade, a regra fica em `src/estoque.df` e cada interface a adota com `adopt ./estoque as E`. Um teste da regra não abre janela nem sobe servidor — e é ele que pega o erro de negócio, antes de qualquer tela."},
  {"cards": [{"title": "Vitrine", "desc": "painéis e aplicações de dados no navegador.", "href": "/docs/vitrine"}, {"title": "Bigorna", "desc": "aplicações de mesa nativas.", "href": "/docs/desktop"}, {"title": "Brasa", "desc": "aplicativos para o celular.", "href": "/docs/mobile"}]},
];

const headings = [{ id: 'a-regra-uma-vez', text: "A regra, uma vez", level: 2 as const }, { id: 'as-tres-telas', text: "As três telas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Uma regra, três plataformas"}
      description={"A mesma regra de negócio na web (Vitrine), na mesa (Bigorna) e no celular (Brasa) — escrita uma vez, testada uma vez."}
      href={"/docs/multiplataforma"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
