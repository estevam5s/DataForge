'use client';

import { useCallback, useEffect, useState } from 'react';
import { Cabecalho, Icone } from '@/components/painel/Casca';
import { Editor } from '@/components/painel/Editor';
import { prepararRuntime, rodar, versaoRuntime, type Resultado } from '@/lib/runtime';

/**
 * Playground: escreve, roda e inspeciona.
 *
 * A diferença para o Laboratório é a coluna da direita: além da saída,
 * ela mostra o que o programa **declarou** — ações, blueprints, records,
 * variáveis — e os decoradores de cada um. É a mesma ideia do painel de
 * inspeção do NestJS Devtools: ver a forma do programa, não só o que
 * ele imprimiu.
 *
 * Tudo roda no navegador, com o interpretador de verdade. Nada é
 * enviado a servidor nenhum.
 */

type Simbolo = {
  nome: string;
  tipo: string;
  detalhe: string;
  decoradores: string[];
  membros?: string[];
};

const ARMAZEM = 'dataforge:playground';

const EXEMPLOS: { nome: string; icone: string; codigo: string }[] = [
  {
    nome: 'Decoradores',
    icone: 'alvo',
    codigo: `// Um mini-framework com decoradores, na própria linguagem.
adopt Arcane.Meta as Meta

action Injetavel(alvo):
    yield void

action Controlador(prefixo):
    action aplicar(alvo):
        yield void
    yield aplicar

action Rota(metodo, caminho):
    action aplicar(alvo):
        yield void
    yield aplicar

@Injetavel
blueprint RepositorioUsuarios:
    action todos():
        yield [{"id": 1, "nome": "Ana"}, {"id": 2, "nome": "Bia"}]

@Controlador("/usuarios")
blueprint UsuariosController:
    @Rota("GET", "/")
    action listar():
        yield "todos"

    @Rota("GET", "/:id")
    action mostrar():
        yield "um"

    @Rota("POST", "/")
    action criar():
        yield "criado"

// O roteador descobre as rotas sozinho, lendo os metadados.
prefixo := Meta.arg(UsuariosController, "Controlador", 0)
cycle r in Meta.metodos_com(UsuariosController, "Rota"):
    verbo := r["meta"]["args"][0]
    caminho := r["meta"]["args"][1]
    metodo := r["nome"]
    out $"{verbo} {prefixo}{caminho}  ->  {metodo}()"`,
  },
  {
    nome: 'Primeiros passos',
    icone: 'livro',
    codigo: `x := 10
steady PI := 3.14159
out $"x vale {x}, o dobro é {x * 2}"

given x bigger 5:
    out "grande"
otherwise:
    out "pequeno"

cycle i from 1 to 5:
    out i, "ao quadrado é", i ** 2`,
  },
  {
    nome: 'OOP completa',
    icone: 'pasta',
    codigo: `trait Forma:
    action area()

blueprint Retangulo(largura, altura) with Forma:
    private escala: Float := 1.0

    action area():
        yield self.largura * self.altura * self.escala

    get descricao():
        yield $"retângulo {self.largura}×{self.altura}"

    operator +(outro):
        yield spawn Retangulo(self.largura + outro.largura,
                              self.altura + outro.altura)

blueprint Quadrado(lado) extends Retangulo:
    action setup(lado):
        self.largura := lado
        self.altura := lado

record Ponto:
    x: Integer
    y: Integer

    action distancia_ate(outro):
        yield sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)

cycle f in [spawn Retangulo(3, 4), spawn Quadrado(5)]:
    out f.descricao, "→", f.area()

out "soma:", (spawn Retangulo(2, 3) + spawn Retangulo(4, 1)).area()
out "distância:", Ponto(0, 0).distancia_ate(Ponto(3, 4))
out "igualdade estrutural:", Ponto(1, 2) is Ponto(1, 2)`,
  },
  {
    nome: 'Pipelines',
    icone: 'codigo',
    codigo: `nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

out nums
    >> sift n: n % 2 is 0
    >> morph n: n * n

soma := nums
    >> sift n: n % 2 is 0
    >> morph n: n * n
    >> distill acumulado, v: acumulado + v 0

out "soma dos pares ao quadrado:", soma

// generator preguiçoso: infinito, calcula só o que você pedir
stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

out fibonacci().take(12)`,
  },
  {
    nome: 'Kiln — servidor',
    icone: 'raio',
    codigo: `adopt Kiln

produtos := [
    {"id": 1, "nome": "Martelo", "preco": 89.9},
    {"id": 2, "nome": "Bigorna", "preco": 450.0}
]

server loja on 8080:
    route GET "/":
        respond html "<h1>Forja</h1>"

    route GET "/produtos":
        respond json {"itens": produtos, "total": len(produtos)}

    route GET "/produtos/:id":
        alvo := int(params["id"])
        cycle p in produtos:
            given p["id"] is alvo:
                respond json p
        respond 404 json {"erro": "não achei"}

// Kiln.test executa a rota sem abrir socket
out "GET /            ->", Kiln.test(loja, "GET", "/")["status"]
out "GET /produtos    ->", Kiln.test(loja, "GET", "/produtos")["body"]["total"], "itens"
out "GET /produtos/2  ->", Kiln.test(loja, "GET", "/produtos/2")["body"]["nome"]
out "GET /nada        ->", Kiln.test(loja, "GET", "/nada")["status"]
out "POST /produtos   ->", Kiln.test(loja, "POST", "/produtos")["status"], "(verbo errado)"`,
  },
  {
    nome: 'Dados',
    icone: 'grafico',
    codigo: `adopt Arcane.Database as DB
adopt Arcane.Analytics as An

banco := DB.connect(":memory:")
DB.execute(banco, """CREATE TABLE vendas (
    produto TEXT, regiao TEXT, qtd INTEGER, preco REAL)""")

cycle linha in [
    ["Martelo", "Sul", 12, 89.9],
    ["Bigorna", "Sul", 3, 450.0],
    ["Tenaz", "Norte", 27, 65.5],
    ["Fole", "Norte", 8, 320.0]
]:
    DB.execute(banco, "INSERT INTO vendas VALUES (?, ?, ?, ?)", linha)

registros := DB.query(banco, "SELECT * FROM vendas ORDER BY qtd DESC")
qtds := [r["qtd"] cycle r in registros]
precos := [r["preco"] cycle r in registros]

out "vendas:", len(registros)
out "média de unidades:", An.mean(qtds)
out "correlação qtd × preço:", round(An.correlation(qtds, precos), 3)
out "  (negativa: o caro vende pouco)"

DB.close(banco)`,
  },
  {
    nome: 'Erros',
    icone: 'nota',
    codigo: `action dividir(a, b):
    given b is 0:
        trigger "divisão por zero: confira o divisor antes de chamar"
    yield a / b

monitor:
    out dividir(10, 2)
    out dividir(1, 0)
handle TriggerError as e:
    out "peguei:", e.message
ensure:
    out "isso sempre roda"

// '??' cobre o valor ausente
config := {"porta": 8080}
out config["porta"] ?? 3000
out config["host"] ?? "127.0.0.1"`,
  },
];

