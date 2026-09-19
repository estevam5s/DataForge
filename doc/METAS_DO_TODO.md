# As metas do `TODO.md`, medidas

O `TODO.md` pede duas coisas grandes: implementar o conteúdo de
`doc/dataforge_completo_avancado_dataforge.md` (87 capítulos, escritos na
forma do Node.js) e o de `bibliotecas.md` (cerca de 100 bibliotecas do
Python e do Node). Atacar "tudo" de uma vez não é um plano — é uma lista.

Este documento é o **mapa**: cada área de capacidade dos dois documentos,
cruzada com o que a linguagem já tem. Ele foi feito medindo — lendo os
símbolos dos 71 módulos, não a memória de quem escreveu.

Atualizado em 2026-09-19, com 71 módulos e 1.873 símbolos.

---

## Já existe

Cada linha foi conferida pelos símbolos do módulo, e não pelo nome dele.

| O documento pede | Onde está |
|---|---|
| fs, path, glob, tempfile, shutil | `Arcane.IO`, `Arcane.OS` |
| streams, web streams | `Arcane.Stream`, `Kiln.sse`/`Kiln.stream` |
| http server e client, REST | `Kiln`, `Arcane.Http`, `Arcane.API` |
| websocket e tempo real | `Kiln.ws`, `Kiln.sala` (RFC 6455 falado à mão) |
| net (TCP), dgram (UDP), dns | `Arcane.Rede` (`udp`, `resolver`) |
| buffer e dados binários, struct | `Arcane.Bytes` |
| process, child_process, subprocess | `Arcane.Process`, `Arcane.OS` |
| worker_threads, cluster, multiprocessing | `Arcane.Concurrent` (`processo`, `pool_processos`, `map_processos`), `travessia.py` |
| queue, concurrent, threading | `Arcane.Concurrent` (mutex, semáforo, barreira, canal) |
| events, pubsub, message broker | `Arcane.Eventos`, `Arcane.Stream` (`topico`, `publicar`) |
| timers | `Arcane.Time`, `Arcane.Concurrent.repetir_a_cada` |
| modules, packages, monorepo | `adopt`/`relay`, `forge.toml`, `dataforge add/publish` |
| crypto, hashlib, hmac, secrets, JWT | `Arcane.Crypto` |
| compression (zlib, gzip) | `Arcane.Archive` |
| url, querystring | `Arcane.Url` |
| test runner, assert, unittest, pytest | `Arcane.Crucible`, `dataforge test`, `expect` |
| debugging, inspector | `dataforge debug`, `dataforge dap` |
| performance, perf_hooks | `Arcane.Bench`, `dataforge profile`, `dataforge big-o` |
| diagnósticos, observabilidade, logging | `Arcane.Observar`, `Arcane.Logging`, `Arcane.Qualidade` |
| errors, graceful shutdown | `monitor`/`handle`/`ensure`/`defer`, `retry`, `guard` |
| database, SQLite, ORM | `Arcane.Database`, `Arcane.Forge` |
| middleware, authentication, authorization | `Kiln` (middleware, `after`, sessão, CSRF) + JWT |
| cache | `Arcane.Vitrine.cache`, `Arcane.Functional.memoize`, `Kiln.cache` |
| microservices, RPC com retry e circuit breaker | `Arcane.Malha` (retry, disjuntor, saga, propagação de rastro) |
| GraphQL (esquema, resolvedor por campo, consulta) | `Arcane.Lavra` — 42 símbolos: esquema, tipo, campo, diretiva, assinatura, introspecção, lote e federação |
| ETL, pipelines, Airflow, PySpark, Dask | `Arcane.Pipeline` (DAG, retry, incremental), `Arcane.Lago`, `Arcane.Analytics`, `parallel` |
| IA, scikit-learn | `Arcane.Cortex`, `train`/`predict` |
| DevOps, cloud, produção | `dataforge devops` (Dockerfile, compose, CI, k8s, Helm, SBOM) |
| CLI, argparse, readline, console | `Arcane.Cli`, `dataforge repl` |
| i18n | `Arcane.Vitrine.i18n`, e `DF_IDIOMA` para as mensagens |
| matemática, decimal, estatística, frações | `Arcane.Math`, `Arcane.Decimal`, `Arcane.Analytics` |
| dataclasses, enum, abc, typing | `record`, `enum`, `abstract`, tipos e `<T extends X>` |
| itertools, functools, operator, collections | `Arcane.Iter`, `Arcane.Functional`, `Arcane.Collections` |
| re, string, textwrap | `Arcane.Regex`, `Arcane.Text` |
| json, csv, pickle, base64 | `Arcane.Serialization`, `Arcane.Data`, `Arcane.Crypto` |
| datetime, zoneinfo, calendar | `Arcane.Time` |
| email, smtplib | `Arcane.Email` |
| BeautifulSoup (parsing HTML) | `Arcane.Html` |
| Matplotlib, Seaborn (gráficos) | `Arcane.Vitrine` (SVG escrito no servidor) |
| numpy, pandas, torch, OpenCV, Pillow | `adopt Python.numpy` — a ponte, sem cópia na fronteira |

