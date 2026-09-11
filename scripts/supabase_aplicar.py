#!/usr/bin/env python3
"""
Aplica as migrações de supabase/ no projeto.

    python3 scripts/supabase_aplicar.py            # aplica tudo
    python3 scripts/supabase_aplicar.py 03         # só a 03
    python3 scripts/supabase_aplicar.py --estado   # o que já existe lá

As credenciais vêm de `.supabase.local` (gitignored) ou do ambiente.
Nunca as passe por argumento: argv aparece em `ps` para qualquer
processo da máquina.

Por que a Management API e não o `psql`: a rede aqui pode não alcançar a
porta 5432 do Postgres, e a API HTTP passa por onde o resto do trabalho
já passa. O token `sbp_` que ela exige é de gestão — vive fora do site e
nunca vai para o navegador.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__))))
# A saida deste script tambem desenha, e precisa sobreviver a um
# terminal que nao fala UTF-8 — o cano do Windows e cp1252, que
# nao tem um unico dos tracos usados aqui.
from dataforge import marca  # noqa: E402

marca.preparar_saida()

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRACOES = os.path.join(RAIZ, "supabase")
SEGREDOS = os.path.join(RAIZ, ".supabase.local")

VERDE, VERMELHO, AMARELO, CINZA, LIMPO = (
    "\033[1;32m", "\033[1;31m", "\033[1;33m", "\033[0;90m", "\033[0m")


def carregar_segredos():
    """Lê .supabase.local sem exportar nada para processos filhos."""
    valores = dict(os.environ)
    if os.path.isfile(SEGREDOS):
        with open(SEGREDOS, encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                chave, _, valor = linha.partition("=")
                valores.setdefault(chave.strip(), valor.strip())

    faltando = [c for c in ("SUPABASE_ACCESS_TOKEN", "SUPABASE_PROJECT_REF")
                if not valores.get(c)]
    if faltando:
        raise SystemExit(
            f"{VERMELHO}faltam credenciais: {', '.join(faltando)}{LIMPO}\n"
            f"crie {os.path.relpath(SEGREDOS, RAIZ)} com:\n"
            f"  SUPABASE_ACCESS_TOKEN=sbp_…\n"
            f"  SUPABASE_PROJECT_REF=…")
    return valores


def executar(sql, segredos):
    """Roda SQL pela Management API. Devolve as linhas, ou levanta."""
    ref = segredos["SUPABASE_PROJECT_REF"]
    pedido = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        data=json.dumps({"query": sql}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {segredos['SUPABASE_ACCESS_TOKEN']}",
            "Content-Type": "application/json",
            # Sem User-Agent proprio, o WAF na frente da API recusa com
            # "error code: 1010" — que nao diz nada sobre o SQL.
            "User-Agent": "dataforge-migracoes/1.0",
        },
        method="POST")
    try:
        with urllib.request.urlopen(pedido, timeout=180) as resposta:
            corpo = resposta.read().decode("utf-8")
            return json.loads(corpo) if corpo.strip() else []
    except urllib.error.HTTPError as erro:
        detalhe = erro.read().decode("utf-8", errors="replace")
        try:
            detalhe = json.loads(detalhe).get("message", detalhe)
        except json.JSONDecodeError:
            pass
        raise RuntimeError(detalhe) from None


def arquivos(filtro=None):
    nomes = sorted(n for n in os.listdir(MIGRACOES) if n.endswith(".sql"))
    if filtro:
        nomes = [n for n in nomes if n.startswith(filtro)]
    return nomes


def mostrar_estado(segredos):
    print(f"\n  {CINZA}projeto {segredos['SUPABASE_PROJECT_REF']}{LIMPO}\n")

    tabelas = executar(
        "select table_name,"
        "  (select count(*) from information_schema.columns c"
        "    where c.table_name = t.table_name and c.table_schema='public')"
        "    as colunas"
        " from information_schema.tables t"
        " where table_schema='public' and table_type='BASE TABLE'"
        " order by 1", segredos)
    print(f"  {len(tabelas)} tabela(s)")
    for linha in tabelas:
        print(f"    {CINZA}·{LIMPO} {linha['table_name']:<24} "
              f"{CINZA}{linha['colunas']} colunas{LIMPO}")

    politicas = executar(
        "select tablename, count(*) as n from pg_policies"
        " where schemaname='public' group by 1 order by 1", segredos)
    total = sum(p["n"] for p in politicas)
    print(f"\n  {total} política(s) de RLS em {len(politicas)} tabela(s)")

    sem_rls = executar(
        "select c.relname from pg_class c"
        " join pg_namespace n on n.oid = c.relnamespace"
        " where n.nspname='public' and c.relkind='r' and not c.relrowsecurity"
        " order by 1", segredos)
    if sem_rls:
        print(f"  {VERMELHO}sem RLS: "
              f"{', '.join(l['relname'] for l in sem_rls)}{LIMPO}")
    elif tabelas:
        print(f"  {VERDE}toda tabela tem RLS ligada{LIMPO}")

    try:
        jobs = executar("select jobname, schedule, active from cron.job"
                        " order by jobname", segredos)
        print(f"\n  {len(jobs)} tarefa(s) agendada(s)")
        for j in jobs:
            marca = VERDE + "ativa" if j["active"] else CINZA + "parada"
            print(f"    {CINZA}·{LIMPO} {j['jobname']:<28} "
                  f"{j['schedule']:<16} {marca}{LIMPO}")
    except RuntimeError:
        print(f"\n  {CINZA}pg_cron ainda não instalado{LIMPO}")
    print()


def main():
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    segredos = carregar_segredos()

    if "--estado" in sys.argv:
        mostrar_estado(segredos)
        return

    filtro = argumentos[0] if argumentos else None
    nomes = arquivos(filtro)
    if not nomes:
        raise SystemExit(f"nenhuma migração encontrada em supabase/{filtro or ''}")

    print(f"\n  {CINZA}projeto {segredos['SUPABASE_PROJECT_REF']}{LIMPO}\n")
    falhou = False
    for nome in nomes:
        caminho = os.path.join(MIGRACOES, nome)
        with open(caminho, encoding="utf-8") as f:
            sql = f.read()
        linhas = len([l for l in sql.split("\n") if l.strip()])
        try:
            executar(sql, segredos)
            print(f"  {VERDE}✓{LIMPO} {nome:<28} {CINZA}{linhas} linhas{LIMPO}")
        except RuntimeError as erro:
            falhou = True
            print(f"  {VERMELHO}✗{LIMPO} {nome}")
            for linha in str(erro).strip().split("\n")[:6]:
                print(f"      {VERMELHO}{linha}{LIMPO}")

    print()
    if falhou:
        raise SystemExit(1)
    mostrar_estado(segredos)


if __name__ == "__main__":
    main()
