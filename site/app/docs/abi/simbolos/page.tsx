// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_e_alvos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O mapa de símbolos",
  description: "De onde vem cada nome de um arquivo — o análogo do mapa que um ligador escreve, e a resposta para a pergunta que mais custa num projeto grande.",
};

const blocos: Bloco[] = [
  {"p": "Num projeto de duzentos arquivos, *\"de onde vem este nome?\"* é a pergunta que mais custa a responder à mão. Um ligador escreve isso num **arquivo de mapa**; aqui ele sai do mesmo caminho que o `check` usa para atravessar arquivos."},
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

caminho := $"{OS.temp_dir()}/exemplo-{randint(100000, 999999)}.df"
IO.write(caminho, "adopt Arcane.Math as M\\n\\n" +
                  "action calcular(n):\\n" +
                  "    yield M.sqrt(n) + len(\\"abc\\") + fantasma\\n")

origem := {e["nome"]: e["origem"] cycle e in Abi.mapa(caminho)}

assert origem["M"] is "modulo"              // veio de um adopt
assert origem["len"] is "embutido"          // uma das 228 globais
assert origem["calcular"] is "local"        // declarado neste arquivo
assert origem["fantasma"] is "desconhecido" // NINGUEM prove este nome

IO.delete(caminho)`, lang: 'df' },
  {"table": {"head": ["Origem", "O que quer dizer"], "rows": [["`modulo`", "veio de um `adopt`; `de` traz o módulo e `linha`, a linha do import"], ["`local`", "declarado neste arquivo — ação, record, blueprint, enum ou variável de topo"], ["`embutido`", "uma das 228 funções globais, sem import"], ["`desconhecido`", "**ninguém provê este nome** — é isto que interessa"]]}},
  {"h2": "O nome sem dono"},
  {"p": "A linha `desconhecido` é a que paga o mapa. Um nome que nenhum `adopt`, nenhuma declaração local e nenhum embutido provê é, quase sempre, uma das três coisas: um erro de digitação, um `adopt` que alguém apagou, ou um nome que vem de um arquivo vizinho que este não importa."},
  {"p": "O [`check` já acusa](/docs/tecnicas/analise-estatica) o nome indefinido quando consegue provar. O mapa é a outra metade: ele **lista tudo**, com a origem de cada um, e serve para revisar um arquivo inteiro de uma vez em vez de esperar o analisador tropeçar."},
  {"callout": {"tipo": "nota", "titulo": "Por que isto é o análogo de um mapa de ligador", "texto": "Um ligador resolve símbolos entre objetos e escreve onde cada um foi parar. Aqui não há relocação nem seção — mas a **resolução de símbolo** existe igual: `resolucao.py` decide onde mora o módulo de um `adopt`, e é a única cópia dessa regra no repositório. O mapa é o relatório dela."}},
];

const headings = [{ id: 'o-nome-sem-dono', text: "O nome sem dono", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O mapa de símbolos"}
      description={"De onde vem cada nome de um arquivo — o análogo do mapa que um ligador escreve, e a resposta para a pergunta que mais custa num projeto grande."}
      href={"/docs/abi/simbolos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