## Não existe, e a decisão está tomada

| O documento pede | Por que não |
|---|---|
| HTTP/2, TLS no servidor | o `http.server` do Python não tem, e implementá-los é reescrever um servidor de produção. Em produção pública, nginx ou Caddy na frente — está em `ANALISE_E_ROADMAP.md` |
| gRPC | exige HTTP/2, que a linha acima explica |
| native addons, FFI, C++ embedder API | a promessa é **zero dependência** e um binário por sistema; carregar `.so` do usuário quebra as duas |
| V8, WebAssembly, WASI, VM isolada | um sandbox de verdade não se faz dentro do próprio processo, e prometê-lo é pior que não ter |
| TypeScript | a linguagem tem tipos próprios e analisador próprio |
| punycode, TTY avançado, trace events | cabem, e nenhum programa real esbarrou na falta |

## Não existe, e cabe — em ordem de valor

Medido pelo que um programa real pede primeiro, não pela ordem dos
capítulos. **Cada item traz como conferir que ele ainda falta** — a
revisão à mão é o que fez a versão anterior desta lista envelhecer
inteira: os quatro itens dela estavam feitos.

1. **Exaustividade em padrão aninhado.** O `match` avisa o que fica de
   fora em enum, booleano, sequência e na família de um
   `abstract blueprint`. Ele não desce em padrão aninhado.

       enum Cor: A / B
       match par:
           point [Cor.A, x]:   ← 'Cor.B' fica de fora, e nada avisa

2. **Watchpoint de leitura.** A vigia para quando um valor **muda** (`w
   total`, `--vigiar=expr`, data breakpoint no editor). Parar quando ele
   é só **lido** não existe — e é o que se quer quando a pergunta é
   "quem está consultando isto?".

3. **Cache de compilação.** Os fechamentos são montados a cada processo.
   Num servidor que reinicia, é trabalho repetido a cada partida.

4. **Literal decimal exato.** `19.99` no código é `Float`, com o
   arredondamento binário de sempre; a exatidão exige
   `Dec.de("19.99")`. Um sufixo (`19.99d`) resolveria, e mexe no lexer.

5. **Vínculo genérico carregado pelo objeto.** `Caixa<Integer>` é
   conferido na **fronteira** (a atribuição anotada) e pelo `check`
   quando o literal prova. Uma escrita posterior em campo
   (`c.guardado := valor_de_fora`) não é conferida: o objeto não carrega
   o vínculo, e fazê-lo carregar custa estado por instância — ver
   "custo zero" em `ecossistema/principios`.

6. **Gerenciador de versões, e workspace.** Trocar de versão é
   reinstalar; não há como fixar a versão por projeto nem resolver a
   árvore de vários pacotes de uma vez.

---

## Feito desde a versão anterior desta lista

Os quatro itens que estavam aqui saíram, e é por isso que o documento
ganhou a coluna "como conferir":

| Estava pedindo | Onde está |
|---|---|
| fila de trabalho com persistência | `Arcane.Eventos.fila_persistente` — SQLite, com reserva com prazo, recuo, agendamento e carta morta |
| `Cluster<T>` e `Vault<K, V>` como tipo de parâmetro | existe, conferido na fronteira, na inserção e pelo `check` |
| watchpoint no depurador | `w expr`, `--vigiar=expr`, data breakpoint |
| sessão da Vitrine entre processos | `V.sessoes_em_banco`, `V.sessoes_em_arquivos` |

E fora desta lista, medido na mesma passada: **LSP**, **depurador**,
**cobertura de testes**, **`Mutex`/`Semaphore`/`Atomic`**, **`TaskGroup`
e cancelamento** e **registro hospedado com autenticação** — todos
pedidos em `ANALISE_E_ROADMAP.md` e todos já existentes.

> A lição, e ela vale mais que a lista: **uma lista de "o que falta"
> defasada é a pior espécie de documento envelhecido**, porque é
> justamente a que alguém consulta para decidir no que trabalhar. Quatro
> comandos deste repositório existiam, funcionavam e não apareciam no
> `help` — `login`, `logout`, `whoami` e `palavras` — e um deles fala com
> um serviço de verdade. Hoje há trava:
> `test_todo_comando_DESPACHADO_esta_no_catalogo`.

## Como este documento não envelhece

As duas primeiras tabelas citam **símbolos**, e símbolo que sai da
biblioteca quebra `tests/test_estabilidade.py`. A terceira é a única que
precisa de revisão à mão, e ela é curta de propósito: quatro itens é uma
lista de trabalho, cem é um desabafo.
