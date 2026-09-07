# Exercicio 151 — Módulos com `adopt` e `relay`

## Enunciado

Importe um módulo local e comprove que `relay` controla de verdade o que sai
dele.

## Conceitos

### Importar

```dataforge
adopt geometria as geo          // arquivo geometria.df ao lado
adopt Arcane.Math as Math       // biblioteca padrão
```

A resolução segue esta ordem:

1. módulos já carregados (cache — um arquivo só executa uma vez)
2. biblioteca padrão (`Arcane.*` e os nomes curtos)
3. arquivo `.df` **ao lado do arquivo que importa**

O terceiro ponto importa: o caminho é relativo ao arquivo, não ao diretório de
onde você rodou o comando. Isso faz um projeto funcionar igual sendo executado da
raiz ou de dentro de uma subpasta.

### Exportar

```dataforge
relay PI, area_circulo, perimetro_circulo, area_retangulo
```

A regra tem dois casos:

| No módulo | Exporta |
|-----------|---------|
| nenhum `relay` | tudo do nível superior |
| pelo menos um `relay` | só o que foi listado |

Sem `relay`, você tem a conveniência de um script. Com `relay`, tem uma
**interface pública** — e o que ficou de fora é detalhe de implementação que você
pode reescrever sem quebrar ninguém.

## Por que isso vale a pena

Em `geometria.df` existe uma ação `_arredondar` que não está no `relay`.
Tentar usá-la falha:

```
bloqueado: Vault has no key '_arredondar'
```

Essa é a diferença entre "por convenção não use isso" (o `_` do Python) e "isso
não está acessível". A segunda é verificável.

## Módulo inexistente

```dataforge
adopt Arcane.NaoExiste as x
// ImportError_: Module 'Arcane.NaoExiste' not found. Available: ...
```

A mensagem lista o que existe. Antes do 4.0 isso devolvia um dicionário vazio e o
erro só aparecia páginas adiante, como `NameError` — um dos bugs corrigidos nesta
versão.

## Saída esperada

```
3.14159265
circulo de raio 2: 12.5664
retangulo 3x4: 12
bloqueado: Vault has no key '_arredondar'
erro: ImportError
sqrt(144) = 12.0
```

## Experimente

- Remova a linha `relay` de `geometria.df` e veja `_arredondar` ficar acessível.
- Crie `circulo.df` que importa `geometria` e reexporta só a parte de círculos.
