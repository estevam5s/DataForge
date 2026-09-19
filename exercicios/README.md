# Exercícios DataForge

**216 exercícios em 26 módulos**, do `out "Ola"` a um interpretador de expressões
com lexer, parser e avaliador próprios.

Cada exercício **verifica o próprio resultado com `assert`** — se ele roda sem
erro, está correto. Os módulos **11 a 20** trazem um arquivo `.md` ao lado de cada
`.df`, com enunciado, conceitos, saída esperada e sugestões para experimentar.

## Como rodar

```bash
python3 exercicios/run_all.py          # todos os 180
python3 exercicios/run_all.py 14       # só o módulo 14
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df    # um exercício
```

## Como estudar

Cada arquivo começa com o número, o título e o enunciado:

```dataforge
// Exercicio 134 — Resto e spread
// Enunciado: colete o que sobra com ...resto e expanda colecoes com ...
```

Leia o enunciado, tente resolver por conta, depois compare. Os `assert` no fim
documentam exatamente o comportamento esperado — inclusive os casos de borda.

Nos módulos 11–20, abra o `.md` de mesmo nome para a explicação completa.

## Trilhas

| Se você quer… | Comece por |
|---------------|------------|
| aprender a linguagem do zero | 01 → 10, na ordem |
| conhecer os recursos do 4.0 | 11 → 16 |
| escrever programas de verdade | 16 → 20 |
| dominar pattern matching | 12, 14 |
| trabalhar com dados | 03, 08, 15, 18, 20 |
| construir uma aplicação | 16, 17, 18, 19, 20 |

---

<!-- indice:inicio -->

## 01 — Fundamentos

*12 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 02 — Controle fluxo

*12 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 03 — Colecoes

*14 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 04 — Strings

*10 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 05 — Acoes

*14 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 06 — Blueprints

*14 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 07 — Erros

*10 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 08 — Pipelines

*12 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 09 — Modulos

*12 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 10 — Avancado

*10 exercícios*

| # | Exercício | Assunto |
|---|-----------|---------|
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

## 11 — Tipos e checagem

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 121 | [`121_anotacoes_basicas.df`](11-tipos-e-checagem/121_anotacoes_basicas.df) · [doc](11-tipos-e-checagem/121_anotacoes_basicas.md) | Anotacoes de tipo |
| 122 | [`122_acoes_tipadas.df`](11-tipos-e-checagem/122_acoes_tipadas.df) · [doc](11-tipos-e-checagem/122_acoes_tipadas.md) | Acoes com tipos |
| 123 | [`123_typeof_e_cast.df`](11-tipos-e-checagem/123_typeof_e_cast.df) · [doc](11-tipos-e-checagem/123_typeof_e_cast.md) | typeof e conversao |
| 124 | [`124_checagem_estatica.df`](11-tipos-e-checagem/124_checagem_estatica.df) · [doc](11-tipos-e-checagem/124_checagem_estatica.md) | Analise estatica |
| 125 | [`125_tipos_em_colecoes.df`](11-tipos-e-checagem/125_tipos_em_colecoes.df) · [doc](11-tipos-e-checagem/125_tipos_em_colecoes.md) | Tipos dentro de colecoes |
| 126 | [`126_any_e_gradual.df`](11-tipos-e-checagem/126_any_e_gradual.df) · [doc](11-tipos-e-checagem/126_any_e_gradual.md) | Tipagem gradual com Any |

## 12 — Records e enums

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 127 | [`127_record_basico.df`](12-records-e-enums/127_record_basico.df) · [doc](12-records-e-enums/127_record_basico.md) | Records |
| 128 | [`128_record_imutavel.df`](12-records-e-enums/128_record_imutavel.df) · [doc](12-records-e-enums/128_record_imutavel.md) | Imutabilidade e with |
| 129 | [`129_record_com_metodos.df`](12-records-e-enums/129_record_com_metodos.df) · [doc](12-records-e-enums/129_record_com_metodos.md) | Records com metodos |
| 130 | [`130_enum_basico.df`](12-records-e-enums/130_enum_basico.df) · [doc](12-records-e-enums/130_enum_basico.md) | Enums |
| 131 | [`131_enum_com_valores.df`](12-records-e-enums/131_enum_com_valores.df) · [doc](12-records-e-enums/131_enum_com_valores.md) | Enums com valores |
| 132 | [`132_enum_e_match.df`](12-records-e-enums/132_enum_e_match.df) · [doc](12-records-e-enums/132_enum_e_match.md) | Enums com match |

