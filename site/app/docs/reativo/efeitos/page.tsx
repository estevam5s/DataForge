// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Efeitos e propagação",
  description: "O efeito que roda ao nascer, o lote, e o losango que entregava um valor que nunca existiu.",
};

const blocos: Bloco[] = [
  {"h2": "O efeito roda uma vez ao ser criado"},
  { code: `action mostrar():
    linhas.append($"total R$ {total.ler()}")

steady vigia := R.efeito(mostrar)   // ja rodou uma vez

itens.escrever([...])               // roda de novo
vigia.parar()                       // e para de rodar`, lang: 'df' },
  {"p": "Sem isso, quem escreve `R.efeito(…)` vê a tela vazia até a primeira mudança — e conclui que o efeito não funciona. A alternativa seria chamá-lo à mão depois de criar, o que se esquece exatamente uma vez."},
  {"h2": "A propagação tem duas fases"},
  {"p": "Esta é a decisão que mais importa do módulo, e ela veio de um defeito medido. Num **losango** — `c` lê `a` e `b`, e `b` lê `a` — marcar e avisar numa fase só entrega um valor que nunca existiu."},
  { code: `a := R.sinal(1)
b := R.derivado(lambda => a.ler() * 2)
c := R.derivado(lambda => a.ler() + b.ler())

R.efeito(lambda => vistos.append(c.ler()))
a.escrever(5)

// antes:  [3, 7, 15]     <- o 7 nunca foi verdade
// agora:  [3, 15]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Não é uma notificação a mais — é um número errado", "texto": "Com `a = 5`, o valor certo é 15. O 7 era `5 + o b antigo`: `b` ainda estava limpo quando `c` recalculou. E como a lista de dependentes é um conjunto, qual caminho vem primeiro não é escolhido por ninguém — o defeito ia e vinha conforme a ordem de hash, aparecendo e sumindo sozinho na tela."}},
  {"p": "Hoje a marcação percorre o grafo **inteiro** primeiro, e só depois os efeitos e ouvintes rodam. Daí saem três regras:"},
  {"table": {"head": ["Regra", "Sem ela"], "rows": [["o aviso pertence à propagação, e não ao recálculo", "uma simples **leitura** disparava efeito de terceiros"], ["o efeito alcançado por dois caminhos roda **uma** vez", "a tela redesenhava duas vezes por mudança"], ["a dedup é pelo objeto, e não por `id()`", "`id()` só é único entre objetos **vivos**"], ["uma escrita dentro de um efeito abre a **próxima** onda", "a fila cresceria enquanto é percorrida"]]}},
  {"h2": "Lote"},
  { code: `action tres_escritas():
    itens.escrever([...])
    cupom.escrever(0.0)
    itens.escrever([...])

R.lote(tres_escritas)      // UMA notificacao`, lang: 'df' },
  {"p": "Sem ele, mudar três sinais que alimentam o mesmo derivado faz o efeito rodar três vezes — e as duas primeiras mostram um estado intermediário que nunca deveria aparecer na tela."},
  {"callout": {"tipo": "nota", "titulo": "Ele já existiu sem agrupar nada", "texto": "A primeira versão montava uma lista de adiados que **ninguém lia**: o gancho era escrito e nenhum caminho de escrita o consultava. `lote` tinha documentação e tinha teste de que não estourava — e três escritas davam três notificações, exatamente como sem ele. É a mesma forma do `forge.lock` que era escrito e nunca lido."}},
  {"p": "Se a ação falhar no meio, os avisos **saem mesmo assim**: a escrita já aconteceu, e engolir a notificação deixaria a tela mostrando um estado que não é mais o do programa."},
];

const headings = [{ id: 'o-efeito-roda-uma-vez-ao-ser-criado', text: "O efeito roda uma vez ao ser criado", level: 2 as const }, { id: 'a-propagacao-tem-duas-fases', text: "A propagação tem duas fases", level: 2 as const }, { id: 'lote', text: "Lote", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Efeitos e propagação"}
      description={"O efeito que roda ao nascer, o lote, e o losango que entregava um valor que nunca existiu."}
      href={"/docs/reativo/efeitos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
