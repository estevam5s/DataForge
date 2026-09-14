"""O painel e o esquema do banco não podem divergir.

Três páginas estavam quebradas EM PRODUÇÃO, e a mensagem era sempre a
mesma forma:

    /painel/trechos     column trechos.linguagem does not exist
    /painel/anotacoes   column anotacoes.titulo does not exist
    /painel/exercicios  column progresso.modulo does not exist

Nada acusava. A consulta só falha quando alguém abre a página, e o erro
aparece na tela de quem usa — não no `tsc`, não no `next build`, não na
suíte. O TypeScript confere o formato do objeto em TypeScript; ele não
tem como saber o que existe no Postgres.

Este teste lê as duas fontes e compara:

    site/lib/supabase/*.ts      o que o site pede
    supabase/*.sql              o que o banco tem

É comparação de MAPA com MAPA — não vai ao território. Ir ao banco
exigiria credencial na CI, e um teste que só roda com segredo é um
teste que não roda. O que ele pega é a divergência introduzida ao
escrever código, que é quando ela é barata de corrigir.
"""

import os
import re
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)


def _colunas_do_esquema():
    """Tabela -> colunas, lendo os .sql na ordem em que são aplicados."""
    tabelas = {}
    pasta = os.path.join(RAIZ, "supabase")
    if not os.path.isdir(pasta):
        return tabelas

    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".sql"):
            continue
        texto = open(os.path.join(pasta, nome), encoding="utf-8").read()

        # create table … ( … );
        for m in re.finditer(
                r"create table if not exists public\.(\w+)\s*\((.*?)\n\);",
                texto, re.S):
            tabela, corpo = m.group(1), m.group(2)
            colunas = set()
            for linha in corpo.splitlines():
                linha = linha.strip()
                if not linha or linha.startswith("--"):
                    continue
                # 'primary key (a, b)' e 'check (…)' não declaram coluna
                if re.match(r"(primary key|unique|check|constraint|foreign)\b",
                            linha, re.I):
                    continue
                casou = re.match(r"(\w+)\s+\S", linha)
                if casou:
                    colunas.add(casou.group(1))
            tabelas.setdefault(tabela, set()).update(colunas)

        # alter table … add column if not exists x
        for m in re.finditer(
                r"alter table public\.(\w+)\s+add column if not exists (\w+)",
                texto, re.S):
            tabelas.setdefault(m.group(1), set()).add(m.group(2))

        # As VISÕES também são consultadas pelo site ('placar',
        # 'problemas_publicos'), e para o PostgREST são indistinguíveis
        # de uma tabela. As colunas delas saem do 'select' que as
        # define, e por isso a conferência aqui é só de EXISTÊNCIA: um
        # 'select *' não nomeia coluna nenhuma, e inventar as que ele
        # traria daria falso alarme nos dois sentidos.
        for m in re.finditer(
                r"create (?:or replace )?view public\.(\w+)", texto):
            tabelas.setdefault(m.group(1), set()).add("*")

    return tabelas


def _colunas_que_o_site_pede():
    """Tabela -> colunas citadas em select, insert, upsert, eq e order."""
    pedidas = {}
    pasta = os.path.join(RAIZ, "site", "lib", "supabase")
    if not os.path.isdir(pasta):
        return pedidas

    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".ts"):
            continue
        texto = open(os.path.join(pasta, nome), encoding="utf-8").read()

        # Cada '.from(...)' até o próximo — sem janela de tamanho fixo,
        # que foi o que deixou 'trechos.linguagem' passar na primeira
        # varredura que escrevi.
        partes = re.split(r"\.from\('(\w+)'\)", texto)
        for i in range(1, len(partes), 2):
            tabela, corpo = partes[i], partes[i + 1]
            # Para no fim da cadeia: a próxima função que não é do query
            # builder encerra o encadeamento.
            corpo = corpo.split("\n}")[0]
            alvo = pedidas.setdefault(tabela, set())

            for sel in re.finditer(r"\.select\(\s*'([^']*)'", corpo):
                for coluna in sel.group(1).split(","):
                    coluna = coluna.strip().split("(")[0].split(":")[0].strip()
                    if coluna and coluna != "*" and re.fullmatch(r"\w+", coluna):
                        alvo.add(coluna)

            for ins in re.finditer(
                    r"\.(?:insert|update|upsert)\(\s*\{([^}]*)\}", corpo):
                for coluna in re.finditer(r"(\w+)\s*:", ins.group(1)):
                    alvo.add(coluna.group(1))

            for filtro in re.finditer(
                    r"\.(?:eq|neq|gt|lt|gte|lte|order|is|in)\(\s*'(\w+)'",
                    corpo):
                alvo.add(filtro.group(1))

            for conflito in re.finditer(r"onConflict:\s*'([^']*)'", corpo):
                for coluna in conflito.group(1).split(","):
                    if coluna.strip():
                        alvo.add(coluna.strip())
    return pedidas


def test_toda_coluna_que_o_painel_pede_existe_no_esquema():
    esquema = _colunas_do_esquema()
    if not esquema:
        pytest.skip("os .sql não estão neste checkout")

    pedidas = _colunas_que_o_site_pede()
    if not pedidas:
        pytest.skip("o site não está neste checkout")

    faltando = []
    for tabela, colunas in sorted(pedidas.items()):
        if tabela not in esquema:
            faltando.append(f"{tabela}: a TABELA não existe no esquema")
            continue
        if "*" in esquema[tabela]:
            continue        # visão: conferida só por existir
        for coluna in sorted(colunas - esquema[tabela]):
            faltando.append(f"{tabela}.{coluna}")

    assert not faltando, (
        "o painel consulta colunas que o banco não tem — a página quebra "
        "para quem a abrir, e nem o tsc nem o build acusam:\n  "
        + "\n  ".join(faltando))


def test_o_dono_de_uma_linha_chama_se_dono_id():
    """Uma tabela com `usuario_id` divergiria das políticas de RLS.

    Todas elas comparam `dono_id = auth.uid()`. Uma tabela que chamasse
    a coluna de outra coisa precisaria de uma política escrita à mão, e
    a que fosse esquecida ficaria **aberta** — o modo mais silencioso de
    vazar dado de usuário.

    Era o que o site escrevia em três consultas, e por isso elas
    falhavam.
    """
    esquema = _colunas_do_esquema()
    if not esquema:
        pytest.skip("os .sql não estão neste checkout")

    erradas = [t for t, colunas in esquema.items() if "usuario_id" in colunas]
    assert not erradas, (
        "estas tabelas chamam o dono de 'usuario_id', e as políticas de "
        f"RLS comparam 'dono_id': {', '.join(sorted(erradas))}")

    pedidas = _colunas_que_o_site_pede()
    no_site = [t for t, colunas in pedidas.items() if "usuario_id" in colunas]
    assert not no_site, (
        "o site escreve 'usuario_id' nestas tabelas, e a coluna chama-se "
        f"'dono_id': {', '.join(sorted(no_site))}")