## 13 — Desestruturacao

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 133 | [`133_desestruturar_listas.df`](13-desestruturacao/133_desestruturar_listas.df) · [doc](13-desestruturacao/133_desestruturar_listas.md) | Desestruturacao de listas |
| 134 | [`134_resto_e_spread.df`](13-desestruturacao/134_resto_e_spread.df) · [doc](13-desestruturacao/134_resto_e_spread.md) | Resto e spread |
| 135 | [`135_desestruturar_registros.df`](13-desestruturacao/135_desestruturar_registros.df) · [doc](13-desestruturacao/135_desestruturar_registros.md) | Desestruturar records e vaults |
| 136 | [`136_comprehension_lista.df`](13-desestruturacao/136_comprehension_lista.df) · [doc](13-desestruturacao/136_comprehension_lista.md) | Compreensao de listas |
| 137 | [`137_comprehension_vault.df`](13-desestruturacao/137_comprehension_vault.df) · [doc](13-desestruturacao/137_comprehension_vault.md) | Compreensao de vaults |
| 138 | [`138_interpolacao.df`](13-desestruturacao/138_interpolacao.df) · [doc](13-desestruturacao/138_interpolacao.md) | Interpolacao de strings |

## 14 — Pattern matching

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 139 | [`139_padroes_basicos.df`](14-pattern-matching/139_padroes_basicos.df) · [doc](14-pattern-matching/139_padroes_basicos.md) | Padroes basicos |
| 140 | [`140_padroes_de_tipo.df`](14-pattern-matching/140_padroes_de_tipo.df) · [doc](14-pattern-matching/140_padroes_de_tipo.md) | Padroes de tipo |
| 141 | [`141_padroes_de_sequencia.df`](14-pattern-matching/141_padroes_de_sequencia.df) · [doc](14-pattern-matching/141_padroes_de_sequencia.md) | Padroes de sequencia |
| 142 | [`142_padroes_de_registro.df`](14-pattern-matching/142_padroes_de_registro.df) · [doc](14-pattern-matching/142_padroes_de_registro.md) | Padroes de record e vault |
| 143 | [`143_guardas_e_binding.df`](14-pattern-matching/143_guardas_e_binding.df) · [doc](14-pattern-matching/143_guardas_e_binding.md) | Guardas e ligacao com as |
| 144 | [`144_interpretador_json.df`](14-pattern-matching/144_interpretador_json.df) · [doc](14-pattern-matching/144_interpretador_json.md) | Projeto: validador de dados |

## 15 — Streams e generators

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 145 | [`145_generator_basico.df`](15-streams-e-generators/145_generator_basico.df) · [doc](15-streams-e-generators/145_generator_basico.md) | Generators com stream action |
| 146 | [`146_generator_infinito.df`](15-streams-e-generators/146_generator_infinito.df) · [doc](15-streams-e-generators/146_generator_infinito.md) | Sequencias infinitas |
| 147 | [`147_stream_em_pipeline.df`](15-streams-e-generators/147_stream_em_pipeline.df) · [doc](15-streams-e-generators/147_stream_em_pipeline.md) | Streams com pipelines |
| 148 | [`148_stream_leitura.df`](15-streams-e-generators/148_stream_leitura.df) · [doc](15-streams-e-generators/148_stream_leitura.md) | Processamento incremental |
| 149 | [`149_observe_reativo.df`](15-streams-e-generators/149_observe_reativo.df) · [doc](15-streams-e-generators/149_observe_reativo.md) | observe e eventos |
| 150 | [`150_projeto_etl.df`](15-streams-e-generators/150_projeto_etl.df) · [doc](15-streams-e-generators/150_projeto_etl.md) | Projeto: ETL com streams |

## 16 — Modulos e projetos

