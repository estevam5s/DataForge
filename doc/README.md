# Documentação DataForge

## Comece aqui

| Documento | Para quem |
|-----------|-----------|
| [**INSTALACAO.md**](INSTALACAO.md) | Instalar e preparar o ambiente, do zero |
| [**TUTORIAL.md**](TUTORIAL.md) | Aprender a linguagem inteira, com exemplos que rodam |
| [**REFERENCIA.md**](REFERENCIA.md) | Consultar gramática, palavras-chave, precedência e semântica |
| [**BIBLIOTECA_PADRAO.md**](BIBLIOTECA_PADRAO.md) | Assinaturas de todos os módulos `Arcane.*` |
| [**ANALISE_E_ROADMAP.md**](ANALISE_E_ROADMAP.md) | Estado técnico do projeto e o que falta implementar |
| [**KILN.md**](KILN.md) | O framework web: rotas, templates, middleware e o que ele não tem |
| [**OOP.md**](OOP.md) | Orientação a objetos: blueprints, traits, propriedades e métodos mágicos |

Além destes:

- [`../exercicios/`](../exercicios) — 216 exercícios; os dos módulos 11-23 com `.md` explicativo
- [`../examples/`](../examples) — 43 programas maiores
- [`../CLAUDE.md`](../CLAUDE.md) — contexto para trabalhar no interpretador

## Manutenção

`BIBLIOTECA_PADRAO.md` é **gerado** a partir do código. Depois de alterar
`dataforge/stdlib/`, regenere:

```bash
python3 tools/gerar_doc_stdlib.py
```

Ao mudar `KEYWORDS` em `dataforge/tokens.py`, sincronize a lista em
`REFERENCIA.md` §1.6 — há um teste que compara as duas
(`test_referencia_lista_exatamente_as_palavras_reservadas`). O mesmo vale para a
§13 e as funções de `builtins.py`.

Ao criar um módulo `Arcane.*` novo, registre-o em `dataforge/stdlib/__init__.py`
**e** no dicionário `DESCRICOES` de `tools/gerar_doc_stdlib.py`.

## Documentos históricos

Os arquivos abaixo descrevem versões anteriores ou direções abandonadas e trazem
um aviso no topo. Não use como referência:

`SPECIFICATION.md` · `DOCUMENTATION.md` · `INSTALL.md` · `INSTALACAO_PT-BR.md` ·
`DATAFORGE_ANALYSIS.md` · `DATAFORGE_LANGUAGE_SPEC.md` · `PUBLISHING_GUIDE.md` ·
`LANGUAGE_SPEC.md` · `TYPES.md` · `TYPE_erros.md` · `linguagem.md`

`DATAFORGE_LANGUAGE_SPEC.md` merece nota à parte: é uma **proposta** anterior à
implementação, e descreve uma linguagem diferente desta. Das 31 palavras
reservadas que propõe, 23 vêm de Rust ou de JavaScript — e a regra deste projeto
é que as palavras da DataForge não saiam de outra linguagem.

## Material de origem

Não são documentação da linguagem: são os textos que **serviram de fonte** para
o que foi implementado. Ficam aqui para que se possa conferir o que foi
adaptado, e não como referência de uso.

`engenharia_dados_python.md` · `conteudos-servidor.md` ·
`servidor-framework-web.md` · `tasks.md`
