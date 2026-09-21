// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/telegram.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Teclados e formatação",
  description: "Botões embutidos, o teclado do celular, e o escape de MarkdownV2 que salva a mensagem inteira.",
};

const blocos: Bloco[] = [
  {"h2": "Botões embutidos"},
  { code: `ctx.responder("Confirma?", teclado := Tg.botoes([
    [Tg.botao("Sim", dados := "ok"), Tg.botao("Nao", dados := "cancelar")],
    [Tg.botao("Ver no site", url := "https://exemplo.dev")]
]))`, lang: 'df' },
  {"p": "O `dados` volta em `ctx.dados` quando alguém clica. `dados` e `url` no mesmo botão é um erro do Telegram — e ele recusa o teclado **inteiro** sem dizer qual botão é o culpado, então é melhor descobrir na chamada."},
  {"callout": {"tipo": "atencao", "titulo": "O `dados` tem 64 BYTES, não 64 caracteres", "texto": "O limite é do protocolo e conta bytes: um texto com acento estoura antes do que parece. Guarde o valor no estado do chat e mande só uma chave curta."}},
  {"h2": "O teclado do celular"},
  { code: `ctx.responder("Escolha:", teclado := Tg.teclado([
    ["Consultar saldo", "Extrato"],
    ["Falar com alguem"]
], dica := "toque numa opcao"))

// e para tirar:
ctx.responder("Pronto.", teclado := Tg.remover_teclado())`, lang: 'df' },
  {"h2": "O escape que salva a mensagem"},
  {"p": "O MarkdownV2 do Telegram exige escapar dezoito caracteres, e a lista inclui o **ponto** e o **hífen** — ou seja, um preço e uma data. Um caractere sem escape faz o Telegram recusar a mensagem **inteira** com 400, e o texto que quebra costuma ser justamente o que veio do usuário: funciona em teste e falha em produção, com o nome de alguém."},
  { code: `// errado: o '.' e o '-' derrubam a mensagem
ctx.responder("Total: R$ 1.099,90 - hoje", marcacao := "MarkdownV2")

// certo:
ctx.responder(Tg.escapar("Total: R$ 1.099,90 - hoje"),
              marcacao := "MarkdownV2")`, lang: 'df' },
  {"table": {"head": ["Função", "Sai como"], "rows": [["`Tg.escapar(t)`", "o texto com os dezoito reservados escapados"], ["`Tg.negrito(t)`", "`*texto*` — já escapado por dentro"], ["`Tg.italico(t)` · `Tg.riscado(t)` · `Tg.spoiler(t)`", "as outras ênfases"], ["`Tg.codigo(t)`", "código em linha; só a crase é escapada"], ["`Tg.bloco(t, lang)`", "bloco de código com linguagem"], ["`Tg.link(t, url)` · `Tg.mencao(t, id)`", "link, e menção a uma pessoa"], ["`Tg.escapar_html(t)`", "para a marcação HTML, que exige só três trocas"]]}},
  {"p": "O `escapar_html` troca o `&` **primeiro**: na ordem contrária, `<` viraria `&amp;lt;` — o escape do escape."},
];

const headings = [{ id: 'botoes-embutidos', text: "Botões embutidos", level: 2 as const }, { id: 'o-teclado-do-celular', text: "O teclado do celular", level: 2 as const }, { id: 'o-escape-que-salva-a-mensagem', text: "O escape que salva a mensagem", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Teclados e formatação"}
      description={"Botões embutidos, o teclado do celular, e o escape de MarkdownV2 que salva a mensagem inteira."}
      href={"/docs/telegram/teclados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
