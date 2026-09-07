# Documentação DataForge

## Comece aqui

| Documento | Para quem |
|-----------|-----------|
| [**INSTALACAO.md**](INSTALACAO.md) | Instalar e preparar o ambiente, do zero |
| [**TUTORIAL.md**](TUTORIAL.md) | Aprender a linguagem inteira, com exemplos que rodam |
| [**REFERENCIA.md**](REFERENCIA.md) | Consultar gramática, palavras-chave, precedência e semântica |
| [**BIBLIOTECA_PADRAO.md**](BIBLIOTECA_PADRAO.md) | Assinaturas de todos os módulos `Arcane.*` |
| [**ANALISE_E_ROADMAP.md**](ANALISE_E_ROADMAP.md) | Estado técnico do projeto e o que falta implementar |

Além destes:

- [`../exercicios/`](../exercicios) — 120 exercícios comentados e verificados
- [`../examples/`](../examples) — 42 programas maiores
- [`../CLAUDE.md`](../CLAUDE.md) — contexto para trabalhar no interpretador

## Manutenção

`BIBLIOTECA_PADRAO.md` é **gerado** a partir do código. Depois de alterar
`dataforge/stdlib/`, regenere:

```bash
python3 tools/gerar_doc_stdlib.py
```

Ao mudar `KEYWORDS` em `dataforge/tokens.py`, sincronize a lista em
`REFERENCIA.md` §1.6 — há um teste que compara as duas.

## Documentos históricos

Os arquivos abaixo descrevem versões anteriores ou direções abandonadas e trazem
um aviso no topo. Não use como referência:

`SPECIFICATION.md` · `DOCUMENTATION.md` · `INSTALL.md` · `INSTALACAO_PT-BR.md` ·
`DATAFORGE_ANALYSIS.md` · `PUBLISHING_GUIDE.md` · `../LANGUAGE_SPEC.md` ·
`../TYPES.md` · `../TYPE_erros.md` · `../linguagem.md`
