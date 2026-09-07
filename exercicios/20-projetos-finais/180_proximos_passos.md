# Exercicio 180 — Encerramento e próximos passos

## O que você percorreu

180 exercícios em 20 módulos, do `out "Ola"` a um interpretador de expressões com
lexer, parser e avaliador próprios.

### Módulos 1–10: a base

Fundamentos, controle de fluxo, coleções, textos, ações, blueprints, tratamento
de erros, pipelines, módulos e concorrência.

### Módulos 11–20: DataForge 4.0

Tipos verificados, análise estática, records, enums, desestruturação, pattern
matching, generators, sistema de módulos, tempo e sistema, persistência,
concorrência e seis projetos integradores.

## O que a linguagem tem hoje

| Área | Recursos |
|------|----------|
| **Tipos** | anotações opcionais verificadas, `typeof`, `cast`, análise estática |
| **Dados** | records imutáveis, enums, clusters, vaults, compreensões |
| **Fluxo** | `given`/`orif`/`otherwise`, `match` estrutural, quatro laços |
| **Ações** | padrões, tipos, closures, lambdas, decoradores, `defer` |
| **Erros** | `handle` tipado, `guard`, `retry`, `propagate`, stack traces |
| **Fluxos** | pipelines, `stream action` com avaliação preguiçosa |
| **Módulos** | `adopt` seletivo, `relay`, detecção de ciclos, `forge.toml` |
| **Stdlib** | 20 módulos `Arcane.*` |
| **Ferramentas** | `check`, `test`, `fmt`, `lint`, `doc`, `repl`, `init` |

## O que ainda não existe

Ser honesto sobre isso é parte de conhecer a ferramenta:

- **Generics** — `Cluster<T>` e ações genéricas
- **Exaustividade** — avisar quando um membro de enum ficou fora do `match`
- **Contrato de trait** — verificar que o blueprint implementou tudo
- **LSP** — autocomplete e ir-para-definição no editor
- **Debugger** — breakpoints e inspeção passo a passo
- **Gerenciador de pacotes** — `dataforge add`, registry, lockfile
- **Bytecode** — VM própria no lugar do interpretador de árvore
- **Sincronização** — mutex e semáforo entre threads

O plano completo está em `doc/ANALISE_E_ROADMAP.md`.

## O ciclo de trabalho

```bash
dataforge init                # começar um projeto
dataforge check src/          # nomes, tipos, aridade
dataforge lint src/           # estilo e higiene
dataforge fmt src/            # formatar
dataforge test tests/ -v      # testes
dataforge doc src/ --out=doc/API.md
dataforge run                 # executar
```

Em integração contínua:

```bash
dataforge fmt . --check && dataforge check . && dataforge test
```

## Desafios para continuar

**Fácil**
- Jogo da velha em terminal
- Conversor de unidades com enum e records

**Médio**
- Gerenciador de tarefas com banco e CLI
- Cliente de API com retry e cache
- Gerador de sites estáticos a partir de markdown

**Difícil**
- Linguagem de consulta sobre CSV (`SELECT nome WHERE idade > 30`)
- Servidor HTTP com rotas, autenticação e persistência
- Type checker para o mini interpretador do exercício 177

Esse último é especialmente interessante: você já escreveu o interpretador;
acrescentar verificação de tipos a ele é o mesmo caminho que o DataForge
percorreu do 3.0 para o 4.0.

## Documentação

| Documento | Para |
|-----------|------|
| [`doc/TUTORIAL.md`](../../doc/TUTORIAL.md) | a linguagem do zero |
| [`doc/REFERENCIA.md`](../../doc/REFERENCIA.md) | gramática e semântica |
| [`doc/BIBLIOTECA_PADRAO.md`](../../doc/BIBLIOTECA_PADRAO.md) | os módulos `Arcane.*` |
| [`doc/ANALISE_E_ROADMAP.md`](../../doc/ANALISE_E_ROADMAP.md) | estado técnico e roadmap |
| [`CLAUDE.md`](../../CLAUDE.md) | trabalhar no interpretador |

## Rodando tudo

```bash
python3 exercicios/run_all.py         # os 180
python3 exercicios/run_all.py 14      # um módulo
python3 -m pytest tests/ -q           # a suíte do interpretador
```

## Contribuir

O roadmap tem itens de todos os tamanhos. Os mais acessíveis para começar:

- Verificação de exaustividade em `match` sobre enum
- Contrato de trait no analisador estático
- Novas funções nos módulos `Arcane.*`
- Mais exercícios

Cada recurso novo pede: sintaxe documentada, teste de regressão, exercício
didático e a suíte existente continuando verde.
