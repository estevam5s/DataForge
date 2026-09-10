# -*- coding: utf-8 -*-
"""Streaming, observabilidade e Docker."""

PAGINAS = [
{
"href": "/docs/tecnicas/streaming",
"title": "Streaming",
"description": "Tópicos, partições e offsets — um log em disco, com a semântica do Kafka.",
"blocos": [
 {"code": """adopt Arcane.Stream as S

corrente := S.corrente("eventos/")
S.topico(corrente, "pedidos", 4)

S.publicar(corrente, "pedidos", {"id": 1, "valor": 90}, "cliente-7")

cycle e in S.consumir(corrente, "pedidos", "faturamento"):
    processar(e["valor"])
    S.confirmar(corrente, "pedidos", "faturamento", e)""", "lang": "df"},
 {"p": "Kafka é um cluster: réplicas, eleição de líder, coordenação entre máquinas. `Arcane.Stream` é um **log em arquivo** com a mesma semântica de tópico, partição e offset — o que cabe num processo, e que é onde a maioria dos fluxos de verdade começa."},

 {"h2": "Um log, não uma fila"},
 {"p": "É a diferença que define o módulo. A fila **entrega e esquece**; o log **guarda**, e cada consumidor lembra onde parou."},
 {"code": """faturamento := S.consumir(corrente, "pedidos", "faturamento")   // 12
auditoria   := S.consumir(corrente, "pedidos", "auditoria")     // 12

S.confirmar_ate(corrente, "pedidos", "faturamento", faturamento)

S.consumir(corrente, "pedidos", "faturamento")   // 0  — já processou
S.consumir(corrente, "pedidos", "auditoria")     // 12 — não mexeu""", "lang": "df"},
 {"p": "Dois grupos leem o **mesmo** evento sem disputar. Numa fila, o primeiro a ler tira o evento do outro."},
 {"callout": {"tipo": "atencao", "titulo": "`consumir` não avança sozinho", "texto": "Quem avança é `confirmar`, **depois** de processar. Avançar na leitura daria *no máximo uma vez*: um processo que cai no meio perderia o evento em silêncio — o pior resultado possível num fluxo de dados. A garantia aqui é *ao menos uma vez*, e é a honesta."}},

 {"h2": "A partição é a unidade de ordem"},
 {"code": """S.publicar(corrente, "pedidos", evento, "cliente-7")""", "lang": "df"},
 {"p": "Eventos com a **mesma chave** caem sempre na mesma partição, e ali a ordem é garantida — os três eventos do cliente 7 chegam na ordem em que aconteceram."},
 {"p": "Entre partições não há ordem, e é justamente isso que permite processar quatro em paralelo. Quem quer ordem total usa uma partição só, e paga com a serialização."},
 {"callout": {"tipo": "nota", "titulo": "A partição é estável entre execuções", "texto": "O `hash()` do Python é aleatorizado por processo desde a 3.3. Usá-lo mandaria a mesma chave para partições diferentes a cada execução, e a única garantia que a partição dá — a ordem por chave — deixaria de existir. Aqui é SHA-256."}},

 {"h2": "Voltar e reprocessar"},
 {"code": """S.voltar(corrente, "pedidos", "faturamento", 0)""", "lang": "df"},
 {"p": "É o que uma fila **não permite**, e o motivo de o log guardar o evento depois de entregue: quando a regra de processamento estava errada — e vai estar — dá para rodar tudo de novo."},

 {"h2": "O atraso é a métrica que se vigia"},
 {"code": """S.atraso(corrente, "pedidos", "faturamento")
// {"total": 40213, "por_particao": {"p0": 12000, "p1": 9800, …}}""", "lang": "df"},
 {"p": "Um atraso que só cresce significa que a produção passou o consumo — e o momento de agir é **antes** de o disco encher, não depois."},

 {"h2": "Retenção"},
 {"code": """S.reter(corrente, "pedidos", 10)     // guarda os 10 últimos segmentos""", "lang": "df"},
 {"p": "Um log que só cresce enche o disco. A retenção apaga por **segmento**, não por evento: apagar o meio de um arquivo exigiria reescrevê-lo inteiro, e o offset dos que sobram mudaria — quebrando a posição de todo grupo."},

 {"h2": "Janelas"},
 {"code": """cycle j in S.janela(eventos, 60):
    out $"{j["inicio"]}: {j["quantos"]} eventos\"""", "lang": "df"},
 {"p": "É a operação que dá sentido a um fluxo: *quantos por minuto* é a pergunta que se faz, e ela não existe sem janela."},

 {"h2": "O que ele não faz"},
 {"list": [
   "**Sem réplica.** O log vive num disco só.",
   "**Sem transação entre tópicos.** Publicar em dois é duas operações.",
   "**Sem coordenação automática** entre consumidores de um mesmo grupo — cada processo lê as partições que você mandar.",
   "**A garantia é *ao menos uma vez*.** Um processo que cai entre processar e confirmar reprocessa o evento; *exatamente uma vez* exige transação de ponta a ponta, e ninguém a tem de graça."]},
]},

{
"href": "/docs/tecnicas/observar",
"title": "Observabilidade e linhagem",
"description": "As sete perguntas, métricas com percentil, tracing aninhado e de onde veio cada número.",
"blocos": [
 {"p": "Observabilidade é conseguir responder, **sem abrir o código**:"},
 {"list": ["executou?", "quanto tempo demorou?", "quantos registros processou?",
           "quantos falharam?", "qual etapa falhou?", "quando?", "qual versão estava rodando?"]},
 {"p": "Log sozinho responde a primeira e a sexta. As outras cinco exigem **número** — e é isso que separa observabilidade de logging."},

 {"h2": "O painel"},
 {"code": """adopt Arcane.Observar as O

p := O.painel("etl-vendas", "2.1.0")

O.contar(p, "linhas_lidas", 40000)      // só sobe
O.medir(p, "latencia_ms", 12.4)         // guarda a distribuição
O.marcar(p, "versao_do_esquema", 7)     // o último vale

out O.relatorio(p)""", "lang": "df"},

 {"h2": "A média esconde"},
 {"code": """  medida                         p50       p95       p99       máx
  latencia_ms                  2.000     2.000    40.000    40.000""", "lang": "text"},
 {"p": "Um pipeline com média de 3,9s e **p99 de 40s** tem um problema que a média nunca mostra — e é o p99 que o usuário sente. `medir` guarda a distribuição e devolve p50, p95 e p99."},
 {"callout": {"tipo": "nota", "titulo": "Amostragem por reservatório", "texto": "O percentil exato exige a lista inteira, e uma lista sem teto vira vazamento de memória num processo longo. Dez mil amostras dão p99 com erro menor que 1% — e o reservatório garante que cada valor tenha a **mesma** chance de ficar, independente de quando chegou. Guardar só os primeiros mil daria o percentil do começo da execução."}},
 {"p": "O cálculo é interpolação linear — a mesma de `numpy.percentile`. Não é detalhe: um p99 calculado de outro jeito daria um número diferente do painel que a equipe já olha, e ninguém saberia qual acreditar."},

 {"h2": "Tracing: onde o tempo foi"},
 {"code": """extrair := O.abrir(p, "extrair")
// …
O.fechar(p, extrair)

transformar := O.abrir(p, "transformar")
limpar := O.abrir(p, "limpar", transformar)      // aninhado
O.fechar(p, limpar)
O.fechar(p, transformar)""", "lang": "df"},
 {"code": """    transformar                 0.048s  60.3% ██████████████
      enriquecer                  0.035s  44.4% ██████████
      limpar                      0.013s  15.9% ███
    extrair                     0.025s  31.7% ███████
  ✗ carregar                    0.006s   8.0% █""", "lang": "text"},
 {"p": "*carregar levou 40s* não ajuda. *Dos 40s, 38 foram no INSERT* resolve — e é o aninhamento que mostra isso."},
 {"h3": "A forma que não deixa trecho aberto"},
 {"code": """O.cronometrar(p, "carregar", lambda => carregar(dados))""", "lang": "df"},
 {"p": "Mesmo quando a ação estoura, o trecho é fechado — marcado como falha, e com a mensagem. E `resumo` **avisa** se sobrou trecho aberto no fim, que é quase sempre um `ensure` que faltou."},

 {"h2": "Linhagem: de onde veio esse número"},
 {"code": """O.derivar(p, "vendas_bruto",  ["api_erp"], "extração diária")
O.derivar(p, "vendas_prata",  ["vendas_bruto"], "limpeza e deduplicação")
O.derivar(p, "painel_diario", ["vendas_prata", "metas"], "agregação por dia")""", "lang": "df"},
 {"p": "Quando um número no painel está errado, a pergunta não é *onde está o bug*: é **de onde veio esse número**. Sem linhagem registrada, a resposta sai de ler o código de trás para a frente — e o código mudou desde que aquele número foi calculado."},
 {"code": """O.origem(p, "painel_diario")
//   vendas_prata → painel_diario   (agregação por dia)
//   metas        → painel_diario   (agregação por dia)
//   vendas_bruto → vendas_prata    (limpeza e deduplicação)
//   api_erp      → vendas_bruto    (extração diária)""", "lang": "df"},
 {"h3": "E a pergunta inversa, que é a mais cara"},
 {"code": """O.impacto(p, "vendas_bruto")
// ["vendas_prata", "painel_diario"]""", "lang": "df"},
 {"p": "*Se eu mexer aqui, o que quebra?* — a pergunta que trava refatoração em pipeline grande."},

 {"h2": "Sair"},
 {"code": """O.relatorio(p)         // tudo em texto, para o log
O.prometheus(p)        // o formato de exposição, para o coletor
O.salvar(p, "obs/execucao.json")
O.alertar(p, regras)""", "lang": "df"},
 {"h3": "Alertas"},
 {"code": """regras := {
    "latencia_ms": {"acima": 10, "estatistica": "p99", "texto": "a cauda está longa"},
    "erros":       {"acima": 0, "texto": "houve falha"},
}""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Alerta é sobre o que exige ação", "texto": "Uma regra que dispara todo dia deixa de ser lida em uma semana — e aí a que importa passa despercebida junto. Alerte sobre o p99, não sobre a média: é a cauda que dói."}},
 {"h3": "Expor no Kiln"},
 {"code": """route GET "/metricas":
    respond text O.prometheus(painel)""", "lang": "df"},
]},

{
"href": "/docs/instalacao/docker",
"title": "Docker",
"description": "A imagem oficial: multi-estágio, sem root, sem dependências.",
"blocos": [
 {"code": """docker run --rm -it estevan5s/dataforge repl""", "lang": "bash"},
 {"p": "A imagem oficial está em [hub.docker.com/r/estevan5s/dataforge](https://hub.docker.com/r/estevan5s/dataforge). Ela é **multi-estágio**: as ferramentas de build ficam no primeiro estágio e não chegam à imagem final — o que se baixa é o interpretador, a biblioteca padrão e nada mais."},

 {"h2": "Rodar o seu arquivo"},
 {"code": """docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df""", "lang": "bash"},
 {"p": "O `-v \"$PWD:/app\"` monta a pasta atual em `/app`, que é o diretório de trabalho da imagem. **Sem ele, o container não enxerga arquivo nenhum seu** — é o esquecimento mais comum."},
 {"code": """alias df-docker='docker run --rm -it -v "$PWD:/app" estevan5s/dataforge'

df-docker run main.df
df-docker check src/
df-docker repl""", "lang": "bash"},

 {"h2": "O que há dentro"},
 {"table": {"head": ["", ""], "rows": [
   ["Base", "`python:3.12-slim`"],
   ["Usuário", "`forge` — **não é root**"],
   ["Diretório", "`/app`"],
   ["Entrypoint", "`dataforge`"],
   ["Comando padrão", "`repl`"],
   ["Dependências", "**nenhuma** além da stdlib do Python"]]}},
 {"p": "O entrypoint é o `dataforge`, então **qualquer subcomando funciona** — `run`, `check`, `fmt`, `lint`, `test`, `big-o`, `init`, `new`, `repl`."},

 {"h2": "Servidor web"},
 {"p": "O Kiln escuta em `0.0.0.0` dentro do container. Em `127.0.0.1` ele ficaria inalcançável de fora — é o erro mais comum ao conteinerizar um servidor."},
 {"code": """docker run --rm -p 8080:8080 -v "$PWD:/app" estevan5s/dataforge run app.df
curl localhost:8080""", "lang": "bash"},

 {"h2": "Como imagem base"},
 {"code": """FROM estevan5s/dataforge:1.0.0

WORKDIR /app
COPY forge.toml .
RUN dataforge install          # resolve as dependências primeiro

COPY src/ ./src/
RUN dataforge check src/ --strict    # o build falha se o código não passar

EXPOSE 8080
CMD ["run", "src/main.df"]""", "lang": "text"},
 {"callout": {"tipo": "dica", "titulo": "Copie o `forge.toml` antes do código", "texto": "As dependências mudam menos que o código. Nessa ordem, o Docker reaproveita a camada do `install` em toda build que só mexeu em `src/` — a diferença entre um build de 2 segundos e um de 2 minutos."}},

 {"h2": "No CI"},
 {"code": """jobs:
  verificar:
    runs-on: ubuntu-latest
    container: estevan5s/dataforge:1.0.0
    steps:
      - uses: actions/checkout@v4
      - run: dataforge check src/ --strict
      - run: dataforge fmt . --check
      - run: dataforge test tests/""", "lang": "text"},
 {"p": "Como o container **já é** o ambiente, não há passo de instalação — e a versão do interpretador fica presa na tag, então o CI de hoje roda igual daqui a um ano."},

 {"h2": "Etiquetas"},
 {"table": {"head": ["Tag", "O que é"], "rows": [
   ["`latest`", "a última versão estável"],
   ["`1.0.0`", "uma versão fixa — **use esta em produção**"],
   ["`1.0`", "a última correção da 1.0"]]}},
 {"callout": {"tipo": "atencao", "titulo": "`latest` muda sem avisar", "texto": "Num Dockerfile ou num CI, fixe a versão. É a diferença entre um build reproduzível e um que quebra numa terça-feira sem ninguém ter mexido em nada."}},

 {"h2": "Permissões"},
 {"p": "O container não roda como root. Se os arquivos que ele cria aparecerem com dono errado na sua máquina, force o seu próprio usuário:"},
 {"code": """docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/app" \\
  estevan5s/dataforge run main.df""", "lang": "bash"},

 {"h2": "Construir a sua"},
 {"code": """git clone https://github.com/estevam5s/DataForge
cd DataForge
docker build -t dataforge .
docker run --rm -it dataforge repl""", "lang": "bash"},
]},
]
