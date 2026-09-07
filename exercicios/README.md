# Exercícios DataForge

120 exercícios em 10 módulos, do "Olá, mundo" a um interpretador de expressões
escrito em DataForge. **Cada exercício verifica o próprio resultado com `assert`**
— se ele roda sem erro, está correto.

## Como rodar

```bash
python3 exercicios/run_all.py          # todos os 120
python3 exercicios/run_all.py 05       # só o módulo 05
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df    # um exercício
```

## Como estudar

Cada arquivo começa com o número, o título e o enunciado:

```dataforge
// Exercicio 004 — Operadores aritmeticos
// Enunciado: use +, -, *, /, %, ** e a divisao inteira ~/.
```

Leia o enunciado, tente resolver por conta, depois compare. Os `assert` no fim
documentam exatamente o comportamento esperado — inclusive os casos de borda.

---


## 01 — Fundamentos

*12 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 001 | [`001_ola_mundo.df`](01-fundamentos/001_ola_mundo.df) | Ola, mundo |
| 002 | [`002_variaveis.df`](01-fundamentos/002_variaveis.df) | Variaveis |
| 003 | [`003_constantes.df`](01-fundamentos/003_constantes.df) | Constantes com steady |
| 004 | [`004_aritmetica.df`](01-fundamentos/004_aritmetica.df) | Operadores aritmeticos |
| 005 | [`005_precedencia.df`](01-fundamentos/005_precedencia.df) | Precedencia de operadores |
| 006 | [`006_comparacoes.df`](01-fundamentos/006_comparacoes.df) | Comparacoes |
| 007 | [`007_logica.df`](01-fundamentos/007_logica.df) | Operadores logicos |
| 008 | [`008_comparacao_encadeada.df`](01-fundamentos/008_comparacao_encadeada.df) | Comparacao encadeada |
| 009 | [`009_atribuicao_composta.df`](01-fundamentos/009_atribuicao_composta.df) | Atribuicao composta |
| 010 | [`010_tipos_e_conversao.df`](01-fundamentos/010_tipos_e_conversao.df) | typeof e cast |
| 011 | [`011_anotacoes_de_tipo.df`](01-fundamentos/011_anotacoes_de_tipo.df) | Anotacoes de tipo |
| 012 | [`012_entrada_de_dados.df`](01-fundamentos/012_entrada_de_dados.df) | Interpolacao e formatacao de saida |

## 02 — Controle de fluxo

*12 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 013 | [`013_given_simples.df`](02-controle-fluxo/013_given_simples.df) | Condicional given |
| 014 | [`014_given_aninhado.df`](02-controle-fluxo/014_given_aninhado.df) | Condicionais aninhadas |
| 015 | [`015_match.df`](02-controle-fluxo/015_match.df) | match / point / default |
| 016 | [`016_cycle_from_to.df`](02-controle-fluxo/016_cycle_from_to.df) | Laco cycle from/to |
| 017 | [`017_cycle_step.df`](02-controle-fluxo/017_cycle_step.df) | Laco com step |
| 018 | [`018_cycle_in.df`](02-controle-fluxo/018_cycle_in.df) | Laco cycle in |
| 019 | [`019_persist.df`](02-controle-fluxo/019_persist.df) | Laco persist (while) |
| 020 | [`020_perform.df`](02-controle-fluxo/020_perform.df) | Laco perform (do-while) |
| 021 | [`021_halt_skip.df`](02-controle-fluxo/021_halt_skip.df) | halt e skip |
| 022 | [`022_lacos_aninhados.df`](02-controle-fluxo/022_lacos_aninhados.df) | Lacos aninhados |
| 023 | [`023_fizzbuzz.df`](02-controle-fluxo/023_fizzbuzz.df) | FizzBuzz |
| 024 | [`024_guard.df`](02-controle-fluxo/024_guard.df) | guard como pre-condicao |

## 03 — Coleções

*14 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 025 | [`025_clusters.df`](03-colecoes/025_clusters.df) | Clusters (listas) |
| 026 | [`026_fatiamento.df`](03-colecoes/026_fatiamento.df) | Fatiamento |
| 027 | [`027_metodos_de_cluster.df`](03-colecoes/027_metodos_de_cluster.df) | Metodos de cluster |
| 028 | [`028_agregacoes.df`](03-colecoes/028_agregacoes.df) | Agregacoes numericas |
| 029 | [`029_unique_flatten.df`](03-colecoes/029_unique_flatten.df) | unique, flatten e chunk |
| 030 | [`030_ordenacao.df`](03-colecoes/030_ordenacao.df) | Ordenacao |
| 031 | [`031_vaults.df`](03-colecoes/031_vaults.df) | Vaults (dicionarios) |
| 032 | [`032_vault_iteracao.df`](03-colecoes/032_vault_iteracao.df) | Percorrendo vaults |
| 033 | [`033_vault_avancado.df`](03-colecoes/033_vault_avancado.df) | Operacoes avancadas de vault |
| 034 | [`034_matrizes.df`](03-colecoes/034_matrizes.df) | Matrizes |
| 035 | [`035_pilha_fila.df`](03-colecoes/035_pilha_fila.df) | Pilha e fila |
| 036 | [`036_busca.df`](03-colecoes/036_busca.df) | Busca linear e binaria |
| 037 | [`037_ordenacao_manual.df`](03-colecoes/037_ordenacao_manual.df) | Bubble sort |
| 038 | [`038_frequencias.df`](03-colecoes/038_frequencias.df) | Contagem de frequencias |