*7 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 151 | [`151_adopt_e_relay.df`](16-modulos-e-projetos/151_adopt_e_relay.df) · [doc](16-modulos-e-projetos/151_adopt_e_relay.md) | Modulos com adopt e relay |
| 152 | [`152_imports_seletivos.df`](16-modulos-e-projetos/152_imports_seletivos.df) · [doc](16-modulos-e-projetos/152_imports_seletivos.md) | Imports seletivos e apelidos |
| 153 | [`153_organizacao_projeto.df`](16-modulos-e-projetos/153_organizacao_projeto.df) · [doc](16-modulos-e-projetos/153_organizacao_projeto.md) | Organizando um projeto |
| 154 | [`154_forge_toml.df`](16-modulos-e-projetos/154_forge_toml.df) · [doc](16-modulos-e-projetos/154_forge_toml.md) | Manifesto e ferramentas |
| 155 | [`155_testes_automatizados.df`](16-modulos-e-projetos/155_testes_automatizados.df) · [doc](16-modulos-e-projetos/155_testes_automatizados.md) | Testes automatizados |
| 156 | [`156_projeto_biblioteca.df`](16-modulos-e-projetos/156_projeto_biblioteca.df) · [doc](16-modulos-e-projetos/156_projeto_biblioteca.md) | Projeto: biblioteca completa |
| 157 | [`157_check_entre_modulos.df`](16-modulos-e-projetos/157_check_entre_modulos.df) · [doc](16-modulos-e-projetos/157_check_entre_modulos.md) | O que o 'check' pega ATRAVES do adopt |

## 17 — Tempo e sistema

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 158 | [`158_datas_basico.df`](17-tempo-e-sistema/158_datas_basico.df) · [doc](17-tempo-e-sistema/158_datas_basico.md) | Datas e horas |
| 159 | [`159_datas_aritmetica.df`](17-tempo-e-sistema/159_datas_aritmetica.df) · [doc](17-tempo-e-sistema/159_datas_aritmetica.md) | Aritmetica com datas |
| 160 | [`160_cronometro.df`](17-tempo-e-sistema/160_cronometro.df) · [doc](17-tempo-e-sistema/160_cronometro.md) | Cronometragem e desempenho |
| 161 | [`161_sistema_e_ambiente.df`](17-tempo-e-sistema/161_sistema_e_ambiente.df) · [doc](17-tempo-e-sistema/161_sistema_e_ambiente.md) | Sistema e ambiente |
| 162 | [`162_processos.df`](17-tempo-e-sistema/162_processos.df) · [doc](17-tempo-e-sistema/162_processos.md) | Executando processos |
| 163 | [`163_logging_estruturado.df`](17-tempo-e-sistema/163_logging_estruturado.df) · [doc](17-tempo-e-sistema/163_logging_estruturado.md) | Registro de eventos |

## 18 — Dados e persistencia

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 164 | [`164_serializacao.df`](18-dados-e-persistencia/164_serializacao.df) · [doc](18-dados-e-persistencia/164_serializacao.md) | Serializacao de dados |
| 165 | [`165_arquivos.df`](18-dados-e-persistencia/165_arquivos.df) · [doc](18-dados-e-persistencia/165_arquivos.md) | Arquivos e diretorios |
| 166 | [`166_banco_sqlite.df`](18-dados-e-persistencia/166_banco_sqlite.df) · [doc](18-dados-e-persistencia/166_banco_sqlite.md) | Banco de dados |
| 167 | [`167_http_servidor.df`](18-dados-e-persistencia/167_http_servidor.df) · [doc](18-dados-e-persistencia/167_http_servidor.md) | Servidor HTTP |
| 168 | [`168_http_cliente.df`](18-dados-e-persistencia/168_http_cliente.df) · [doc](18-dados-e-persistencia/168_http_cliente.md) | Cliente HTTP e URLs |
| 169 | [`169_projeto_crud.df`](18-dados-e-persistencia/169_projeto_crud.df) · [doc](18-dados-e-persistencia/169_projeto_crud.md) | Projeto: CRUD com persistencia |

