// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um projeto completo",
  description: "Análise de vendas de ponta a ponta: banco SQLite, ETL, agregação, painel com filtros, exportação e testes.",
};

const blocos: Bloco[] = [
  {"p": "Um sistema de análise de vendas, do arquivo bruto ao painel no navegador. Nada de pseudocódigo: cada bloco desta página compila, e o projeto inteiro está em `projetos/painel-vendas/` — com testes que rodam em `dataforge test`."},
  { code: `painel-vendas/
├── forge.toml
├── dados/
│   └── vendas-2026.csv
├── src/
│   ├── esquema.df      as tabelas e as migrações
│   ├── etl.df          do CSV para o banco
│   ├── consultas.df    o SQL, num lugar só
│   └── painel.df       a página
├── main.df             sobe o servidor
└── tests/
    ├── etl_test.df
    ├── consultas_test.df
    └── painel_test.df`, lang: 'text' },
  {"h2": "1. O esquema"},
  {"p": "Migrações desde a primeira linha. Num sistema que vai receber dado todo dia, trocar o `create_table` no código não muda a tabela que já existe."},
  { code: `// src/esquema.df
adopt Arcane.Database as Banco

steady MIGRACOES := [
    {
        "version": 1,
        "description": "vendas",
        "up": """
            CREATE TABLE vendas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                data       TEXT    NOT NULL,
                mes        TEXT    NOT NULL,
                regiao     TEXT    NOT NULL,
                categoria  TEXT    NOT NULL,
                vendedor   TEXT    NOT NULL,
                produto    TEXT    NOT NULL,
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                valor      REAL    NOT NULL CHECK (valor >= 0),
                UNIQUE (data, vendedor, produto)
            );
            CREATE INDEX idx_vendas_mes    ON vendas(mes);
            CREATE INDEX idx_vendas_regiao ON vendas(regiao);
        """,
        "down": "DROP TABLE vendas;"
    },
    {
        "version": 2,
        "description": "metas por regiao e mes",
        "up": """
            CREATE TABLE metas (
                regiao TEXT NOT NULL,
                mes    TEXT NOT NULL,
                alvo   REAL NOT NULL,
                PRIMARY KEY (regiao, mes)
            );
        """,
        "down": "DROP TABLE metas;"
    }
]

action abrir(caminho):
    db := Banco.connect(caminho)
    Banco.migrate(db, MIGRACOES)
    yield db

relay abrir, MIGRACOES`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "O `UNIQUE` é o que torna o ETL repetível", "texto": "`(data, vendedor, produto)` é a identidade natural de uma linha de venda. Com ela declarada, importar o mesmo arquivo duas vezes **atualiza** em vez de duplicar — e reprocessar um dia inteiro deixa de ser um problema."}},
  {"h2": "2. ETL — do arquivo para o banco"},
  { code: `// src/etl.df
adopt Arcane.Database as Banco
adopt Arcane.IO as IO

//: Quantas linhas por transação. Uma transação por linha faz uma
//: sincronização de disco por linha; uma transação para tudo mantém a
//: escrita presa até o fim, e um erro na linha 90.000 desfaz as 89.999
//: que estavam certas.
steady LOTE := 500

action limpar(linha):
    yield {
        "data": linha["data"].trim(),
        "mes": linha["data"].trim()[0:7],
        "regiao": linha["regiao"].trim().title(),
        "categoria": linha["categoria"].trim().lower(),
        "vendedor": linha["vendedor"].trim().lower(),
        "produto": linha["produto"].trim(),
        "quantidade": int(linha["quantidade"]),
        "valor": round(float(linha["valor"].replace(",", ".")), 2)
    }

action importar(db, caminho):
    brutas := IO.read_csv(caminho)
    limpas := []
    recusadas := []

    cycle linha in brutas:
        monitor:
            limpas.append(limpar(linha))
        handle Error as e:
            // Uma linha ruim não derruba a importação, e não é perdida
            // em silêncio: ela sai no relatório, com o motivo.
            recusadas.append({"linha": linha, "motivo": e.message})

    gravadas := 0
    cycle inicio in range(0, len(limpas), LOTE):
        lote := limpas[inicio:inicio + LOTE]
        r := Banco.upsert_many(db, "vendas", lote,
                               ["data", "vendedor", "produto"])
        gravadas += r["inseridos"] + r["atualizados"]

    yield {"lidas": len(brutas), "gravadas": gravadas,
           "recusadas": recusadas}

relay importar, limpar`, lang: 'df' },
  {"p": "Três decisões que fazem a diferença num ETL que roda todo dia:"},
  {"table": {"head": ["Decisão", "Por quê"], "rows": [["`upsert_many` com a chave natural", "reprocessar o mesmo arquivo não duplica"], ["lote de 500, e não linha a linha", "uma transação por linha é uma sincronização de disco por linha; uma transação só prende a escrita até o fim"], ["linha ruim vai para `recusadas`", "não derruba a importação, e não desaparece"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Normalize na entrada, não na consulta", "texto": "`\"  SUL \"` e `\"Sul\"` são a mesma região, e descobrir isso no `GROUP BY` significa dois grupos no gráfico. O `limpar` acima resolve na fronteira, uma vez — e não em cada uma das trinta consultas."}},
  {"h2": "3. As consultas, num lugar só"},
  { code: `// src/consultas.df
adopt Arcane.Database as Banco
adopt Arcane.Vitrine as V

//: O cache é por argumento. O programa de um painel roda INTEIRO a
//: cada clique: sem ele, mover um deslizante refaz toda agregação.
mark @V.cache(validade := 120, teto := 64)
action receita_por_mes(db, regiao):
    onde := {} given regiao is "Todas" otherwise {"regiao": regiao}
    yield Banco.aggregate(db, "vendas",
                          {"receita": ["sum", "valor"],
                           "itens": ["sum", "quantidade"],
                           "vendas": ["count", "*"]},
                          group_by := "mes", where := onde,
                          order_by := "mes")

mark @V.cache(validade := 120)
action ranking_de_vendedores(db, regiao, quantos):
    onde := {} given regiao is "Todas" otherwise {"regiao": regiao}
    yield Banco.aggregate(db, "vendas",
                          {"receita": ["sum", "valor"],
                           "ticket": ["avg", "valor"]},
                          group_by := "vendedor", where := onde,
                          order_by := "receita DESC", limit := quantos)

mark @V.cache(validade := 120)
action mix_por_categoria(db, regiao):
    onde := {} given regiao is "Todas" otherwise {"regiao": regiao}
    yield Banco.aggregate(db, "vendas", {"receita": ["sum", "valor"]},
                          group_by := "categoria", where := onde,
                          order_by := "receita DESC")

mark @V.cache(validade := 120)
action contra_meta(db, regiao):
    yield Banco.query(db, """
        SELECT v.mes,
               SUM(v.valor)                      AS receita,
               COALESCE(MAX(m.alvo), 0)          AS meta
        FROM vendas v
        LEFT JOIN metas m ON m.regiao = v.regiao AND m.mes = v.mes
        WHERE (? = 'Todas' OR v.regiao = ?)
        GROUP BY v.mes
        ORDER BY v.mes
    """, [regiao, regiao])

action regioes(db):
    yield ["Todas"] + (Banco.group_count(db, "vendas", "regiao")
                       >> morph r: r["regiao"])

action resumo(db, regiao):
    linhas := receita_por_mes(db, regiao)
    receita := linhas >> morph l: l["receita"] >> distill a, v: a + v 0.0
    vendas := linhas >> morph l: l["vendas"] >> distill a, v: a + v 0
    yield {
        "receita": round(receita, 2),
        "vendas": vendas,
        "ticket": round(receita / vendas, 2) given vendas bigger 0 otherwise 0.0,
        "meses": len(linhas)
    }

relay receita_por_mes, ranking_de_vendedores, mix_por_categoria
relay contra_meta, regioes, resumo`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "O SQL num arquivo só", "texto": "Espalhar consulta pelo código da página é o que torna impossível responder \"quais consultas este painel faz?\" — e é essa pergunta que se faz quando ele fica lento. Com tudo aqui, `Banco.explain` sobre cada uma é uma tarde de trabalho, não uma arqueologia."}},
  {"h2": "4. O painel"},
  { code: `// src/painel.df
adopt Arcane.Vitrine as V
adopt ./consultas as Q

action painel(db):
    // ── Filtros, na barra lateral ──
    lado := V.lateral()
    lado.cabecalho("Filtros", 4)
    regiao := lado.escolha("Região", Q.regioes(db))
    quantos := lado.deslizante("Vendedores no ranking", 3, 15, valor := 8)
    lado.divisor()
    detalhar := lado.interruptor("Mostrar a tabela", yes)

    // ── Cabeçalho e métricas ──
    V.titulo("Análise de Vendas", icone := "📊")
    V.texto($"Região: {regiao}")

    r := Q.resumo(db, regiao)
    colunas := V.colunas(4)
    colunas[0].metrica("Receita", $"R$ {r["receita"]}")
    colunas[1].metrica("Vendas", r["vendas"])
    colunas[2].metrica("Ticket médio", $"R$ {r["ticket"]}")
    colunas[3].metrica("Meses", r["meses"])

    // ── Abas ──
    abas := V.abas(["Evolução", "Ranking", "Mix", "Dados"])

    evolucao := abas[0]
    evolucao.cabecalho("Receita contra meta")
    g := evolucao.grafico("barras", Q.contra_meta(db, regiao))
    g.eixo_x("mes")
    g.eixo_y(["receita", "meta"])
    g.titulo($"Mensal — {regiao}")
    evolucao.desenhar(g)

    linha := evolucao.grafico("linha", Q.receita_por_mes(db, regiao))
    linha.eixo_x("mes")
    linha.eixo_y("itens")
    linha.suavizar(yes)
    linha.titulo("Itens vendidos")
    evolucao.desenhar(linha)

    ranking := abas[1]
    top := Q.ranking_de_vendedores(db, regiao, quantos)
    ranking.grafico_barras_h(top, x := "vendedor", y := "receita",
                             titulo := $"Top {quantos}")
    ranking.frame(top)

    mix := abas[2]
    mix.grafico_rosca(Q.mix_por_categoria(db, regiao),
                      x := "categoria", y := "receita",
                      titulo := "Participação por categoria")

    dados := abas[3]
    given detalhar:
        linhas := Q.receita_por_mes(db, regiao)
        dados.frame(linhas)
        dados.exportar_csv(linhas, nome := $"receita-{regiao}.csv")
        dados.exportar_json(linhas, nome := $"receita-{regiao}.json")
    otherwise:
        dados.informacao("Ligue "Mostrar a tabela" na barra lateral.")

    // ── Rodapé ──
    V.divisor()
    given V.botao("Recarregar dados", tipo := "secundario"):
        V.cache.invalidar()
        V.sucesso("Cache esvaziado — as consultas serão refeitas.")

relay painel`, lang: 'df' },
  {"h2": "5. Subir"},
  { code: `// main.df
adopt Arcane.Vitrine as V
adopt Kiln
adopt ./src/esquema as E
adopt ./src/painel as P
adopt ./src/consultas as Q

db := E.abrir("vendas.db")

V.app("Análise de Vendas", icone := "📊", modo_tema := "automatico")
V.pagina("/", lambda: P.painel(db), titulo := "Painel")

// A MESMA aplicação serve uma API para quem quer o dado cru
kiln := V.montar()
Kiln.get(kiln, "/api/receita", lambda req: {
    "itens": Q.receita_por_mes(db, req["query"]["regiao"] ?? "Todas")
})
Kiln.use(kiln, Kiln.cors())
Kiln.use(kiln, Kiln.rate_limit(120))

V.subir(porta := 8501)`, lang: 'df' },
  { code: `dataforge vitrine dev            # http://127.0.0.1:8501
dataforge test --cobertura       # os testes, com o que falta cobrir
curl 'localhost:8501/api/receita?regiao=Sul'`, lang: 'bash' },
  {"h2": "6. Os testes"},
  {"p": "Três níveis, e cada um pega um tipo de erro diferente."},
  { code: `// tests/etl_test.df — a normalização
adopt Arcane.Test as T
adopt ../src/etl as ETL

action test_normaliza_regiao():
    limpa := ETL.limpar({"data": "2026-03-14", "regiao": "  SUL ",
                         "categoria": " Bebida", "vendedor": " ANA ",
                         "produto": "Café", "quantidade": "2",
                         "valor": "32,90"})
    T.assert_eq(limpa["regiao"], "Sul")
    T.assert_eq(limpa["categoria"], "bebida")
    T.assert_eq(limpa["vendedor"], "ana")
    T.assert_eq(limpa["valor"], 32.9)
    T.assert_eq(limpa["mes"], "2026-03")

action test_virgula_decimal():
    T.assert_eq(ETL.limpar({"data": "2026-01-01", "regiao": "Sul",
                            "categoria": "x", "vendedor": "y",
                            "produto": "z", "quantidade": "1",
                            "valor": "1.234,50"})["valor"], 1.2345)`, lang: 'df' },
  { code: `// tests/consultas_test.df — a agregação, com banco em memória
adopt Arcane.Test as T
adopt Arcane.Database as Banco
adopt ../src/esquema as E
adopt ../src/consultas as Q

db := Banco.memory()
Banco.migrate(db, E.MIGRACOES)
Banco.insert_many(db, "vendas", [
    {"data": "2026-01-05", "mes": "2026-01", "regiao": "Sul",
     "categoria": "bebida", "vendedor": "ana", "produto": "Café",
     "quantidade": 2, "valor": 100.0},
    {"data": "2026-01-06", "mes": "2026-01", "regiao": "Sul",
     "categoria": "bebida", "vendedor": "bruno", "produto": "Chá",
     "quantidade": 1, "valor": 50.0},
    {"data": "2026-02-01", "mes": "2026-02", "regiao": "Norte",
     "categoria": "mercearia", "vendedor": "ana", "produto": "Arroz",
     "quantidade": 3, "valor": 75.0}
])

action test_receita_por_mes():
    linhas := Q.receita_por_mes(db, "Todas")
    T.assert_eq(len(linhas), 2)
    T.assert_eq(linhas[0]["mes"], "2026-01")
    T.assert_eq(linhas[0]["receita"], 150.0)

action test_filtro_de_regiao():
    T.assert_eq(len(Q.receita_por_mes(db, "Norte")), 1)

action test_ranking_ordena_por_receita():
    top := Q.ranking_de_vendedores(db, "Todas", 5)
    T.assert_eq(top[0]["vendedor"], "ana")
    T.assert_eq(top[0]["receita"], 175.0)

action test_resumo():
    r := Q.resumo(db, "Todas")
    T.assert_eq(r["receita"], 225.0)
    T.assert_eq(r["vendas"], 3)
    T.assert_eq(r["ticket"], 75.0)`, lang: 'df' },
  { code: `// tests/painel_test.df — a tela, sem navegador
adopt Arcane.Test as T
adopt Arcane.Database as Banco
adopt Arcane.Vitrine as V
adopt ../src/esquema as E
adopt ../src/painel as P

db := Banco.memory()
Banco.migrate(db, E.MIGRACOES)
Banco.insert_many(db, "vendas", [
    {"data": "2026-01-05", "mes": "2026-01", "regiao": "Sul",
     "categoria": "bebida", "vendedor": "ana", "produto": "Café",
     "quantidade": 2, "valor": 100.0}
])

action pagina():
    P.painel(db)

action test_o_painel_monta():
    t := V.testar(pagina)
    T.assert_false(t.falhou())
    T.assert_eq(t.quantos("metrica"), 4)

action test_os_graficos_desenham():
    T.assert_contains(V.testar(pagina).html(), "<svg")

action test_o_filtro_de_regiao_funciona():
    t := V.testar(pagina)
    T.assert_contains(t.texto(), "Todas")
    t.selecionar("Região", "Sul")
    T.assert_contains(t.texto(), "Sul")

action test_o_interruptor_esconde_a_tabela():
    t := V.testar(pagina)
    antes := t.quantos("frame")
    t.marcar("Mostrar a tabela", no)
    T.assert_true(t.quantos("frame") smaller antes)

action test_a_api_responde():
    app := V.app("teste")
    V.pagina("/", pagina)
    r := V.pedir(app, "GET", "/")
    T.assert_eq(r["status"], 200)`, lang: 'df' },
  {"table": {"head": ["Nível", "Pega"], "rows": [["ETL", "a vírgula decimal, o espaço em branco, a região com caixa diferente"], ["consultas", "o `GROUP BY` errado, o filtro que não filtra, o `JOIN` que perde linha"], ["painel", "o componente que sumiu, o filtro que não chega à consulta, o erro que a página engoliu"]]}},
  {"callout": {"tipo": "dica", "titulo": "`Banco.memory()` nos testes", "texto": "O banco em memória some ao terminar, e `Banco.migrate` o monta em milissegundos. Para uma suíte que escreve muito, `Crucible.banco(db)` desfaz cada trial — ver [Instantâneos e isolamento](/docs/tecnicas/instantaneos)."}},
  {"h2": "7. O que fazer quando fica lento"},
  {"p": "Na ordem, e cada passo custa menos que o seguinte:"},
  { code: `// 1. o cache está pegando?
out V.cache.estatisticas()
// {"receita_por_mes": {"acertos": 47, "erros": 3, "taxa": 0.94}, …}

// 2. qual consulta varre a tabela?
out Banco.explain(db, "SELECT … FROM vendas WHERE regiao = ?", ["Sul"])

// 3. onde está o tempo?
out V.metricas()["media_ms"]`, lang: 'df' },
  {"table": {"head": ["Sintoma", "Causa provável"], "rows": [["a taxa de acerto do cache é baixa", "a chave muda a cada execução — um argumento que é um vault novo, ou o relógio"], ["uma consulta aparece com `SCAN`", "falta índice na coluna do `WHERE`"], ["a média em ms sobe com o número de sessões", "cada sessão refaz a agregação; suba a `validade` do cache"], ["o primeiro clique é lento e os outros não", "é o cache frio, e está funcionando"]]}},
  {"h2": "8. Em produção"},
  { code: `V.configurar("producao", yes)        // esconde o stack trace na página
V.configurar("validade_sessao", 1800)
V.subir(porta := 8501, host := "127.0.0.1")`, lang: 'df' },
  {"p": "Com nginx ou Caddy na frente, para TLS e compressão — a Vitrine roda sobre o `http.server`, que não tem nenhum dos dois. `GET /__vitrine__/saude` e `/__vitrine__/metricas` vêm prontas para o balanceador e o monitoramento."},
  {"p": "E a sessão vive na memória do processo: **um** processo por aplicação. Dois processos fazem dois pedidos da mesma pessoa caírem em memórias diferentes."},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/tecnicas/banco-de-dados/crud", "title": "O CRUD completo", "desc": "Cinco sistemas com o mesmo esqueleto."}, {"href": "/docs/tecnicas/banco-de-dados/relatorios", "title": "Relatórios e busca", "desc": "Agregação, FTS5 e o plano de consulta."}, {"href": "/docs/vitrine/graficos", "title": "Gráficos", "desc": "Sete tipos, em SVG escrito no servidor."}, {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "O que os testes deste projeto não exercitam."}]},
];

const headings = [{ id: '1-o-esquema', text: "1. O esquema", level: 2 as const }, { id: '2-etl-do-arquivo-para-o-banco', text: "2. ETL — do arquivo para o banco", level: 2 as const }, { id: '3-as-consultas-num-lugar-so', text: "3. As consultas, num lugar só", level: 2 as const }, { id: '4-o-painel', text: "4. O painel", level: 2 as const }, { id: '5-subir', text: "5. Subir", level: 2 as const }, { id: '6-os-testes', text: "6. Os testes", level: 2 as const }, { id: '7-o-que-fazer-quando-fica-lento', text: "7. O que fazer quando fica lento", level: 2 as const }, { id: '8-em-producao', text: "8. Em produção", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um projeto completo"}
      description={"Análise de vendas de ponta a ponta: banco SQLite, ETL, agregação, painel com filtros, exportação e testes."}
      href={"/docs/vitrine/projeto"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
