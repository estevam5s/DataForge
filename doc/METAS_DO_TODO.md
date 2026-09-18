# As metas do `TODO.md`, medidas

O `TODO.md` pede duas coisas grandes: implementar o conteúdo de
`doc/dataforge_completo_avancado_dataforge.md` (87 capítulos, escritos na
forma do Node.js) e o de `bibliotecas.md` (cerca de 100 bibliotecas do
Python e do Node). Atacar "tudo" de uma vez não é um plano — é uma lista.

Este documento é o **mapa**: cada área de capacidade dos dois documentos,
cruzada com o que a linguagem já tem. Ele foi feito medindo — lendo os
símbolos dos 56 módulos, não a memória de quem escreveu.

Atualizado em 2026-09-17, com 56 módulos e 1.539 símbolos.

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
capítulos:

1. **Fila de trabalho com persistência** (capítulo 47). `Arcane.Eventos`
   tem fila em memória; o que falta é a que sobrevive ao processo morrer,
   com tentativa, atraso e carta morta. É a peça que todo sistema com
   e-mail ou relatório precisa.
2. **`Cluster<T>` e `Vault<K, V>`** como tipo de parâmetro. `<T>` e
   `<T extends X>` existem; o tipo do **conteúdo** de uma coleção, não —
   e hoje a linguagem ao menos **diz isso**: `xs: Cluster<Integer>`
   responde que a forma não existe e o que escrever no lugar, em vez de
   um erro de sintaxe cru.
3. ~~**Watchpoint no depurador**~~ — **feito**: `w expr` no terminal,
   `dataforge debug --vigiar=expr`, e data breakpoint no editor. Para
   quando o valor muda, inclusive por mutação no lugar e dentro de método.
4. ~~**Sessão da Vitrine compartilhada entre processos**~~ — **feito**:
   `sessoes_em := V.sessoes_em_banco(…)`, `V.sessoes_em_arquivos(…)` ou um
   blueprint com `carregar`/`gravar`/`apagar`.

---

## Como este documento não envelhece

As duas primeiras tabelas citam **símbolos**, e símbolo que sai da
biblioteca quebra `tests/test_estabilidade.py`. A terceira é a única que
precisa de revisão à mão, e ela é curta de propósito: quatro itens é uma
lista de trabalho, cem é um desabafo.
