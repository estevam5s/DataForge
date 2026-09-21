# -*- coding: utf-8 -*-
"""O que foi ESCRITO a mao na pagina de time.

As tabelas de constantes e de funcoes NAO estao aqui: elas
saem do modulo a cada geracao. Escritas a mao, elas
envelheciam sem ninguem ver — a de Arcane.Regex anunciava
28 funcoes onde havia 44, e a contagem estava no titulo.
"""

PROLOGO_TSX = [
    r'''{ code: `adopt Arcane.Time as Time

hoje := Time.today()
out Time.to_date_string(hoje)
out Time.weekday_name(hoje)
out Time.to_date_string(Time.add_days(hoje, 45))
out Time.age(Time.date(1995, 3, 10))
out Time.humanize(3725)`, title: `exemplo` }''',
    r'''{"callout": {"tipo": "nota", "texto": "`add_months` grampeia no último dia válido: 31/01 + 1 mês = 28/02. A operação não é reversível — veja [Datas e horas](/docs/tecnicas/datas)."}}''',
    r'''{"p": "Guia com contexto e boas práticas: [Time](/docs/tecnicas/datas)."}''',
]
