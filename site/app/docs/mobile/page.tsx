// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/mobile.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Aplicativos móveis",
  description: "Brasa: o framework de aplicativos para o celular — abas, lista tocável, compartilhar, localização e o PWA que o Android e o iPhone instalam, testável sem navegador.",
};

const blocos: Bloco[] = [
  {"p": "A **Brasa** transforma um programa DataForge num aplicativo que o **Android e o iPhone instalam na tela inicial**, abrem em tela cheia, sem barra de endereço, e usam sem conexão. Por baixo é a [Vitrine](/docs/vitrine): o programa roda no servidor, de cima para baixo, e o estado sobrevive por sessão. A Brasa acrescenta o que faz uma página virar aplicativo."},
  { code: `adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

produtos := [{"id": 1, "nome": "café", "qtd": 12},
             {"id": 2, "nome": "açúcar", "qtd": 3}]

app := Br.app("Estoque", cor := "#E8453C")

action inicio():
    Br.topo("Produtos")
    Br.lista(produtos, titulo := "nome", detalhe := "qtd",
             destino := "/produto?id={id}")

action produto():
    id := int(V.parametro("id", "0"))
    p := [x cycle x in produtos given x["id"] is id][0]
    Br.topo(p["nome"], voltar := yes)
    V.metrica("Em estoque", p["qtd"])
    Br.compartilhar($"{p["nome"]}: {p["qtd"]} em estoque")

Br.tela("/", inicio, titulo := "Estoque", icone := "carrinho", aba := yes)
Br.tela("/produto", produto)

// Br.rodar(app) sobe na rede local. Aqui, a Sonda toca sem navegador.
s := Br.testar(app)
s.tocar("açúcar")
assert s.titulo() is "açúcar"
s.voltar()
assert s.titulo() is "Produtos"
out s.itens()`, lang: 'df' },
  {"h2": "O que ela é"},
  {"table": {"head": ["Peça", "Como se escreve", "Página"], "rows": [["barra de abas embaixo", "`Br.tela(\"/\", inicio, aba := yes, icone := \"casa\")`", "[Telas e navegação](/docs/mobile/telas-e-navegacao)"], ["topo com voltar", "`Br.topo(\"Produto\", voltar := yes)`", "[Telas e navegação](/docs/mobile/telas-e-navegacao)"], ["lista tocável", "`Br.lista(itens, destino := \"/p?id={id}\")`", "[Componentes](/docs/mobile/componentes)"], ["botão flutuante, estado vazio", "`Br.botao_flutuante(\"Novo\", \"/novo\")` · `Br.vazio(...)`", "[Componentes](/docs/mobile/componentes)"], ["recursos do aparelho", "`Br.compartilhar` · `Br.ligar` · `Br.mapa` · `Br.localizacao`", "[O aparelho](/docs/mobile/aparelho)"], ["o aplicativo instalável", "manifesto, service worker e ícones — gerados", "[PWA e publicação](/docs/mobile/pwa)"], ["testar", "`Br.testar(app)` · `Br.conferir_pwa(app)`", "[Testar](/docs/mobile/testar)"]]}},
  {"p": "E todo componente da Vitrine continua valendo dentro de uma tela: `V.entrada`, `V.botao`, `V.metrica`, `V.grafico`, `V.camera`… O CSS da Brasa os ajusta ao dedo — botão com 44 px de altura, campo com fonte de 16 px (abaixo disso o iPhone dá zoom ao tocar)."},
  {"h2": "Começar"},
  { code: `$ dataforge mobile novo tarefas
$ cd tarefas
$ dataforge test                     # as telas sem navegador, e o PWA conferido
$ dataforge mobile rodar src/main.df
  Tarefas no ar
  neste computador:  http://localhost:8600
  no celular:        http://192.168.0.12:8600   (mesma rede Wi-Fi)`, lang: 'bash' },
  {"p": "Abra o endereço do celular no navegador dele: o aplicativo funciona na hora. Para **instalar** na tela inicial, o endereço precisa ser HTTPS — ver [PWA e publicação](/docs/mobile/pwa)."},
  {"callout": {"tipo": "atencao", "titulo": "Não há APK", "texto": "O que a Brasa entrega é um PWA: uma página que o sistema instala como aplicativo. Empacotar o interpretador num APK exigiria python-for-android ou Chaquopy, e as duas trazem a cadeia de dependências que a linguagem não tem. O que existe e o que não existe está em [Limites](/docs/mobile/limites)."}},
  {"cards": [{"title": "Telas e navegação", "desc": "abas, topo, voltar e parâmetros.", "href": "/docs/mobile/telas-e-navegacao"}, {"title": "Componentes", "desc": "lista, vazio, seção e botão flutuante.", "href": "/docs/mobile/componentes"}, {"title": "O aparelho", "desc": "compartilhar, ligar, mapa e localização.", "href": "/docs/mobile/aparelho"}, {"title": "Testar", "desc": "a Sonda, e o PWA conferido servindo.", "href": "/docs/mobile/testar"}, {"title": "PWA e publicação", "desc": "instalar exige HTTPS — as formas que funcionam.", "href": "/docs/mobile/pwa"}, {"title": "Limites", "desc": "o que não existe, e a decisão.", "href": "/docs/mobile/limites"}]},
];

const headings = [{ id: 'o-que-ela-e', text: "O que ela é", level: 2 as const }, { id: 'comecar', text: "Começar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Aplicativos móveis"}
      description={"Brasa: o framework de aplicativos para o celular — abas, lista tocável, compartilhar, localização e o PWA que o Android e o iPhone instalam, testável sem navegador."}
      href={"/docs/mobile"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