## 19 — Concorrencia

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 170 | [`170_async_await.df`](19-concorrencia/170_async_await.df) · [doc](19-concorrencia/170_async_await.md) | Acoes assincronas |
| 171 | [`171_threads.df`](19-concorrencia/171_threads.df) · [doc](19-concorrencia/171_threads.md) | Threads e paralelismo |
| 172 | [`172_canais.df`](19-concorrencia/172_canais.df) · [doc](19-concorrencia/172_canais.md) | Canais entre threads |
| 173 | [`173_defer_recursos.df`](19-concorrencia/173_defer_recursos.df) · [doc](19-concorrencia/173_defer_recursos.md) | Liberacao garantida |
| 174 | [`174_erros_concorrentes.df`](19-concorrencia/174_erros_concorrentes.df) · [doc](19-concorrencia/174_erros_concorrentes.md) | Erros e retentativas |
| 175 | [`175_projeto_worker.df`](19-concorrencia/175_projeto_worker.df) · [doc](19-concorrencia/175_projeto_worker.md) | Projeto: fila de trabalho |

## 20 — Projetos finais

*6 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 176 | [`176_cli_arquivos.df`](20-projetos-finais/176_cli_arquivos.df) · [doc](20-projetos-finais/176_cli_arquivos.md) | Projeto: ferramenta de linha de comando |
| 177 | [`177_analise_dados.df`](20-projetos-finais/177_analise_dados.df) · [doc](20-projetos-finais/177_analise_dados.md) | Projeto: analise de dados |
| 178 | [`178_interpretador.df`](20-projetos-finais/178_interpretador.df) · [doc](20-projetos-finais/178_interpretador.md) | Projeto: mini linguagem |
| 179 | [`179_sistema_completo.df`](20-projetos-finais/179_sistema_completo.df) · [doc](20-projetos-finais/179_sistema_completo.md) | Projeto: sistema de biblioteca |
| 180 | [`180_revisao_geral.df`](20-projetos-finais/180_revisao_geral.df) · [doc](20-projetos-finais/180_revisao_geral.md) | Revisao: todos os conceitos |
| 181 | [`181_proximos_passos.df`](20-projetos-finais/181_proximos_passos.df) · [doc](20-projetos-finais/181_proximos_passos.md) | Encerramento e proximos passos |

## 21 — Oop avancado

*10 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 182 | [`182_campos_declarados.df`](21-oop-avancado/182_campos_declarados.df) · [doc](21-oop-avancado/182_campos_declarados.md) | Campos declarados |
| 183 | [`183_metodos_estaticos.df`](21-oop-avancado/183_metodos_estaticos.df) · [doc](21-oop-avancado/183_metodos_estaticos.md) | Metodos estaticos |
| 184 | [`184_propriedades.df`](21-oop-avancado/184_propriedades.df) · [doc](21-oop-avancado/184_propriedades.md) | Propriedades com get e set |
| 185 | [`185_visibilidade.df`](21-oop-avancado/185_visibilidade.df) · [doc](21-oop-avancado/185_visibilidade.md) | Visibilidade: private e protected |
| 186 | [`186_sobrecarga_operadores.df`](21-oop-avancado/186_sobrecarga_operadores.df) · [doc](21-oop-avancado/186_sobrecarga_operadores.md) | Sobrecarga de operadores |
| 187 | [`187_abstratos_e_traits.df`](21-oop-avancado/187_abstratos_e_traits.df) · [doc](21-oop-avancado/187_abstratos_e_traits.md) | Blueprints abstratos e contratos de trait |
| 188 | [`188_heranca_e_root.df`](21-oop-avancado/188_heranca_e_root.df) · [doc](21-oop-avancado/188_heranca_e_root.md) | Heranca e 'root' |
| 189 | [`189_composicao.df`](21-oop-avancado/189_composicao.df) · [doc](21-oop-avancado/189_composicao.md) | Composicao no lugar de heranca |
| 190 | [`190_records_vs_blueprints.df`](21-oop-avancado/190_records_vs_blueprints.df) · [doc](21-oop-avancado/190_records_vs_blueprints.md) | Quando usar record e quando usar blueprint |
| 191 | [`191_polimorfismo.df`](21-oop-avancado/191_polimorfismo.df) · [doc](21-oop-avancado/191_polimorfismo.md) | Polimorfismo |