## 04 — Textos

*10 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 039 | [`039_basico_strings.df`](04-strings/039_basico_strings.df) | Strings basicas |
| 040 | [`040_caixa_e_limpeza.df`](04-strings/040_caixa_e_limpeza.df) | Caixa e limpeza |
| 041 | [`041_busca_em_texto.df`](04-strings/041_busca_em_texto.df) | Busca dentro de texto |
| 042 | [`042_split_join.df`](04-strings/042_split_join.df) | split e join |
| 043 | [`043_substituicao.df`](04-strings/043_substituicao.df) | Substituicao e preenchimento |
| 044 | [`044_inversao_palindromo.df`](04-strings/044_inversao_palindromo.df) | Palindromo |
| 045 | [`045_contagem_palavras.df`](04-strings/045_contagem_palavras.df) | Contagem de palavras |
| 046 | [`046_template.df`](04-strings/046_template.df) | Templates de texto |
| 047 | [`047_regex.df`](04-strings/047_regex.df) | Expressoes regulares |
| 048 | [`048_cifra_cesar.df`](04-strings/048_cifra_cesar.df) | Cifra de Cesar |

## 05 — Ações (funções)

*14 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 049 | [`049_acao_basica.df`](05-acoes/049_acao_basica.df) | Acao basica |
| 050 | [`050_parametros_padrao.df`](05-acoes/050_parametros_padrao.df) | Parametros com valor padrao |
| 051 | [`051_argumentos_nomeados.df`](05-acoes/051_argumentos_nomeados.df) | Argumentos nomeados |
| 052 | [`052_aridade.df`](05-acoes/052_aridade.df) | Verificacao de aridade |
| 053 | [`053_tipos_em_acoes.df`](05-acoes/053_tipos_em_acoes.df) | Acoes tipadas |
| 054 | [`054_recursao.df`](05-acoes/054_recursao.df) | Recursao |
| 055 | [`055_recursao_profunda.df`](05-acoes/055_recursao_profunda.df) | Limite de recursao |
| 056 | [`056_acoes_de_alta_ordem.df`](05-acoes/056_acoes_de_alta_ordem.df) | Acoes de alta ordem |
| 057 | [`057_closures.df`](05-acoes/057_closures.df) | Closures |
| 058 | [`058_lambdas.df`](05-acoes/058_lambdas.df) | Lambdas |
| 059 | [`059_decoradores.df`](05-acoes/059_decoradores.df) | Decoradores com mark |
| 060 | [`060_defer.df`](05-acoes/060_defer.df) | defer |
| 061 | [`061_escopo.df`](05-acoes/061_escopo.df) | Escopo e shadow |
| 062 | [`062_memoizacao.df`](05-acoes/062_memoizacao.df) | Memoizacao manual |

## 06 — Blueprints (classes)

*14 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 063 | [`063_blueprint_basico.df`](06-blueprints/063_blueprint_basico.df) | Blueprint com construtor |
| 064 | [`064_setup.df`](06-blueprints/064_setup.df) | Construtor com setup |
| 065 | [`065_metodos_e_estado.df`](06-blueprints/065_metodos_e_estado.df) | Estado mutavel |
| 066 | [`066_heranca.df`](06-blueprints/066_heranca.df) | Heranca com extends |
| 067 | [`067_root.df`](06-blueprints/067_root.df) | root (super) |
| 068 | [`068_traits.df`](06-blueprints/068_traits.df) | Traits (interfaces) |
| 069 | [`069_polimorfismo.df`](06-blueprints/069_polimorfismo.df) | Polimorfismo |
| 070 | [`070_estaticos.df`](06-blueprints/070_estaticos.df) | Membros estaticos |
| 071 | [`071_sobrecarga_operadores.df`](06-blueprints/071_sobrecarga_operadores.df) | Sobrecarga de operadores |
| 072 | [`072_composicao.df`](06-blueprints/072_composicao.df) | Composicao |
| 073 | [`073_heranca_profunda.df`](06-blueprints/073_heranca_profunda.df) | Cadeia de heranca |
| 074 | [`074_introspeccao.df`](06-blueprints/074_introspeccao.df) | Introspeccao |
| 075 | [`075_padrao_singleton.df`](06-blueprints/075_padrao_singleton.df) | Padrao Singleton |
| 076 | [`076_padrao_observador.df`](06-blueprints/076_padrao_observador.df) | Padrao Observador |

## 07 — Tratamento de erros

