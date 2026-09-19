// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_e_alvos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Onde este programa roda",
  description: "Seis alvos descritos, com o que cada um suporta e por que não suporta o resto — lido dos adopt, e honesto sobre o que isso não prova.",
};

const blocos: Bloco[] = [
  {"p": "*Este programa roda no navegador? numa função serverless? num WASI?* É uma pergunta real e ela aparece cedo — e a resposta dependia de alguém conhecer de cor o que cada ambiente suporta, e de lembrar, para cada `adopt`, se aquele módulo abre soquete, processo ou arquivo."},
  { code: `dataforge alvo app.df                      # a tabela de todos
dataforge alvo app.df --alvo=navegador     # um so, e sai com 3 se nao roda
dataforge alvo app.df --json               # como dado`, lang: 'bash' },
  { code: `adopt Arcane.Alvo as Alvo

assert sorted(keys(Alvo.alvos())) is
       ["cli", "embarcado", "funcao", "navegador", "servidor", "wasi"]

// o servidor suporta tudo
assert Alvo.alvos()["servidor"]["nao_suporta"] is []`, lang: 'df' },
  {"h2": "Os seis alvos"},
  {"table": {"head": ["Alvo", "O que é", "Não tem"], "rows": [["`servidor`", "máquina com sistema operacional completo — onde o DataForge foi feito para rodar", "—"], ["`cli`", "programa de linha de comando na máquina do usuário", "—"], ["`navegador`", "o CPython compilado para WebAssembly (Pyodide) dentro de uma aba", "arquivos, rede, processo, banco, threads, nativo, ambiente"], ["`wasi`", "WebAssembly **fora** do navegador, com a interface de sistema do WASI", "rede, processo, banco, threads, nativo"], ["`funcao`", "serverless: processo efêmero, disco só de leitura fora de `/tmp`", "processo, threads, nativo"], ["`embarcado`", "microcontrolador com MicroPython — memória em kilobytes", "quase tudo"]]}},
  {"p": "E cada ausência vem com **o motivo**, não só com um `não`:"},
  { code: `adopt Arcane.Alvo as Alvo

porque := Alvo.porque("navegador", "threads")
assert "SharedArrayBuffer" in porque

assert "soquete cru" in Alvo.porque("navegador", "rede")
assert Alvo.porque("servidor", "rede") is ""     // ele tem`, lang: 'df' },
  {"h2": "O mesmo vocabulário da capacidade"},
  {"p": "As capacidades são as de [`Arcane.Capacidade`](/docs/seguranca/capacidade): `arquivos`, `rede`, `processo`, `banco`, `threads`, `nativo`, `python`, `ambiente`."},
  {"p": "Lá elas são **cobradas em execução**; aqui são **lidas antes de rodar**, e o alvo é quem diz quais existem. É a mesma pergunta feita de dois lados — e usar dois vocabulários faria as duas respostas divergirem no primeiro módulo novo."},
  { code: `adopt Arcane.Alvo as Alvo
adopt Arcane.Capacidade as Cap

// os dois falam a mesma lingua
assert Cap.exige("Arcane.Process") is "processo"
assert "processo" in Alvo.alvos()["navegador"]["nao_suporta"]`, lang: 'df' },
  {"h2": "O que esta leitura NÃO prova"},
  {"callout": {"tipo": "atencao", "titulo": "É estática, e sai dos `adopt` de um arquivo", "texto": "Um `roda` aqui quer dizer **\"não achei impedimento por esta via\"**, e não \"vai funcionar\". O módulo devolve esta lista em execução, com `Alvo.limites()`, para quem for ler pelo código e não pela documentação."}},
  {"table": {"head": ["Limite", "Consequência"], "rows": [["a leitura é de **um arquivo**", "um módulo alcançado indiretamente — uma biblioteca do projeto que adota `Arcane.Process` — não aparece"], ["`adopt Python.x` conta como `python` e para aí", "o que aquele pacote faz por dentro, ninguém lê"], ["não executa nada", "memória, tempo e dependência nativa do Python continuam sendo problema de quem publica"]]}},
  {"p": "Dito isso, o que ela dá é o que vale: **a lista dos pontos que certamente não rodam, com a linha**. Isso responde a pergunta em dois segundos, e o resto continua sendo trabalho de quem publica."},
];

const headings = [{ id: 'os-seis-alvos', text: "Os seis alvos", level: 2 as const }, { id: 'o-mesmo-vocabulario-da-capacidade', text: "O mesmo vocabulário da capacidade", level: 2 as const }, { id: 'o-que-esta-leitura-nao-prova', text: "O que esta leitura NÃO prova", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Onde este programa roda"}
      description={"Seis alvos descritos, com o que cada um suporta e por que não suporta o resto — lido dos adopt, e honesto sobre o que isso não prova."}
      href={"/docs/alvos/portabilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
