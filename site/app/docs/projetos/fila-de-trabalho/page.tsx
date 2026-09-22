// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Processador de fila",
  description: "Tarefas com retentativa, recuo exponencial e carta morta — sem perder nenhuma.",
};

const blocos: Bloco[] = [
  {"p": "Todo sistema acaba com trabalho que não cabe no pedido: mandar e-mail, gerar PDF, chamar um serviço lento. A fila resolve, e cria três perguntas novas: o que acontece quando a tarefa falha, quantas vezes se tenta, e onde fica a que nunca vai dar certo. Esta página responde as três com um laço que se entende em cinco minutos."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["vault por tarefa", "tentativas, próximo horário e último erro"], ["recuo exponencial", "o serviço que caiu não é martelado"], ["carta morta", "a tarefa impossível sai do caminho sem sumir"], ["`monitor` / `handle`", "a falha de uma não para as outras"]]}},
  {"h2": "Estrutura"},
  { code: `processador/
  src/
    fila.df        enfileirar, proxima, concluir, falhar
    trabalhos.df   o que cada tipo de tarefa faz
    main.df        o laco
  tests/`, lang: 'text' },
  { code: `[project]
name = "processador"
version = "0.1.0"
description = "Fila de trabalho"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `steady MAXIMO := 4

fila := []
mortas := []
feitas := []

action enfileirar(tipo, dados):
    fila.append({"tipo": tipo, "dados": dados, "tentativas": 0, "quando": 0, "erro": ""})

action recuo(tentativa):
    yield 2 ** tentativa

action proxima(agora):
    cycle i in range(0, len(fila)):
        given fila[i]["quando"] smaller_eq agora:
            yield fila.pop(i)
    yield void

// Um servico que falha nas duas primeiras chamadas, e um que nunca volta.
chamadas := {"email": 0}
action trabalhar(t):
    match t["tipo"]:
        point "email":
            chamadas["email"] += 1
            given chamadas["email"] smaller_eq 2:
                trigger "servidor de e-mail indisponivel"
            yield $"enviado para {t['dados']}"
        point "pdf":
            yield $"gerado {t['dados']}.pdf"
        default:
            trigger $"ninguem sabe fazer '{t['tipo']}'"

action rodar_ate(fim):
    agora := 0
    persist agora smaller_eq fim:
        t := proxima(agora)
        given t is void:
            agora += 1
            skip
        monitor:
            feitas.append(trabalhar(t))
        handle Error as e:
            t["tentativas"] += 1
            t["erro"] := e.message
            given t["tentativas"] bigger_eq MAXIMO:
                mortas.append(t)
            otherwise:
                t["quando"] := agora + recuo(t["tentativas"])
                fila.append(t)

enfileirar("email", "ana@exemplo.com")
enfileirar("pdf", "relatorio-setembro")
enfileirar("fax", "1998")
rodar_ate(60)

out $"feitas: {feitas}"
out $"mortas: {mortas >> morph m: m['tipo'] + ' (' + m['erro'] + ')'}"
assert len(feitas) is 2
assert len(mortas) is 1 and mortas[0]["tipo"] is "fax"
assert mortas[0]["tentativas"] is MAXIMO
assert len(fila) is 0`, lang: 'df', title: `src/fila.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/fila as F

crucible "recuo":
    trial "o recuo dobra":
        expect [F.recuo(1), F.recuo(2), F.recuo(3)] is [2, 4, 8]`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o erro fica **na tarefa**", "a carta morta não diz por que morreu"], ["recuo exponencial", "mil tarefas repetindo a cada segundo derrubam de novo o serviço que acabou de voltar"], ["teto de tentativas", "a tarefa impossível roda para sempre e atrasa todas as outras"], ["`handle Error`, não `RuntimeError`", "um `trigger` escapa do `handle` e derruba o laço inteiro"]]}},
  {"h2": "Para ir além"},
  {"list": ["Fila que sobrevive a reinício, com reserva e prazo: `Eventos.fila_persistente` — [Arcane.Eventos](/docs/biblioteca/eventos).", "Acrescente *jitter* ao recuo — [Arcane.Malha](/docs/biblioteca/malha) explica por quê.", "Vários operários: [Concorrência](/docs/tecnicas/concorrencia)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Processador de fila"}
      description={"Tarefas com retentativa, recuo exponencial e carta morta — sem perder nenhuma."}
      href={"/docs/projetos/fila-de-trabalho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
