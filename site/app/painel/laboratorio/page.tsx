'use client';

import { useCallback, useEffect, useState } from 'react';
import { Cabecalho } from '@/components/painel/Casca';
import { Editor } from '@/components/painel/Editor';
import { prepararRuntime, rodar, versaoRuntime, type Resultado } from '@/lib/runtime';

/** Programas que mostram a linguagem sem precisar de explicação. */
const EXEMPLOS: { nome: string; codigo: string }[] = [
  {
    nome: 'Primeiros passos',
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
    nome: 'Pipelines',
    codigo: `nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

out nums
    >> sift n: n % 2 is 0
    >> morph n: n * n

out "soma dos pares ao quadrado:", nums
    >> sift n: n % 2 is 0
    >> morph n: n * n
    >> distill acumulado, v: acumulado + v 0`,
  },
  {
    nome: 'Records e pattern matching',
    codigo: `record Ponto:
    x: Integer
    y: Integer

    action norma():
        yield sqrt(self.x ** 2 + self.y ** 2)

p := Ponto(3, 4)
out p, "norma:", p.norma()

// records são imutáveis: 'with' devolve uma cópia
out p with {"y": 0}

action descrever(valor):
    match valor:
        point Integer as n when n bigger 100:
            yield "inteiro grande"
        point Ponto(x, y):
            yield $"ponto ({x}, {y})"
        point [a, b]:
            yield "par"
        default:
            yield "outra coisa"

out descrever(500)
out descrever(p)
out descrever([1, 2])`,
  },
  {
    nome: 'Blueprints e traits',
    codigo: `trait Forma:
    action area()

blueprint Retangulo(largura, altura) with Forma:
    action area():
        yield self.largura * self.altura

    get descricao():
        yield $"retângulo {self.largura}x{self.altura}"

blueprint Quadrado(lado) extends Retangulo:
    action setup(lado):
        self.largura := lado
        self.altura := lado

    operator +(outro):
        yield spawn Quadrado(self.largura + outro.largura)

r := spawn Retangulo(3, 4)
out r.descricao, "→", r.area()

q := spawn Quadrado(5)
out "quadrado:", q.area()
out "soma:", (q + q).area()`,
  },
  {
    nome: 'Generators preguiçosos',
    codigo: `stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

// infinito, mas só calcula o que você pedir
out fibonacci().take(12)

stream action primos():
    n := 2
    persist yes:
        ehPrimo := yes
        cycle d from 2 to int(sqrt(n)):
            given n % d is 0:
                ehPrimo := no
                halt
        given ehPrimo:
            emit n
        n += 1

out primos().take(10)`,
  },
  {
    nome: 'Kiln — um servidor web',
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
out "GET /          →", Kiln.test(loja, "GET", "/")["status"]
out "GET /produtos  →", Kiln.test(loja, "GET", "/produtos")["body"]["total"], "itens"
out "GET /produtos/2 →", Kiln.test(loja, "GET", "/produtos/2")["body"]["nome"]
out "GET /nada      →", Kiln.test(loja, "GET", "/nada")["status"]
out "POST /produtos →", Kiln.test(loja, "POST", "/produtos")["status"], "(verbo errado)"`,
  },
  {
    nome: 'Dados: banco e análise',
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
out "no banco:", len(registros), "vendas"

qtds := [r["qtd"] cycle r in registros]
precos := [r["preco"] cycle r in registros]

out "média de unidades:", An.mean(qtds)
out "correlação qtd × preço:", round(An.correlation(qtds, precos), 3)

tabela := An.from_records(registros)
out "colunas descritas:", An.describe(tabela)["qtd"]["mean"]

DB.close(banco)`,
  },
  {
    nome: 'Tratamento de erros',
    codigo: `action dividir(a, b):
    given b is 0:
        trigger "divisão por zero"
    yield a / b

monitor:
    out dividir(10, 2)
    out dividir(1, 0)
handle RuntimeError as e:
    out "peguei:", e.message
ensure:
    out "isso sempre roda"

// '??' cobre o valor ausente
config := {"porta": 8080}
out config["porta"] ?? 3000
out config["host"] ?? "127.0.0.1"`,
  },
];

const ARMAZEM = 'dataforge:laboratorio';

