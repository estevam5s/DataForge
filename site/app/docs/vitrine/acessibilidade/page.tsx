// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Acessibilidade e idioma",
  description: "O que a Vitrine já faz por quem usa teclado e leitor de tela, e como traduzir a aplicação.",
};

const blocos: Bloco[] = [
  {"h2": "O que vem pronto"},
  {"p": "Nada disto precisa ser ligado. É como os componentes são desenhados."},
  {"table": {"head": ["O quê", "Como"], "rows": [["HTML semântico", "`<main>`, `<aside>`, `<fieldset>`/`<legend>`, `<table>` com `<thead>`"], ["Link para pular a navegação", "o primeiro elemento da página, visível só ao receber foco"], ["Foco sempre visível", "`:focus-visible` com contorno de 2 px, em todo elemento interativo"], ["Rótulo ligado ao campo", "`<label for>` em todos os campos com rótulo"], ["Erro anunciado", "`role=\"alert\"` na mensagem, `aria-invalid` e `aria-describedby` no campo"], ["Abas pelo teclado", "`role=\"tablist\"`, setas ← →, Home e End, e só a ativa no caminho do Tab"], ["Alerta com a urgência certa", "`role=\"alert\"` para erro e aviso, `role=\"status\"` para o resto"], ["Progresso legível", "`role=\"progressbar\"` com `aria-valuenow` e `aria-label`"], ["Movimento respeitado", "`prefers-reduced-motion` desliga as animações"], ["Tema do sistema", "`prefers-color-scheme` escolhe claro ou escuro sozinho"]]}},
  {"callout": {"tipo": "nota", "titulo": "A seta ▲ não diz \"aumento de\"", "texto": "A variação de uma métrica sai com o símbolo marcado `aria-hidden` e a palavra ao lado, visível só para leitor de tela. Cor e seta sozinhas excluem quem não vê a tela **e** quem não separa vermelho de verde — 8% dos homens."}},
  {"p": "A paleta clara usa `#B28600` como primária, e não o amarelo `#FED403` da marca: amarelo sobre branco dá contraste 1,3:1, e a WCAG pede 4,5:1 para texto. O amarelo continua sendo a marca no tema escuro, onde ele funciona."},
  {"h2": "O que fica com você"},
  {"table": {"head": ["O quê", "Como fazer"], "rows": [["Texto alternativo de imagem", "`V.imagem(origem, legenda := \"…\")` — a legenda vira o `alt`"], ["Ordem de leitura", "é a ordem do programa; escreva na ordem em que se lê"], ["Rótulo que descreve", "`V.botao(\"Excluir pedido 42\")` diz mais que `V.botao(\"Excluir\")`"], ["Contraste do seu tema", "se trocar as cores, confira 4,5:1 para texto e 3:1 para borda"], ["`V.html`", "o que você puser ali passa cru, sem nenhuma dessas garantias"]]}},
  {"h2": "Idioma"},
  {"p": "Carregue as chaves e peça o texto. O idioma é **por sessão**: dois visitantes podem estar lendo a mesma página em línguas diferentes, e guardar isso num lugar só faria um trocar o idioma do outro."},
  { code: `V.i18n.carregar("pt-BR", {
    "painel.titulo": "Painel de Vendas",
    "ola": "Olá, {nome}",
    "vazio": "Nenhum resultado."
})
V.i18n.carregar("en-US", {
    "painel.titulo": "Sales Dashboard",
    "ola": "Hello, {nome}",
    "vazio": "No results."
})

action painel():
    V.titulo(V.t("painel.titulo"))
    V.texto(V.t("ola", nome := V.usuario()["nome"]))`, lang: 'df' },
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`V.i18n.carregar(idioma, vault)`", "acrescenta chaves a um idioma"], ["`V.i18n.idioma()`", "o idioma desta sessão"], ["`V.i18n.idioma(\"en-US\")`", "troca, e reexecuta a página"], ["`V.i18n.idiomas()`", "os carregados"], ["`V.i18n.seletor(\"Idioma\")`", "desenha a troca, pronta"], ["`V.t(chave, …)`", "o texto, com `{nome}` substituído"]]}},
  {"callout": {"tipo": "dica", "titulo": "Uma chave sem tradução aparece crua", "texto": "`V.t(\"painel.titulo\")` sem tradução devolve `painel.titulo`, e não vazio. Feio o bastante na tela para alguém corrigir, e informativo o bastante para dizer **qual** chave falta."}},
  {"p": "O seletor troca o idioma e **reexecuta a página**: mudá-lo no meio deixaria a metade de cima na língua anterior."},
  { code: `V.lateral().espaco(8)
V.i18n.seletor("Idioma", {"pt-BR": "Português", "en-US": "English"})`, lang: 'df' },
];

const headings = [{ id: 'o-que-vem-pronto', text: "O que vem pronto", level: 2 as const }, { id: 'o-que-fica-com-voce', text: "O que fica com você", level: 2 as const }, { id: 'idioma', text: "Idioma", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Acessibilidade e idioma"}
      description={"O que a Vitrine já faz por quem usa teclado e leitor de tela, e como traduzir a aplicação."}
      href={"/docs/vitrine/acessibilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
