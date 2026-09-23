// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Aplicações de mesa",
  description: "Uma janela nativa em macOS, Windows e Linux — com zero dependência, e testável sem display.",
};

const blocos: Bloco[] = [
  {"p": "O Tk vem **na biblioteca padrão do Python**, e é a única forma de desenhar uma janela nativa nos três sistemas sem trazer nada de fora. Qt, GTK e wx dariam mais controle e quebrariam a única promessa inegociável do projeto."},
  { code: `adopt Arcane.Janela as J

action tela(t):
    t.titulo("Cadastro")
    nome := t.entrada("Nome", "")
    given t.botao("Salvar"):
        t.aviso($"salvo: {nome}")

// Com display, abre a janela. Sem, a Sonda exercita a MESMA tela.
given J.tem_display():
    out "aqui eu abriria: J.abrir(J.app(\\"Cadastro\\"), tela)"
otherwise:
    out "sem display — e a tela continua testável"

s := J.testar(tela)
s.digitar("Nome", "café")
s.clicar("Salvar")
assert s.tem("salvo: café")
out s.texto()`, lang: 'df' },
  {"h2": "A forma é a da Vitrine"},
  {"p": "E isso não é coincidência: **o programa inteiro roda de novo a cada interação**, e o estado sobrevive. É o que dispensa callback, diffing e a pergunta \"onde fica o estado\" — e é o que torna uma tela testável."},
  {"table": {"head": ["", "Callback (Tk cru, Qt)", "Reexecução (aqui, e na Vitrine)"], "rows": [["onde mora o estado", "espalhado em widgets", "no vault da aplicação"], ["ler um campo", "`entry.get()`", "`nome := t.entrada(\"Nome\")` — a própria chamada"], ["redesenhar", "você lembra de fazer", "acontece"], ["testar", "precisa de display e de robô", "`J.testar(tela)`"], ["o custo", "—", "a tela roda inteira a cada clique"]]}},
  {"h2": "Começar"},
  { code: `$ dataforge desktop novo caixa
$ cd caixa
$ dataforge test                     # a tela, sem abrir janela
$ dataforge desktop rodar src/main.df`, lang: 'bash' },
  {"p": "O esqueleto separa `src/tela.df` de `src/main.df`, e a razão é a mesma do Kiln (`server` monta, `ignite` sobe): um teste que importasse o módulo da tela **abriria a janela e nunca terminaria**."},
  {"h2": "O que ela NÃO é"},
  {"list": ["Não há animação, tema por componente, arrastar-e-soltar nem gráfico interativo.", "Para painel de dados existe a **Vitrine**, que roda no navegador e desenha 27 tipos de gráfico.", "Esta peça é para a ferramenta interna de mesa — a que lê um arquivo, mostra uma tabela, tem quatro botões, e precisa rodar numa máquina sem navegador."]},
  {"cards": [{"title": "Os componentes", "desc": "o que dá para pôr na tela, e o que cada um devolve.", "href": "/docs/desktop/componentes"}, {"title": "Testar sem display", "desc": "a Sonda, e por que ela não simula nada.", "href": "/docs/desktop/testar"}, {"title": "Empacotar", "desc": ".app, .exe e binário — e o que o PyInstaller cobra.", "href": "/docs/desktop/empacotar"}, {"title": "Android", "desc": "o que funciona, e o APK que não existe.", "href": "/docs/mobile"}]},
];

const headings = [{ id: 'a-forma-e-a-da-vitrine', text: "A forma é a da Vitrine", level: 2 as const }, { id: 'comecar', text: "Começar", level: 2 as const }, { id: 'o-que-ela-nao-e', text: "O que ela NÃO é", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Aplicações de mesa"}
      description={"Uma janela nativa em macOS, Windows e Linux — com zero dependência, e testável sem display."}
      href={"/docs/desktop"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
