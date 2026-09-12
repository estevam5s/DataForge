# Contribuir

Obrigado por olhar. Este documento é curto de propósito: o que você
precisa saber para o primeiro patch, e nada além disso.

## Antes de qualquer coisa

```bash
git clone https://github.com/estevam5s/DataForge && cd DataForge
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python3 -m pytest tests/ -q         # tudo verde é o estado esperado
python3 exercicios/run_all.py
```

Se algo falhar **antes** da sua mudança, isso é um bug nosso — abra uma
questão em vez de tentar contornar.

## As três regras que não se negociam

**1. Zero dependências no runtime.** Nada em `dataforge/` importa nada
de fora da biblioteca padrão do Python. Ferramenta de desenvolvimento
(`pytest`, `pyinstaller`) é outra coisa e vive no `[dev]`.

Se você precisa de uma biblioteca para o que está escrevendo, a resposta
provavelmente é [a ponte](https://dataforge-lang.vercel.app/docs/tecnicas/ponte):
o *programa de quem usa* pode depender do numpy; a linguagem, não.

**2. As palavras reservadas não vêm de outra linguagem.** `given`, não
`if`. `action`, não `fn`. `blueprint`, não `class`. Uma proposta com
`let`, `mut` ou `impl` vai ser recusada, e isso não é gosto: é a única
coisa que faz a DataForge ser uma linguagem em vez de um dialeto.

**3. Ao corrigir um bug, escreva primeiro o teste que falha.** Sem ele
não há como saber se a correção corrigiu, nem impedir que volte.

## Onde mexer

`CLAUDE.md` é o mapa completo — 700 linhas sobre o interpretador, as
armadilhas e as convenções. Leia a seção relevante antes de abrir o
arquivo.

O resumo:

| Você quer | Mexa em |
|---|---|
| um recurso da linguagem | `tokens.py` → `lexer.py` → `ast_nodes.py` + `parser.py` → `interpreter.py` → `typechecker.py` — **os cinco** |
| uma função de biblioteca | `dataforge/stdlib/`, e registre em `stdlib/__init__.py` **e** em `stdlib/catalogo.py` |
| uma mensagem de erro | ela deve dizer **o que fazer**, não só o que houve |
| desempenho | **meça antes.** `dataforge profile` num programa real. Duas otimizações "óbvias" já foram revertidas por medição |

## O que é gerado — não edite à mão

Sessenta e sete páginas de `/docs`, a gramática do editor, a
`BIBLIOTECA_PADRAO.md`, os índices e os dados do site. Elas avisam na
primeira linha. Editar o arquivo gerado funciona até alguém rodar o
gerador, e aí a correção some sem nada explicando.

A lista está em `CLAUDE.md`, seção "O que é gerado".

## Antes de abrir o PR

```bash
python3 -m pytest tests/ -q
python3 exercicios/run_all.py
python3 tools/verificar_docs.py
python3 -m dataforge fmt exercicios/ examples/ packages/ projetos/ --check
```

E se você mexeu em algo público — palavra reservada, função embutida,
símbolo de módulo, comando da CLI:

```bash
python3 scripts/gerar_superficie.py
```

Isso atualiza a foto de `doc/superficie.json`. **Acrescentar é livre**;
remover ou renomear precisa de uma versão maior, e a mudança tem que
aparecer no diff — ver [`doc/ESTABILIDADE.md`](doc/ESTABILIDADE.md).

## Mensagem de commit

Diga **o que estava errado** e **por que a correção é essa**, não só o
que você mudou. O `git log` deste repositório é a documentação de por
que as coisas são como são — vale olhar alguns antes de escrever o seu.

## Escrevendo em DataForge

As armadilhas que mais custam tempo estão em `CLAUDE.md`. As três
primeiras:

- `yield` **retorna**; para uma sequência use `stream action` + `emit`
- divisão inteira é `~/`, porque `//` é comentário
- só espaços na indentação, quatro por nível

Um exercício novo em `exercicios/` vale mais que um exemplo na
documentação: os 217 rodam a cada execução, e um que quebra é
descoberto no mesmo dia.
