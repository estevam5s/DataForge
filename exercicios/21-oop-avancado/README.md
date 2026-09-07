# Módulo 21 — OOP avançado

Dez exercícios sobre o que o DataForge 4.1 trouxe para orientação a objetos:
campos declarados, métodos estáticos, propriedades, visibilidade, sobrecarga de
operadores, abstratos e contratos de trait.

```bash
python3 exercicios/run_all.py 21
```

| # | Exercício | O que ensina |
|---|-----------|--------------|
| 181 | [Campos declarados](181_campos_declarados.md) | tipo e padrão no corpo do blueprint |
| 182 | [Métodos estáticos](182_metodos_estaticos.md) | construtor alternativo, constante da família |
| 183 | [Propriedades](183_propriedades.md) | `get`/`set`, validação na escrita |
| 184 | [Visibilidade](184_visibilidade.md) | `private` e `protected` que valem de verdade |
| 185 | [Sobrecarga de operadores](185_sobrecarga_operadores.md) | `+`, `==` no seu próprio tipo |
| 186 | [Abstratos e traits](186_abstratos_e_traits.md) | contrato conferido na declaração |
| 187 | [Herança e root](187_heranca_e_root.md) | estender sem reimplementar, `final` |
| 188 | [Composição](188_composicao.md) | quando *ter* é melhor que *ser* |
| 189 | [Records vs blueprints](189_records_vs_blueprints.md) | valor ou identidade |
| 190 | [Polimorfismo](190_polimorfismo.md) | acrescentar tipo sem editar quem usa |

## A ordem importa

Os exercícios se apoiam uns nos outros: 181 a 185 são as ferramentas novas, 186
a 190 são as decisões de modelagem que elas permitem. Fazer 188 antes de 186
funciona, mas a discussão sobre herança e composição fica mais clara depois de
ver o contrato de trait em ação.