## 22 — Web kiln

*8 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 192 | [`192_primeiro_servidor.df`](22-web-kiln/192_primeiro_servidor.df) · [doc](22-web-kiln/192_primeiro_servidor.md) | O primeiro servidor |
| 193 | [`193_parametros_e_query.df`](22-web-kiln/193_parametros_e_query.df) · [doc](22-web-kiln/193_parametros_e_query.md) | Parametros de caminho e query string |
| 194 | [`194_crud_restful.df`](22-web-kiln/194_crud_restful.df) · [doc](22-web-kiln/194_crud_restful.md) | Uma API RESTful completa |
| 195 | [`195_paginas_html.df`](22-web-kiln/195_paginas_html.df) · [doc](22-web-kiln/195_paginas_html.md) | Paginas HTML com template |
| 196 | [`196_middleware_e_auth.df`](22-web-kiln/196_middleware_e_auth.df) · [doc](22-web-kiln/196_middleware_e_auth.md) | Middleware, autenticacao e limite de taxa |
| 197 | [`197_erros_e_estaticos.df`](22-web-kiln/197_erros_e_estaticos.df) · [doc](22-web-kiln/197_erros_e_estaticos.md) | Paginas de erro, redirecionamento e arquivos estaticos |
| 198 | [`198_servidor_de_verdade.df`](22-web-kiln/198_servidor_de_verdade.df) · [doc](22-web-kiln/198_servidor_de_verdade.md) | Subir o servidor de verdade |
| 199 | [`199_api_rest_export.df`](22-web-kiln/199_api_rest_export.df) · [doc](22-web-kiln/199_api_rest_export.md) | A API vista de fora: OpenAPI, Insomnia e curl |

## 23 — Dados e planilhas

*3 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 200 | [`200_primeira_planilha.df`](23-dados-e-planilhas/200_primeira_planilha.df) · [doc](23-dados-e-planilhas/200_primeira_planilha.md) | Gravar e ler uma planilha |
| 201 | [`201_relatorio_com_formulas.df`](23-dados-e-planilhas/201_relatorio_com_formulas.df) · [doc](23-dados-e-planilhas/201_relatorio_com_formulas.md) | Relatorio com varias abas e formulas |
| 202 | [`202_planilha_banco_e_analise.df`](23-dados-e-planilhas/202_planilha_banco_e_analise.df) · [doc](23-dados-e-planilhas/202_planilha_banco_e_analise.md) | Do banco para a planilha, passando pela analise |

## 24 — Banco de dados

*8 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 203 | [`203_conectar.df`](24-banco-de-dados/203_conectar.df) · [doc](24-banco-de-dados/203_conectar.md) | Conectar e consultar |
| 204 | [`204_construtor_de_consultas.df`](24-banco-de-dados/204_construtor_de_consultas.df) · [doc](24-banco-de-dados/204_construtor_de_consultas.md) | Construtor de consultas |
| 205 | [`205_injecao_de_sql.df`](24-banco-de-dados/205_injecao_de_sql.df) · [doc](24-banco-de-dados/205_injecao_de_sql.md) | Injecao de SQL, e por que ela nao acontece aqui |
| 206 | [`206_transacoes.df`](24-banco-de-dados/206_transacoes.df) · [doc](24-banco-de-dados/206_transacoes.md) | Transacoes |
| 207 | [`207_modelos_e_validacao.df`](24-banco-de-dados/207_modelos_e_validacao.df) · [doc](24-banco-de-dados/207_modelos_e_validacao.md) | Modelos e validacao |
| 208 | [`208_relacoes_sem_n_mais_um.df`](24-banco-de-dados/208_relacoes_sem_n_mais_um.df) · [doc](24-banco-de-dados/208_relacoes_sem_n_mais_um.md) | Relacoes, e o problema do N+1 |
| 209 | [`209_migracoes.df`](24-banco-de-dados/209_migracoes.df) · [doc](24-banco-de-dados/209_migracoes.md) | Migracoes |
| 210 | [`210_pool_e_conexoes.df`](24-banco-de-dados/210_pool_e_conexoes.df) · [doc](24-banco-de-dados/210_pool_e_conexoes.md) | Pool de conexoes |