*10 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 077 | [`077_monitor_handle.df`](07-erros/077_monitor_handle.df) | monitor / handle |
| 078 | [`078_ensure.df`](07-erros/078_ensure.df) | ensure (finally) |
| 079 | [`079_trigger.df`](07-erros/079_trigger.df) | trigger (lancar erro) |
| 080 | [`080_handle_tipado.df`](07-erros/080_handle_tipado.df) | handle tipado |
| 081 | [`081_monitor_sem_handle.df`](07-erros/081_monitor_sem_handle.df) | monitor sem handle propaga |
| 082 | [`082_guard_validate.df`](07-erros/082_guard_validate.df) | guard e validate |
| 083 | [`083_retry.df`](07-erros/083_retry.df) | retry |
| 084 | [`084_propagate.df`](07-erros/084_propagate.df) | propagate |
| 085 | [`085_assert.df`](07-erros/085_assert.df) | assert |
| 086 | [`086_erros_aninhados.df`](07-erros/086_erros_aninhados.df) | Pilha de erros e recuperacao |

## 08 — Pipelines e programação funcional

*12 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 087 | [`087_sift.df`](08-pipelines/087_sift.df) | sift (filtro) |
| 088 | [`088_morph.df`](08-pipelines/088_morph.df) | morph (transformacao) |
| 089 | [`089_distill.df`](08-pipelines/089_distill.df) | distill (reducao) |
| 090 | [`090_pipeline_encadeado.df`](08-pipelines/090_pipeline_encadeado.df) | Pipeline encadeado |
| 091 | [`091_pipeline_com_acao.df`](08-pipelines/091_pipeline_com_acao.df) | Pipeline com acao nomeada |
| 092 | [`092_map_filter_reduce.df`](08-pipelines/092_map_filter_reduce.df) | map, filter e reduce como metodos |
| 093 | [`093_composicao_funcoes.df`](08-pipelines/093_composicao_funcoes.df) | Composicao de funcoes |
| 094 | [`094_currying.df`](08-pipelines/094_currying.df) | Aplicacao parcial e curry |
| 095 | [`095_stdlib_functional.df`](08-pipelines/095_stdlib_functional.df) | Arcane.Functional |
| 096 | [`096_observe_stream.df`](08-pipelines/096_observe_stream.df) | Streams reativos |
| 097 | [`097_pipeline_relatorio.df`](08-pipelines/097_pipeline_relatorio.df) | Relatorio com pipelines |
| 098 | [`098_pipeline_texto.df`](08-pipelines/098_pipeline_texto.df) | Pipeline de limpeza de dados |

## 09 — Módulos e biblioteca padrão

*12 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 099 | [`099_adopt_local.df`](09-modulos/099_adopt_local.df) | adopt de um modulo local |
| 100 | [`100_adopt_erro.df`](09-modulos/100_adopt_erro.df) | Import inexistente |
| 101 | [`101_math.df`](09-modulos/101_math.df) | Arcane.Math |
| 102 | [`102_estatistica.df`](09-modulos/102_estatistica.df) | Estatistica descritiva |
| 103 | [`103_analytics.df`](09-modulos/103_analytics.df) | Arcane.Analytics |
| 104 | [`104_regressao.df`](09-modulos/104_regressao.df) | Regressao linear |
| 105 | [`105_dados_tabulares.df`](09-modulos/105_dados_tabulares.df) | Dados tabulares |
| 106 | [`106_io_arquivos.df`](09-modulos/106_io_arquivos.df) | Arcane.IO |
| 107 | [`107_json.df`](09-modulos/107_json.df) | JSON |
| 108 | [`108_database.df`](09-modulos/108_database.df) | Arcane.Database |
| 109 | [`109_texto_avancado.df`](09-modulos/109_texto_avancado.df) | Arcane.Text |
| 110 | [`110_testes.df`](09-modulos/110_testes.df) | Arcane.Test |

## 10 — Concorrência e estruturas de dados

*10 exercícios*

| # | Arquivo | Assunto |
|---|---------|---------|
| 111 | [`111_async_await.df`](10-avancado/111_async_await.df) | async / await |
| 112 | [`112_threads.df`](10-avancado/112_threads.df) | thread |
| 113 | [`113_channel.df`](10-avancado/113_channel.df) | channel |
| 114 | [`114_parallel.df`](10-avancado/114_parallel.df) | parallel |
| 115 | [`115_defer_recurso.df`](10-avancado/115_defer_recurso.df) | defer com recursos reais |
| 116 | [`116_estruturas_dados.df`](10-avancado/116_estruturas_dados.df) | Lista ligada com blueprints |
| 117 | [`117_arvore_binaria.df`](10-avancado/117_arvore_binaria.df) | Arvore binaria de busca |
| 118 | [`118_maquina_estados.df`](10-avancado/118_maquina_estados.df) | Maquina de estados |
| 119 | [`119_inventario_completo.df`](10-avancado/119_inventario_completo.df) | Sistema de inventario |
| 120 | [`120_interpretador_expressoes.df`](10-avancado/120_interpretador_expressoes.df) | Avaliador de expressoes em notacao polonesa reversa |

---

**Total: 120 exercícios.** Todos passam — o estado esperado do repositório é
verde. Se algum falhar, é regressão no interpretador: veja
[`../CLAUDE.md`](../CLAUDE.md).
