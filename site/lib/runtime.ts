/**
 * A linguagem rodando no navegador.
 *
 * O Pyodide é o CPython compilado para WebAssembly. Como o DataForge é
 * Python puro sem dependência de runtime, o interpretador **de verdade**
 * roda aqui — a mesma implementação do terminal, não uma reescrita em
 * JavaScript que divergiria na primeira correção de bug.
 *
 * Custo: ~4 s no primeiro carregamento, e nada depois. Por isso o
 * runtime é carregado sob demanda, só quando alguém abre a prática.
 */

const VERSAO_PYODIDE = 'v0.28.3';
const CDN = `https://cdn.jsdelivr.net/pyodide/${VERSAO_PYODIDE}/full/`;

/** Quanto tempo um programa pode rodar antes de ser considerado travado. */
const LIMITE_MS = 5000;

export type Resultado = {
  ok: boolean;
  valor?: unknown;
  saida: string;
  erro?: string;
  duracaoMs: number;
};

export type ResultadoCaso = {
  entrada: unknown[];
  esperado: unknown;
  obtido?: unknown;
  passou: boolean;
  erro?: string;
};

export type Correcao = {
  estado: 'aceito' | 'errado' | 'erro_execucao' | 'erro_sintaxe' | 'tempo_esgotado';
  casos: ResultadoCaso[];
  passaram: number;
  total: number;
  duracaoMs: number;
  detalhe?: string;
  saida: string;
};

type Pyodide = {
  runPython: (codigo: string) => unknown;
  loadPackage: (nome: string) => Promise<void>;
  unpackArchive: (dados: ArrayBuffer, formato: string) => void;
  globals: { set: (k: string, v: unknown) => void; get: (k: string) => unknown };
};

declare global {
  interface Window {
    loadPyodide?: (opcoes?: { indexURL?: string }) => Promise<Pyodide>;
  }
}

let carregando: Promise<Pyodide> | null = null;

function carregarScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve();
    const tag = document.createElement('script');
    tag.src = src;
    tag.onload = () => resolve();
    tag.onerror = () => reject(new Error(`não consegui carregar ${src}`));
    document.head.appendChild(tag);
  });
}

/**
 * Prepara o interpretador. Chamadas simultâneas compartilham a mesma
 * promessa: carregar o Pyodide duas vezes gastaria 8 MB à toa.
 */