## 25 — Testes crucible

*4 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 211 | [`211_primeira_suite.df`](25-testes-crucible/211_primeira_suite.df) · [doc](25-testes-crucible/211_primeira_suite.md) | A primeira suite |
| 212 | [`212_isolamento.df`](25-testes-crucible/212_isolamento.df) · [doc](25-testes-crucible/212_isolamento.md) | Isolamento entre trials |
| 213 | [`213_matchers.df`](25-testes-crucible/213_matchers.df) · [doc](25-testes-crucible/213_matchers.md) | Os matchers |
| 214 | [`214_dubles_e_fixtures.df`](25-testes-crucible/214_dubles_e_fixtures.df) · [doc](25-testes-crucible/214_dubles_e_fixtures.md) | Dubles e fixtures |

## 26 — Complexidade

*4 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 215 | [`215_medir_o_crescimento.df`](26-complexidade/215_medir_o_crescimento.df) · [doc](26-complexidade/215_medir_o_crescimento.md) | Medir o crescimento, nao o relogio |
| 216 | [`216_memoizacao.df`](26-complexidade/216_memoizacao.df) · [doc](26-complexidade/216_memoizacao.md) | Trocar tempo exponencial por memoria linear |
| 217 | [`217_estrutura_certa.df`](26-complexidade/217_estrutura_certa.df) · [doc](26-complexidade/217_estrutura_certa.md) | A estrutura certa |
| 218 | [`218_espaco.df`](26-complexidade/218_espaco.df) · [doc](26-complexidade/218_espaco.md) | Complexidade de espaco |

## 27 — Ponte python

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 219 | [`219_ponte_python.df`](27-ponte-python/219_ponte_python.df) · [doc](27-ponte-python/219_ponte_python.md) | A ponte para o Python |

## 28 — Vitrine

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 220 | [`220_vitrine.df`](28-vitrine/220_vitrine.df) · [doc](28-vitrine/220_vitrine.md) | Uma aplicacao de dados com a Vitrine |

## 29 — Banco e crud

*4 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 221 | [`221_crud_completo.df`](29-banco-e-crud/221_crud_completo.df) · [doc](29-banco-e-crud/221_crud_completo.md) | Um CRUD completo, com o banco fazendo o trabalho |
| 222 | [`222_pdv_e_transacoes.df`](29-banco-e-crud/222_pdv_e_transacoes.df) · [doc](29-banco-e-crud/222_pdv_e_transacoes.md) | Um PDV: a venda inteira, ou nenhuma |
| 223 | [`223_relatorios_e_busca.df`](29-banco-e-crud/223_relatorios_e_busca.df) · [doc](29-banco-e-crud/223_relatorios_e_busca.md) | Relatorio, busca e o indice que falta |
| 224 | [`224_migracoes.df`](29-banco-e-crud/224_migracoes.df) · [doc](29-banco-e-crud/224_migracoes.md) | Migracoes: mudar o schema sem perder dado |

## 30 — Tempo real

*2 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 225 | [`225_upload.df`](30-tempo-real/225_upload.df) · [doc](30-tempo-real/225_upload.md) | Receber arquivo |
| 226 | [`226_sse_e_websocket.df`](30-tempo-real/226_sse_e_websocket.df) · [doc](30-tempo-real/226_sse_e_websocket.md) | O servidor empurra: SSE e WebSocket |

## 31 — Qualidade

*3 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 227 | [`227_cobertura.df`](31-qualidade/227_cobertura.df) · [doc](31-qualidade/227_cobertura.md) | Cobertura: o que os testes NAO exercitaram |
| 228 | [`228_instantaneo_e_isolamento.df`](31-qualidade/228_instantaneo_e_isolamento.df) · [doc](31-qualidade/228_instantaneo_e_isolamento.md) | Instantaneo, banco isolado e teste instavel |
| 229 | [`229_depurar.df`](31-qualidade/229_depurar.df) · [doc](31-qualidade/229_depurar.md) | Depurar sem 'out' |

