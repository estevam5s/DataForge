#!/usr/bin/env python3
"""Gera doc/BIBLIOTECA_PADRAO.md a partir das assinaturas reais dos modulos Arcane.

Rode depois de mexer em dataforge/stdlib/ para manter a documentacao em sincronia:

    python3 tools/gerar_doc_stdlib.py
"""

import inspect
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

DESCRICOES = {
    "Arcane.Math": ("Matemática, álgebra linear e estatística básica.", "Math"),
    "Arcane.Text": ("Manipulação de texto, formatação, tabelas e conversão de caixa.", "Text"),
    "Arcane.Analytics": ("Análise de dados: estatística, regressão, clustering e gráficos ASCII.", "Analytics"),
    "Arcane.Functional": ("Utilitários funcionais: composição, lentes, Maybe/Either, transdutores.", "Functional"),
    "Arcane.Database": ("Banco de dados SQLite: tabelas, consultas, migrações e importação.", "Database / DB"),
    "Arcane.Excel": ("Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame.", "Excel / Xlsx"),
    "Arcane.Meta": ("Metadados de decorador: ler @Nome em tempo de execução.", "Meta"),
    "Kiln": ("Framework web: rotas, middleware, templates, sessão e arquivos estáticos.", "Kiln"),
    "Arcane.Test": ("Asserções e organização de suítes de teste.", "Test"),
    "Arcane.Regex": ("Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone).", "Regex"),
    "Arcane.IO": ("Arquivos, diretórios, JSON, CSV e shell.", "IO"),
    "Arcane.Http": ("Servidor HTTP: rotas, middleware, JSON, arquivos estáticos.", "Http / Server"),
    "Arcane.Async": ("Promessas, filas, agendamento e execução concorrente.", "Async"),
    "Arcane.Data": ("DataFrames, séries e transformações tabulares.", "Data"),
    "Arcane.Web": ("Cliente HTTP, URL encoding e JSON.", "Web / Network"),
    "Arcane.Cortex": ("Blocos de rede neural, visão e NLP (implementações simplificadas).", "Cortex"),

    # ── DataForge 4.0 ──
    "Arcane.Time": ("Datas, horas, durações e cronometragem.", "Time"),
    "Arcane.OS": ("Sistema operacional, ambiente, disco e processo atual.", "OS"),
    "Arcane.Process": ("Execução de processos externos, com stdout, stderr e código de saída.", "Process"),
    "Arcane.Logging": ("Registro estruturado de eventos, com níveis e destinos.", "Logging / Log"),
    "Arcane.Crypto": ("Hashes, HMAC, senhas, codificações e aleatoriedade segura.", "Crypto"),
    "Arcane.Collections": ("Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca.", "Collections"),
    "Arcane.Serialization": ("JSON, CSV, INI, TOML, XML e conversões entre eles.", "Serialization / Serde"),
}

CABECALHO = """# Biblioteca padrão DataForge — módulos `Arcane.*`

Referência gerada a partir das assinaturas reais do código
(`python3 tools/gerar_doc_stdlib.py`). Todo módulo é carregado com `adopt`:

```dataforge
adopt Arcane.Math as Math
out Math.sqrt(16)
```

Cada módulo tem um **nome curto** equivalente (`adopt Math as M` funciona igual).

## Índice

| Módulo | Nome curto | Símbolos | Para quê |
|--------|-----------|----------|----------|"""

RODAPE_INDICE = """
> Os nomes curtos e os aliases (`DB`, `Server`, `Network`) apontam para o mesmo
> módulo — use o que ficar mais legível.

## Exemplos rápidos

```dataforge
adopt Arcane.Math as Math
adopt Arcane.Text as Text
adopt Arcane.Analytics as An

out Math.sqrt(16)                       // 4.0
out Math.is_prime(97)                   // yes
out Text.slug("Ola Mundo")              // ola-mundo
out Text.box("Relatorio")               // caixa desenhada
out An.correlation([1,2,3], [2,4,6])    // 1.0
```
"""


def assinatura(valor):
    """Devolve (assinatura, None) para funcoes e (None, valor) para constantes."""
    if not callable(valor):
        texto = repr(valor)
        return None, (texto[:50] + "…" if len(texto) > 50 else texto)
    try:
        sig = str(inspect.signature(valor))
    except (TypeError, ValueError):
        sig = "(…)"
    return sig.replace(", /", "").replace("(/)", "()").replace("/, ", ""), None


def main():
    partes = [CABECALHO]
    corpos = []

    for nome, (descricao, curto) in DESCRICOES.items():
        modulo = get_module(nome)
        if modulo is None:
            print(f"AVISO: modulo {nome} nao carregou", file=sys.stderr)
            continue
        itens = sorted(k for k in modulo if not k.startswith("__"))
        ancora = nome.lower().replace(".", "")
        partes.append(f"| [`{nome}`](#{ancora}) | `{curto}` | {len(itens)} | {descricao} |")

        corpo = [
            f"\n---\n\n## {nome}\n\n{descricao}\n",
            f"```dataforge\nadopt {nome} as {curto.split(' / ')[0]}\n```\n",
        ]
        constantes, funcoes = [], []
        for chave in itens:
            sig, valor = assinatura(modulo[chave])
            if sig is None:
                constantes.append(f"| `{chave}` | `{valor}` |")
            else:
                funcoes.append(f"| `{chave}{sig}` |")

        if constantes:
            corpo.append("**Constantes**\n\n| Nome | Valor |\n|------|-------|")
            corpo.extend(constantes)
            corpo.append("")
        if funcoes:
            corpo.append(f"**Funções ({len(funcoes)})**\n\n| Assinatura |\n|------------|")
            corpo.extend(funcoes)
            corpo.append("")
        corpos.append("\n".join(corpo))

    partes.append(RODAPE_INDICE)
    partes.extend(corpos)

    destino = os.path.join(RAIZ, "doc", "BIBLIOTECA_PADRAO.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))
    print(f"gerado: {destino}")


if __name__ == "__main__":
    main()