export function prepararRuntime(
  aoProgredir?: (etapa: string) => void
): Promise<Pyodide> {
  if (carregando) return carregando;

  carregando = (async () => {
    aoProgredir?.('Baixando o interpretador…');
    await carregarScript(`${CDN}pyodide.js`);
    if (!window.loadPyodide) throw new Error('Pyodide não carregou');

    const py = await window.loadPyodide({ indexURL: CDN });

    // A biblioteca do DataForge importa sqlite3, que o Pyodide não traz
    // por padrão. Sem isto, qualquer 'adopt' falha.
    aoProgredir?.('Carregando o SQLite…');
    await py.loadPackage('sqlite3');

    aoProgredir?.('Instalando a linguagem…');
    const zip = await fetch('/dataforge-web.zip');
    if (!zip.ok) throw new Error('não achei o pacote da linguagem');
    py.unpackArchive(await zip.arrayBuffer(), 'zip');

    py.runPython(`
import sys, io, json, traceback
if '/home/pyodide' not in sys.path:
    sys.path.insert(0, '/home/pyodide')

from dataforge import __version__ as DF_VERSAO
from dataforge.interpreter import Interpreter
from dataforge.lexer import tokenize
from dataforge.parser import parse
from dataforge.errors import DataForgeError


def _df_json(valor):
    """Converte o valor do DataForge em algo que o JSON aceite."""
    if valor is None or isinstance(valor, (bool, int, float, str)):
        return valor
    if isinstance(valor, (list, tuple)):
        return [_df_json(v) for v in valor]
    if isinstance(valor, dict):
        return {str(k): _df_json(v) for k, v in valor.items()}
    if hasattr(valor, 'campos'):
        return {str(k): _df_json(v) for k, v in valor.campos.items()}
    return str(valor)


def df_rodar(fonte):
    """Executa um programa e devolve saída, valor e erro — nunca levanta."""
    saida = io.StringIO()
    antigo = sys.stdout
    sys.stdout = saida
    try:
        interpretador = Interpreter()
        interpretador.run(parse(tokenize(fonte)))
        valor = interpretador.global_env.variables.get('__saida__')
        return json.dumps({
            'ok': True,
            'valor': _df_json(valor),
            'saida': saida.getvalue(),
        })
    except DataForgeError as erro:
        # render() é a mensagem completa, com a linha e a seta — a mesma
        # que o terminal mostra.
        try:
            texto = erro.render(fonte, color=False)
        except Exception:
            texto = str(erro)
        return json.dumps({
            'ok': False,
            'saida': saida.getvalue(),
            'erro': texto,
            'codigo': getattr(erro, 'CODIGO', ''),
        })
    except RecursionError:
        return json.dumps({
            'ok': False, 'saida': saida.getvalue(),
            'erro': 'Recursão profunda demais: a ação chama a si mesma sem parar.',
        })
    except Exception as erro:
        return json.dumps({
            'ok': False, 'saida': saida.getvalue(),
            'erro': f'{type(erro).__name__}: {erro}',
        })
    finally:
        sys.stdout = antigo


def df_literal(valor):
    """Um valor JSON escrito como literal DataForge."""
    if valor is True:  return 'yes'
    if valor is False: return 'no'
    if valor is None:  return 'void'
    if isinstance(valor, str):
        return json.dumps(valor, ensure_ascii=False)
    if isinstance(valor, list):
        return '[' + ', '.join(df_literal(v) for v in valor) + ']'
    if isinstance(valor, dict):
        return '{' + ', '.join(
            json.dumps(str(k)) + ': ' + df_literal(v)
            for k, v in valor.items()) + '}'
    return repr(valor)


def df_igual(obtido, esperado):
    """Comparação tolerante ao que não muda a resposta.

    2 e 2.0 são a mesma resposta para quem resolveu o problema; recusar
    seria implicância com o tipo.
    """
    if isinstance(esperado, float) or isinstance(obtido, float):
        try:
            return abs(float(obtido) - float(esperado)) < 1e-9
        except (TypeError, ValueError):
            return False
    if isinstance(esperado, list) and isinstance(obtido, (list, tuple)):
        return (len(esperado) == len(obtido)
                and all(df_igual(o, e) for o, e in zip(obtido, esperado)))
    return obtido == esperado


def df_corrigir(codigo, casos_json):
    """Roda o código contra cada caso. É o mesmo corretor do repositório."""
    casos = json.loads(casos_json)
    resultados = []
    estado = 'aceito'
    detalhe = ''
    saida_total = ''

    for caso in casos:
        argumentos = ', '.join(df_literal(v) for v in caso['entrada'])
        fonte = codigo + '\\n\\n__saida__ := resolver(' + argumentos + ')\\n'
        bruto = json.loads(df_rodar(fonte))
        saida_total += bruto.get('saida', '')

        if not bruto['ok']:
            texto = bruto.get('erro', '')
            estado = ('erro_sintaxe'
                      if 'DF010' in bruto.get('codigo', '') else 'erro_execucao')
            detalhe = texto
            resultados.append({
                'entrada': caso['entrada'], 'esperado': caso['saida'],
                'passou': False, 'erro': texto,
            })
            break

        obtido = bruto.get('valor')
        passou = df_igual(obtido, caso['saida'])
        if not passou and estado == 'aceito':
            estado = 'errado'
        resultados.append({
            'entrada': caso['entrada'], 'esperado': caso['saida'],
            'obtido': obtido, 'passou': passou,
        })

    return json.dumps({
        'estado': estado,
        'casos': resultados,
        'passaram': sum(1 for r in resultados if r['passou']),
        'total': len(casos),
        'detalhe': detalhe,
        'saida': saida_total,
    })
`);

    aoProgredir?.('Pronto');
    return py;
  })();

  // Uma falha não pode deixar a promessa quebrada para sempre: sem isto,
  // um problema de rede tornaria a prática inutilizável até recarregar.
  carregando.catch(() => {
    carregando = null;
  });

  return carregando;
}

/** A versão da linguagem que está carregada no navegador. */
export async function versaoRuntime(): Promise<string> {
  const py = await prepararRuntime();
  return String(py.runPython('DF_VERSAO'));
}

/** Executa um programa e devolve saída e erro. */
export async function rodar(fonte: string): Promise<Resultado> {
  const py = await prepararRuntime();
  const inicio = performance.now();

  py.globals.set('__fonte__', fonte);
  const bruto = String(py.runPython('df_rodar(__fonte__)'));
  const dados = JSON.parse(bruto);

  return {
    ok: dados.ok,
    valor: dados.valor,
    saida: dados.saida ?? '',
    erro: dados.erro,
    duracaoMs: Math.round(performance.now() - inicio),
  };
}

/** Corrige uma solução contra os casos de teste do problema. */
export async function corrigir(
  codigo: string,
  casos: { entrada: unknown[]; saida: unknown }[]
): Promise<Correcao> {
  const py = await prepararRuntime();
  const inicio = performance.now();

  py.globals.set('__codigo__', codigo);
  py.globals.set('__casos__', JSON.stringify(casos));

  const bruto = String(py.runPython('df_corrigir(__codigo__, __casos__)'));
  const dados = JSON.parse(bruto);
  const duracaoMs = Math.round(performance.now() - inicio);

  return {
    estado: duracaoMs > LIMITE_MS && dados.estado !== 'aceito'
      ? 'tempo_esgotado'
      : dados.estado,
    casos: dados.casos,
    passaram: dados.passaram,
    total: dados.total,
    duracaoMs,
    detalhe: dados.detalhe || undefined,
    saida: dados.saida ?? '',
  };
}

/** O runtime já está na memória? Serve para decidir se vale avisar que vai demorar. */
export function runtimePronto(): boolean {
  return carregando !== null;
}