export default function Playground() {
  const [codigo, setCodigo] = useState(EXEMPLOS[0].codigo);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [simbolos, setSimbolos] = useState<Simbolo[]>([]);
  const [selecionado, setSelecionado] = useState<Simbolo | null>(null);
  const [rodando, setRodando] = useState(false);
  const [estado, setEstado] = useState<'frio' | 'aquecendo' | 'pronto' | 'erro'>('frio');
  const [etapa, setEtapa] = useState('');
  const [versao, setVersao] = useState('');
  const [aba, setAba] = useState<'saida' | 'simbolos'>('saida');
  const [historico, setHistorico] = useState<
    { hora: string; ok: boolean; ms: number }[]
  >([]);

  useEffect(() => {
    try {
      const guardado = localStorage.getItem(ARMAZEM);
      if (guardado) setCodigo(guardado);
    } catch {
      /* armazenamento bloqueado: segue com o exemplo */
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(ARMAZEM, codigo);
    } catch {
      /* idem */
    }
  }, [codigo]);

  /**
   * Lê o que o programa declarou, depois de executá-lo.
   *
   * Percorre o escopo global do interpretador, que é onde ficam as
   * ações, blueprints e records — junto com os metadados que os
   * decoradores deixaram.
   */
  const inspecionar = useCallback(async () => {
    const py = await prepararRuntime();
    const bruto = String(
      py.runPython(`
import json

def _df_inspecionar(fonte):
    import io, sys
    interpretador = Interpreter()
    antigo = sys.stdout
    sys.stdout = io.StringIO()
    try:
        interpretador.run(parse(tokenize(fonte)))
    except Exception:
        pass
    finally:
        sys.stdout = antigo

    # As 225 embutidas e as constantes vivem no mesmo escopo global.
    # Sem filtrá-las, o que o usuário declarou fica afogado no meio de
    # 'abs', 'acos', 'append'… e o painel deixa de servir para nada.
    from dataforge.builtins import get_builtins
    embutidas = set(get_builtins())

    achados = []
    for nome, valor in interpretador.global_env.variables.items():
        if nome.startswith('__') or nome in embutidas:
            continue

        decoradores = [m['nome'] for m in
                       (getattr(valor, '__metadados__', None) or [])]
        tipo = type(valor).__name__
        membros = None
        detalhe = ''

        if tipo == 'DFAction':
            tipo = 'ação'
            detalhe = '(' + ', '.join(getattr(valor, 'params', []) or []) + ')'
        elif tipo == 'DFBlueprint':
            tipo = 'blueprint'
            metodos = getattr(valor, 'methods', {}) or {}
            membros = sorted(metodos)
            campos = getattr(valor, 'fields_decl', []) or []
            detalhe = f"{len(metodos)} método(s), {len(campos)} campo(s)"
        elif tipo == 'DFRecord':
            tipo = 'record'
            campos = getattr(valor, 'fields', []) or []
            membros = [c[0] if isinstance(c, (list, tuple)) else str(c)
                       for c in campos]
            detalhe = f"{len(campos)} campo(s)"
        elif tipo == 'DFEnum':
            tipo = 'enum'
            membros = sorted(getattr(valor, 'values', {}) or {})
        elif isinstance(valor, dict) and '__name__' in valor:
            tipo = 'módulo'
            detalhe = f"{len(valor) - 1} símbolos"
            membros = sorted(k for k in valor if k != '__name__')[:40]
        elif callable(valor):
            tipo = 'função'
        else:
            tipo = {'int': 'Integer', 'float': 'Float', 'str': 'String',
                    'bool': 'Boolean', 'list': 'Cluster',
                    'dict': 'Vault'}.get(tipo, tipo)
            texto = repr(valor)
            detalhe = texto if len(texto) <= 60 else texto[:57] + '…'

        achados.append({'nome': nome, 'tipo': tipo, 'detalhe': detalhe,
                        'decoradores': decoradores, 'membros': membros})

    ordem = {'blueprint': 0, 'record': 1, 'enum': 2, 'ação': 3,
             'módulo': 4}
    achados.sort(key=lambda s: (ordem.get(s['tipo'], 9), s['nome']))
    return json.dumps(achados)

_df_inspecionar(__fonte__)
`)
    );
    return JSON.parse(bruto) as Simbolo[];
  }, []);

  const executar = useCallback(async () => {
    setRodando(true);
    try {
      if (estado !== 'pronto') {
        setEstado('aquecendo');
        await prepararRuntime(setEtapa);
        setEstado('pronto');
        setVersao(await versaoRuntime());
      }

      const r = await rodar(codigo);
      setResultado(r);
      setAba('saida');

      const agora = new Date();
      setHistorico((anterior) =>
        [
          {
            hora: agora.toLocaleTimeString('pt-BR'),
            ok: r.ok,
            ms: r.duracaoMs,
          },
          ...anterior,
        ].slice(0, 8)
      );

      // A inspeção reexecuta o programa num interpretador limpo. Um
      // programa com efeito colateral (escrever arquivo, subir servidor)
      // o faria duas vezes — no navegador, nenhum dos dois sai da aba.
      const py = await prepararRuntime();
      py.globals.set('__fonte__', codigo);
      const achados = await inspecionar();
      setSimbolos(achados);
      setSelecionado(null);
    } catch (erro) {
      setEstado('erro');
      setEtapa(erro instanceof Error ? erro.message : 'falhou');
    } finally {
      setRodando(false);
    }
  }, [codigo, estado, inspecionar]);

  const declarados = simbolos.filter((s) => s.tipo !== 'módulo');

  return (
    <>
      <Cabecalho
        titulo="Playground"
        descricao="Escreva, rode e veja a forma do programa. O interpretador roda no seu navegador — nada é enviado a servidor nenhum."
      />

      <div className="mb-4 flex flex-wrap gap-1.5">
        {EXEMPLOS.map((ex) => (
          <button
            key={ex.nome}
            onClick={() => {
              setCodigo(ex.codigo);
              setResultado(null);
              setSimbolos([]);
            }}
            className="flex items-center gap-1.5 rounded-lg border border-line bg-raised/30 px-3 py-1.5 text-[12.5px] font-medium text-body transition-colors hover:border-accent/40 hover:text-strong"
          >
            <Icone nome={ex.icone} className="h-3.5 w-3.5" />
            {ex.nome}
          </button>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_400px]">
        {/* ── Editor ── */}
        <div className="min-w-0">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
              Editor
            </p>
            <div className="flex items-center gap-3">
              <span className="text-[11.5px] text-muted">⌘/Ctrl + Enter</span>
              <button
                onClick={executar}
                disabled={rodando}
                className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-1.5 text-[13px] font-bold text-white transition-all hover:bg-accent-soft disabled:opacity-50"
              >
                {rodando ? (
                  <>
                    <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                    Rodando
                  </>
                ) : (
                  <>
                    Rodar
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor" aria-hidden>
                      <path d="M2 1l6 4-6 4z" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>

          <Editor valor={codigo} aoMudar={setCodigo} aoExecutar={executar} altura={520} />

          {estado === 'aquecendo' && (
            <div className="mt-3 flex items-center gap-2.5 rounded-xl border border-line bg-raised/30 px-4 py-3 text-[13.5px] text-muted">
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-accent border-t-transparent" />
              {etapa}
              <span className="text-muted/70">— alguns segundos, só na primeira vez</span>
            </div>
          )}

          {estado === 'erro' && (
            <div className="mt-3 rounded-xl border border-accent/40 bg-accent/8 px-4 py-3 text-[13.5px]">
              <strong className="text-strong">Não consegui carregar o interpretador.</strong>{' '}
              <span className="text-muted">{etapa}</span>
            </div>
          )}
        </div>

        {/* ── Resultado e inspeção ── */}
        <aside className="min-w-0">
          <div className="mb-2 flex items-center gap-1">
            {(['saida', 'simbolos'] as const).map((a) => (
              <button
                key={a}
                onClick={() => setAba(a)}
                className={`rounded-lg px-3 py-1.5 text-[12px] font-bold uppercase tracking-wide transition-colors ${
                  aba === a ? 'bg-raised text-strong' : 'text-muted hover:text-strong'
                }`}
              >
                {a === 'saida' ? 'Resultado' : `Declarado${declarados.length ? ` · ${declarados.length}` : ''}`}
              </button>
            ))}
            {versao && (
              <span className="ml-auto font-mono text-[11px] text-muted">
                v{versao}
              </span>
            )}
          </div>

          {aba === 'saida' && (
            <div className="rounded-xl border border-line bg-[#0d0d10]">
              {resultado ? (
                <>
                  <div
                    className={`flex items-center justify-between border-b border-line/60 px-4 py-2.5 text-[12px] ${
                      resultado.ok ? 'text-emerald-400' : 'text-accent'
                    }`}
                  >
                    <span className="font-bold uppercase tracking-wide">
                      {resultado.ok ? 'ok' : 'erro'}
                    </span>
                    <span className="text-muted">{resultado.duracaoMs} ms</span>
                  </div>
                  <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap p-4 font-mono text-[12.5px] leading-[20px] text-body">
                    {resultado.erro ?? resultado.saida ?? '(sem saída)'}
                  </pre>
                  {resultado.ok && !resultado.saida && (
                    <p className="border-t border-line/60 px-4 py-2.5 text-[12.5px] text-muted">
                      O programa rodou sem imprimir nada. Use <code>out</code> para
                      ver um valor.
                    </p>
                  )}
                </>
              ) : (
                <p className="px-4 py-12 text-center text-[13.5px] text-muted">
                  Rode o programa para ver a saída.
                </p>
              )}

              {historico.length > 0 && (
                <div className="border-t border-line/60 px-4 py-2.5">
                  <p className="mb-1.5 text-[10.5px] font-bold uppercase tracking-wide text-muted">
                    Execuções
                  </p>
                  <ul className="space-y-0.5">
                    {historico.map((h, i) => (
                      <li
                        key={i}
                        className="flex items-center gap-2 font-mono text-[11.5px] text-muted"
                      >
                        <span className={h.ok ? 'text-emerald-400' : 'text-accent'}>
                          {h.ok ? '✓' : '✗'}
                        </span>
                        {h.hora}
                        <span className="ml-auto">{h.ms} ms</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {aba === 'simbolos' && (
            <div className="rounded-xl border border-line bg-raised/20">
              {declarados.length === 0 ? (
                <p className="px-4 py-12 text-center text-[13.5px] text-muted">
                  Rode o programa para ver o que ele declarou — ações,
                  blueprints, records e os decoradores de cada um.
                </p>
              ) : (
                <ul className="max-h-[560px] divide-y divide-line/50 overflow-y-auto">
                  {declarados.map((s) => (
                    <li key={s.nome}>
                      <button
                        onClick={() =>
                          setSelecionado(selecionado?.nome === s.nome ? null : s)
                        }
                        className="w-full px-4 py-2.5 text-left transition-colors hover:bg-raised/50"
                      >
                        <div className="flex items-baseline gap-2">
                          <span className="font-mono text-[13px] font-semibold text-strong">
                            {s.nome}
                          </span>
                          <span className="rounded bg-accent/12 px-1.5 py-px text-[10px] font-bold uppercase text-accent">
                            {s.tipo}
                          </span>
                          {s.membros && s.membros.length > 0 && (
                            <span className="ml-auto text-[11px] text-muted">
                              {selecionado?.nome === s.nome ? '−' : '+'}
                            </span>
                          )}
                        </div>

                        {s.detalhe && (
                          <p className="mt-0.5 font-mono text-[11.5px] text-muted">
                            {s.detalhe}
                          </p>
                        )}

                        {s.decoradores.length > 0 && (
                          <div className="mt-1.5 flex flex-wrap gap-1">
                            {s.decoradores.map((d) => (
                              <span
                                key={d}
                                className="rounded bg-amber-400/12 px-1.5 py-px font-mono text-[10.5px] text-amber-400"
                              >
                                @{d}
                              </span>
                            ))}
                          </div>
                        )}

                        {selecionado?.nome === s.nome && s.membros && (
                          <ul className="mt-2 space-y-0.5 border-l border-line pl-3">
                            {s.membros.map((m) => (
                              <li key={m} className="font-mono text-[11.5px] text-muted">
                                {m}
                              </li>
                            ))}
                          </ul>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </aside>
      </div>
    </>
  );
}