export default function Laboratorio() {
  const [codigo, setCodigo] = useState(EXEMPLOS[0].codigo);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [rodando, setRodando] = useState(false);
  const [estado, setEstado] = useState<'frio' | 'aquecendo' | 'pronto' | 'erro'>('frio');
  const [etapa, setEtapa] = useState('');
  const [versao, setVersao] = useState('');

  // O rascunho sobrevive ao recarregar. É a conveniência que faz alguém
  // usar o laboratório para valer, e não só espiar um exemplo.
  useEffect(() => {
    try {
      const guardado = localStorage.getItem(ARMAZEM);
      if (guardado) setCodigo(guardado);
    } catch {
      /* navegador com armazenamento bloqueado: segue com o exemplo */
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(ARMAZEM, codigo);
    } catch {
      /* idem */
    }
  }, [codigo]);

  const executar = useCallback(async () => {
    setRodando(true);
    try {
      if (estado !== 'pronto') {
        setEstado('aquecendo');
        await prepararRuntime(setEtapa);
        setEstado('pronto');
        setVersao(await versaoRuntime());
      }
      setResultado(await rodar(codigo));
    } catch (erro) {
      setEstado('erro');
      setEtapa(erro instanceof Error ? erro.message : 'falhou');
    } finally {
      setRodando(false);
    }
  }, [codigo, estado]);

  return (
    <>
      <Cabecalho
        titulo="Laboratório"
        descricao="Escreva DataForge e rode aqui mesmo. É o interpretador de verdade, compilado para o navegador — nada é enviado a servidor nenhum."
      />

      <div className="mb-4 flex flex-wrap gap-1.5">
        {EXEMPLOS.map((ex) => (
          <button
            key={ex.nome}
            onClick={() => {
              setCodigo(ex.codigo);
              setResultado(null);
            }}
            className="rounded-lg border border-line bg-raised/30 px-3 py-1.5 text-[12.5px] font-medium text-body transition-colors hover:border-accent/40 hover:text-strong"
          >
            {ex.nome}
          </button>
        ))}
      </div>

      <Editor valor={codigo} aoMudar={setCodigo} aoExecutar={executar} altura={420} />

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button
          onClick={executar}
          disabled={rodando}
          className="rounded-xl bg-accent px-5 py-2.5 text-[14px] font-bold text-white transition-all hover:bg-accent-soft disabled:opacity-50"
        >
          {rodando ? 'Rodando…' : 'Rodar'}
        </button>
        <span className="text-[12px] text-muted">⌘/Ctrl + Enter</span>
        {versao && (
          <span className="ml-auto font-mono text-[12px] text-muted">
            DataForge v{versao} no navegador
          </span>
        )}
      </div>

      {estado === 'aquecendo' && (
        <div className="mt-4 flex items-center gap-2.5 rounded-xl border border-line bg-raised/30 px-4 py-3 text-[13.5px] text-muted">
          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          {etapa}
          <span className="text-muted/70">— alguns segundos, só na primeira vez</span>
        </div>
      )}

      {estado === 'erro' && (
        <div className="mt-4 rounded-xl border border-accent/40 bg-accent/8 px-4 py-3 text-[13.5px]">
          <strong className="text-strong">Não consegui carregar o interpretador.</strong>{' '}
          <span className="text-muted">{etapa}</span>
        </div>
      )}

      {resultado && (
        <div
          className={`mt-4 rounded-xl border p-4 ${
            resultado.ok ? 'border-line bg-black/25' : 'border-accent/40 bg-accent/8'
          }`}
        >
          <div className="mb-2 flex items-center justify-between">
            <p className="text-[11px] font-bold uppercase tracking-wide text-muted">
              {resultado.ok ? 'Saída' : 'Erro'}
            </p>
            <p className="text-[12px] text-muted">{resultado.duracaoMs} ms</p>
          </div>
          <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-[12.5px] leading-[20px] text-body">
            {resultado.erro ?? resultado.saida ?? '(sem saída)'}
          </pre>
          {resultado.ok && resultado.saida === '' && (
            <p className="mt-1 text-[12.5px] text-muted">
              O programa rodou sem imprimir nada. Use `out` para ver um valor.
            </p>
          )}
        </div>
      )}
    </>
  );
}