## 32 — Microservicos

*2 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 230 | [`230_malha.df`](32-microservicos/230_malha.df) · [doc](32-microservicos/230_malha.md) | Chamada entre servicos que nao mente |
| 231 | [`231_saga.df`](32-microservicos/231_saga.df) · [doc](32-microservicos/231_saga.md) | Saga: nao existe transacao que atravesse a rede |

## 33 — Lavra

*3 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 232 | [`232_lavra_basico.df`](33-lavra/232_lavra_basico.df) · [doc](33-lavra/232_lavra_basico.md) | Lavra: o esquema e a consulta |
| 233 | [`233_lavra_n1_e_limites.df`](33-lavra/233_lavra_n1_e_limites.df) · [doc](33-lavra/233_lavra_n1_e_limites.md) | Lavra: o N+1, os limites e a paginacao |
| 234 | [`234_lavra_servidor_e_federacao.df`](33-lavra/234_lavra_servidor_e_federacao.df) · [doc](33-lavra/234_lavra_servidor_e_federacao.md) | Lavra: contratos, mudancas, servidor e federacao |

## 34 — Binario e rede

*3 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 235 | [`235_bytes.df`](34-binario-e-rede/235_bytes.df) · [doc](34-binario-e-rede/235_bytes.md) | Dados binarios com Arcane.Bytes |
| 236 | [`236_rede.df`](34-binario-e-rede/236_rede.df) · [doc](34-binario-e-rede/236_rede.md) | TCP, UDP e DNS com Arcane.Rede |
| 237 | [`237_eventos_cli_html.df`](34-binario-e-rede/237_eventos_cli_html.df) · [doc](34-binario-e-rede/237_eventos_cli_html.md) | Eventos, linha de comando, e-mail e HTML |

## 35 — Paralelismo

*3 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 238 | [`238_varios_nucleos.df`](35-paralelismo/238_varios_nucleos.df) · [doc](35-paralelismo/238_varios_nucleos.md) | Varios nucleos, de verdade |
| 239 | [`239_o_que_atravessa.df`](35-paralelismo/239_o_que_atravessa.df) · [doc](35-paralelismo/239_o_que_atravessa.md) | O que atravessa para o outro processo |
| 240 | [`240_pipeline_em_blocos.df`](35-paralelismo/240_pipeline_em_blocos.df) · [doc](35-paralelismo/240_pipeline_em_blocos.md) | Um pipeline que usa a maquina inteira |

## 36 — Quadro e dados

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 241 | [`241_quadro_e_verbos.df`](36-quadro-e-dados/241_quadro_e_verbos.df) · [doc](36-quadro-e-dados/241_quadro_e_verbos.md) | O quadro, e os seis verbos do pipeline |

## 37 — Oop sistema

*10 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 242 | [`242_contratos_e_segregacao.df`](37-oop-sistema/242_contratos_e_segregacao.df) · [doc](37-oop-sistema/242_contratos_e_segregacao.md) | Contratos pequenos, e quem depende de qual |
| 243 | [`243_modificadores.df`](37-oop-sistema/243_modificadores.df) · [doc](37-oop-sistema/243_modificadores.md) | O que cada modificador promete |
| 244 | [`244_design_por_contrato.df`](37-oop-sistema/244_design_por_contrato.df) · [doc](37-oop-sistema/244_design_por_contrato.md) | De quem e o erro? |
| 245 | [`245_sobrecarga.df`](37-oop-sistema/245_sobrecarga.df) · [doc](37-oop-sistema/245_sobrecarga.md) | Sobrecarga que diz o que aceita |
| 246 | [`246_metaclasses.df`](37-oop-sistema/246_metaclasses.df) · [doc](37-oop-sistema/246_metaclasses.md) | Uma metaclasse que registra, valida e audita |
| 247 | [`247_reflexao.df`](37-oop-sistema/247_reflexao.df) · [doc](37-oop-sistema/247_reflexao.md) | Um validador generico escrito com reflexao |
| 248 | [`248_objetos_e_serializacao.df`](37-oop-sistema/248_objetos_e_serializacao.df) · [doc](37-oop-sistema/248_objetos_e_serializacao.md) | Copia, imutabilidade e serializacao que nao confia no dado |
| 249 | [`249_injecao_hexagonal.df`](37-oop-sistema/249_injecao_hexagonal.df) · [doc](37-oop-sistema/249_injecao_hexagonal.md) | Portas, adaptadores e o conteiner |
| 250 | [`250_padroes.df`](37-oop-sistema/250_padroes.df) · [doc](37-oop-sistema/250_padroes.md) | Padroes com mecanismo: comando, estado e especificacao |
| 251 | [`251_ciclo_de_vida_e_concorrencia.df`](37-oop-sistema/251_ciclo_de_vida_e_concorrencia.df) · [doc](37-oop-sistema/251_ciclo_de_vida_e_concorrencia.md) | Nascer, viver sob threads, e morrer limpo |

