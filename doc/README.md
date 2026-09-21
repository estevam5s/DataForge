# Documentação DataForge

## Comece aqui

| Documento | Para quem |
|-----------|-----------|
| [**INSTALACAO.md**](INSTALACAO.md) | Instalar e preparar o ambiente, do zero |
| [**TUTORIAL.md**](TUTORIAL.md) | Aprender a linguagem inteira, com exemplos que rodam |
| [**REFERENCIA.md**](REFERENCIA.md) | Consultar gramática, palavras-chave, precedência e semântica |
| [**BIBLIOTECA_PADRAO.md**](BIBLIOTECA_PADRAO.md) | Assinaturas de todos os módulos `Arcane.*` |
| [**ANALISE_E_ROADMAP.md**](ANALISE_E_ROADMAP.md) | Estado técnico do projeto e o que falta implementar |
| [**METAS_DO_TODO.md**](METAS_DO_TODO.md) | As metas do `TODO.md` cruzadas com o que já existe: o que está feito, o que foi decidido não fazer, e os cinco que cabem |
| [**KILN.md**](KILN.md) | O framework web: rotas, templates, middleware e o que ele não tem |
| [**VITRINE.md**](VITRINE.md) | O framework de dashboards: um programa de cima para baixo vira uma página web |
| [**OOP.md**](OOP.md) | Orientação a objetos como sistema: modelo, modificadores, contratos, metaclasses, reflexão, DI, SOLID — e o mapa do que existe |
| [**ESTABILIDADE.md**](ESTABILIDADE.md) | O que pode quebrar entre versões, e o que não — verificado por teste |
| [**DataForge_Analise_ETL_Engenharia_de_Dados.md**](DataForge_Analise_ETL_Engenharia_de_Dados.md) | Ensaio: a linguagem vista por quem faz engenharia de dados — o que ela cobre de um pipeline de ponta a ponta, e onde ela para |

Além destes:

- [`../exercicios/`](../exercicios) — 387 exercícios; os dos módulos 11-23 com `.md` explicativo
- [`../examples/`](../examples) — 44 programas maiores
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

## Gerado — não edite à mão

`superficie.json` é a foto do que é público, produzida por
`scripts/gerar_superficie.py`. Ela é o que dá dente à promessa de
`ESTABILIDADE.md`: `tests/test_estabilidade.py` falha quando um símbolo
some dela.

## Material de origem

Não são documentação da linguagem: são os textos que **serviram de fonte** para
o que foi implementado. Ficam aqui para que se possa conferir o que foi
adaptado, e não como referência de uso.

`engenharia_dados_python.md` · `conteudos-servidor.md` ·
`servidor-framework-web.md` · `tasks.md`

Os cinco abaixo são a fonte das metas abertas em `TODO.md` — o que ainda
**não** foi implementado. Eles descrevem recursos na forma de outras
linguagens (Node.js, Python), e implementá-los significa adaptar cada um à
sintaxe da DataForge. Não use a sintaxe deles como referência:

`dataforge_completo_avancado_dataforge.md` · `dataforge_do_basico_ao_avancado.md` ·
`dataforge_arquitetura_avan_ada_e_big_o (1).md` · `dataforge-stream-framework.md` ·
`dataforge-stream-devops.md`

E estes quatro são material de estudo e de direcionamento, recebidos como
fonte. `DataForge_Deep_Tech_Consolidada.md` e `DataForge_OOP_SOLID_Metaclasses.md`
descrevem o que a linguagem tem por dentro; `instrucoes_arquiteto_dataforge.md`
traz a direção de arquitetura; `streamlit.md` é a referência que originou a
[Vitrine](/docs/vitrine) — e a Vitrine **não é** um Streamlit em DataForge, é
outra coisa com o mesmo problema a resolver:

`DataForge_Deep_Tech_Consolidada.md` · `DataForge_OOP_SOLID_Metaclasses.md` ·
`instrucoes_arquiteto_dataforge.md` · `streamlit.md`

E `DATAFORGE_CYBER_SECURITY.md`, na raiz do repositório, é a fonte da
[seção de segurança da informação](/docs/seguranca/mapa) e dos módulos
`Arcane.Politica`, `Arcane.Chaves` e `Arcane.Deteccao`. Ele lista 61 frentes;
a documentação diz, para cada uma, o que existe aqui e o que **não** existe.