## 38 — Tipos

*5 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 252 | [`252_tipos_nomeados.df`](38-tipos/252_tipos_nomeados.df) · [doc](38-tipos/252_tipos_nomeados.md) | Tipos nomeados: alias, uniao, intersecao, refinamento e opaco |
| 253 | [`253_genericos_e_traits.df`](38-tipos/253_genericos_e_traits.df) · [doc](38-tipos/253_genericos_e_traits.md) | Generics, tipos indexados e o sistema de traits |
| 254 | [`254_tuplas.df`](38-tipos/254_tuplas.df) · [doc](38-tipos/254_tuplas.md) | Tuplas: a forma de tamanho fixo |
| 255 | [`255_resultado_e_reflexao.df`](38-tipos/255_resultado_e_reflexao.df) · [doc](38-tipos/255_resultado_e_reflexao.md) | A falha como valor, e a reflexao de tipos |
| 256 | [`256_posse_e_recursos.df`](38-tipos/256_posse_e_recursos.df) · [doc](38-tipos/256_posse_e_recursos.md) | Posse, emprestimo e liberacao deterministica |

## 39 — Concorrencia avancada

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 257 | [`257_stm_e_atomicos.df`](39-concorrencia-avancada/257_stm_e_atomicos.df) · [doc](39-concorrencia-avancada/257_stm_e_atomicos.md) | Memoria transacional, CAS e estruturas sem trava |

## 40 — Metaprogramacao

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 258 | [`258_comptime_e_macros.df`](40-metaprogramacao/258_comptime_e_macros.df) · [doc](40-metaprogramacao/258_comptime_e_macros.md) | comptime, macros, DSL e plugin do check |

## 41 — Ffi nativo

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 259 | [`259_ffi_com_c.df`](41-ffi-nativo/259_ffi_com_c.df) · [doc](41-ffi-nativo/259_ffi_com_c.md) | chamar C: bibliotecas, ponteiros e callbacks |

## 42 — Compilador

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 260 | [`260_pipeline_hir_mir.df`](42-compilador/260_pipeline_hir_mir.df) · [doc](42-compilador/260_pipeline_hir_mir.md) | dentro do compilador: HIR, MIR e o que o fluxo prova |

## 43 — Backend

*1 exercícios · com documentação `.md`*

| # | Exercício | Assunto |
|---|-----------|---------|
| 261 | [`261_ssa_e_otimizacao.df`](43-backend/261_ssa_e_otimizacao.df) · [doc](43-backend/261_ssa_e_otimizacao.md) | SSA, o no phi, e a otimizacao que foi MEDIDA |

---

**Total: 261 exercícios.** Todos passam — o estado esperado do repositório é verde. Se algum falhar, é regressão no interpretador: veja
[`../CLAUDE.md`](../CLAUDE.md).

<!-- indice:fim -->

## Depois dos exercícios

- [`../doc/REFERENCIA.md`](../doc/REFERENCIA.md) — a gramática completa
- [`../doc/BIBLIOTECA_PADRAO.md`](../doc/BIBLIOTECA_PADRAO.md) — os 20 módulos
- [`../doc/ANALISE_E_ROADMAP.md`](../doc/ANALISE_E_ROADMAP.md) — o que falta implementar
- [`../examples/`](../examples) — 42 programas maiores
