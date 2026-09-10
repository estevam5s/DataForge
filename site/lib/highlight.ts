/**
 * Realçador de sintaxe para DataForge.
 *
 * Nenhuma biblioteca conhece a linguagem, então este módulo reimplementa o
 * essencial do lexer real (dataforge/lexer.py) para classificar tokens. As
 * regras que importam e que um realçador genérico erraria:
 *
 *   · `//` é COMENTÁRIO por padrão; só é divisão inteira quando seguido de
 *     dígito, `(`, ou identificador que abre chamada/índice/membro.
 *   · `~/` é sempre divisão inteira.
 *   · `$"..."` interpola: o miolo de `{...}` é código, não texto.
 *   · `yes`/`no`/`void` são literais, não identificadores.
 */

export type TokenKind =
  | 'keyword'
  | 'declaration'
  | 'type'
  | 'string'
  | 'interp'
  | 'number'
  | 'comment'
  | 'operator'
  | 'punct'
  | 'function'
  | 'literal'
  | 'property'
  | 'plain';

export type Token = { kind: TokenKind; text: string };

/** As 81 palavras reservadas de dataforge/tokens.py. */
const KEYWORDS = new Set([
  'and', 'as', 'assert', 'async', 'await', 'bigger', 'bigger_eq', 'cast',
  'channel', 'cycle', 'default', 'defer', 'delete', 'distill', 'emit',
  'ensure', 'extends', 'forge', 'frame', 'from', 'given', 'guard', 'halt',
  'handle', 'in', 'inspect', 'is', 'isnt', 'lambda', 'mark', 'match',
  'monitor', 'morph', 'not', 'observe', 'or', 'orif', 'otherwise', 'out',
  'parallel', 'perform', 'persist', 'point', 'predict', 'propagate', 'pulse',
  'recover', 'relay', 'retry', 'root', 'self', 'shadow', 'sift', 'skip',
  'smaller', 'smaller_eq', 'spawn', 'static', 'step', 'stream', 'thread',
  'to', 'train', 'trait', 'trigger', 'typeof', 'using', 'validate', 'wait',
  'when', 'with', 'yield', 'adopt', 'action', 'blueprint', 'record', 'enum',
  'steady',

  // As dez do Kiln. Na linguagem elas são contextuais — só valem dentro
  // de um bloco 'server' — mas aqui colorimos sempre: num trecho de
  // documentação, 'route' é praticamente sempre a palavra do framework,
  // e deixá-la cinza esconde justamente o que o exemplo está ensinando.
  'server', 'route', 'respond', 'render', 'redirect', 'middleware', 'after',
  'mount', 'assets', 'views', 'ignite',
]);

/** Palavras que introduzem uma declaração — recebem ênfase própria. */
const DECLARATIONS = new Set([
  'action', 'blueprint', 'record', 'enum', 'trait', 'adopt', 'relay',
  'steady', 'static', 'shadow', 'stream', 'async', 'server', 'route',
]);

const LITERALS = new Set(['yes', 'no', 'void']);

/** Tipos canônicos das anotações. */
const TYPES = new Set([
  'Integer', 'Float', 'Number', 'String', 'Boolean', 'Cluster', 'Vault',
  'Void', 'Action', 'Stream', 'Any', 'Record', 'Enum', 'Blueprint', 'Error',
  'Server',
]);

const OPERATORS = [
  '...', ':=', '**', '~/', '>>', '=>', '->', '??', '?.', '+=', '-=', '*=',
  '/=', '%=', '<=', '>=', '==', '!=', '+', '-', '*', '/', '%', '<', '>',
];

const PUNCT = new Set(['(', ')', '[', ']', '{', '}', ',', ':', '.', '@']);

const ehIdentInicio = (c: string) => /[A-Za-z_]/.test(c);
const ehIdent = (c: string) => /[A-Za-z0-9_]/.test(c);
const ehDigito = (c: string) => /[0-9]/.test(c);

/**
 * Decide se o `//` na posição dada é divisão inteira ou comentário.
 * Reproduz `Lexer._looks_like_floor_div` do interpretador.
 */
function ehDivisaoInteira(fonte: string, pos: number, ultimo: Token | null): boolean {
  if (!ultimo) return false;
  const fecha = ['plain', 'number', 'string', 'literal', 'property'].includes(ultimo.kind);
  const fechaPunct = ultimo.kind === 'punct' && [')', ']', '}'].includes(ultimo.text);
  if (!fecha && !fechaPunct) return false;

  const resto = fonte.slice(pos + 2).split('\n')[0];
  const depois = resto.replace(/^\s+/, '');
  if (!depois) return false;

  const c = depois[0];
  if (ehDigito(c) || c === '(') return true;
  if (c === '-' && (ehDigito(depois[1]) || depois[1] === '(')) return true;
  if (ehIdentInicio(c)) {
    let i = 0;
    while (i < depois.length && ehIdent(depois[i])) i++;
    return ['(', '[', '.'].includes(depois[i] ?? '');
  }
  return false;
}

export function tokenize(fonte: string): Token[] {
  const saida: Token[] = [];
  let i = 0;
  const n = fonte.length;

  const ultimoSignificativo = (): Token | null => {
    for (let k = saida.length - 1; k >= 0; k--) {
      if (saida[k].kind !== 'plain' || saida[k].text.trim() !== '') return saida[k];
    }
    return null;
  };

  const empurrar = (kind: TokenKind, text: string) => {
    if (text) saida.push({ kind, text });
  };

  while (i < n) {
    const c = fonte[i];

    // Espaços e quebras preservados como estão
    if (c === ' ' || c === '\n' || c === '\t' || c === '\r') {
      let j = i;
      while (j < n && /[ \n\t\r]/.test(fonte[j])) j++;
      empurrar('plain', fonte.slice(i, j));
      i = j;
      continue;
    }

    // Comentário de bloco
    if (c === '/' && fonte[i + 1] === '*') {
      const fim = fonte.indexOf('*/', i + 2);
      const ate = fim === -1 ? n : fim + 2;
      empurrar('comment', fonte.slice(i, ate));
      i = ate;
      continue;
    }

    // Comentário de linha com '#'
    if (c === '#') {
      let j = i;
      while (j < n && fonte[j] !== '\n') j++;
      empurrar('comment', fonte.slice(i, j));
      i = j;
      continue;
    }

    // '//' — comentário ou divisão inteira
    if (c === '/' && fonte[i + 1] === '/') {
      if (ehDivisaoInteira(fonte, i, ultimoSignificativo())) {
        empurrar('operator', '//');
        i += 2;
        continue;
      }
      let j = i;
      while (j < n && fonte[j] !== '\n') j++;
      empurrar('comment', fonte.slice(i, j));
      i = j;
      continue;
    }

    // String interpolada: $"...{expr}..."
    if (c === '$' && (fonte[i + 1] === '"' || fonte[i + 1] === "'")) {
      const aspas = fonte[i + 1];
      let j = i + 2;
      let buffer = '$' + aspas;
      while (j < n) {
        if (fonte[j] === '\\') {
          buffer += fonte.slice(j, j + 2);
          j += 2;
          continue;
        }
        if (fonte[j] === '{' && fonte[j + 1] === '{') {
          buffer += '{{';
          j += 2;
          continue;
        }
        if (fonte[j] === '{') {
          empurrar('interp', buffer);
          buffer = '';
          empurrar('punct', '{');
          j++;
          // O miolo é código: tokeniza recursivamente até fechar
          let nivel = 1;
          const inicio = j;
          while (j < n && nivel > 0) {
            if (fonte[j] === '"' || fonte[j] === "'") {
              const q = fonte[j++];
              while (j < n && fonte[j] !== q) {
                if (fonte[j] === '\\') j++;
                j++;
              }
              j++;
              continue;
            }
            if (fonte[j] === '{') nivel++;
            else if (fonte[j] === '}') nivel--;
            if (nivel > 0) j++;
          }
          for (const t of tokenize(fonte.slice(inicio, j))) saida.push(t);
          empurrar('punct', '}');
          j++;
          continue;
        }
        if (fonte[j] === aspas) {
          buffer += aspas;
          j++;
          break;
        }
        buffer += fonte[j];
        j++;
      }
      empurrar('interp', buffer);
      i = j;
      continue;
    }

    // String comum, inclusive tripla
    if (c === '"' || c === "'") {
      const tripla = fonte[i + 1] === c && fonte[i + 2] === c;
      if (tripla) {
        const fim = fonte.indexOf(c.repeat(3), i + 3);
        const ate = fim === -1 ? n : fim + 3;
        empurrar('string', fonte.slice(i, ate));
        i = ate;
        continue;
      }
      let j = i + 1;
      while (j < n && fonte[j] !== c) {
        if (fonte[j] === '\\') j++;
        j++;
      }
      empurrar('string', fonte.slice(i, Math.min(j + 1, n)));
      i = j + 1;
      continue;
    }

    // Número (decimal, hex, octal, binário, com separador _)
    if (ehDigito(c)) {
      let j = i;
      if (c === '0' && /[xXoObB]/.test(fonte[i + 1] ?? '')) {
        j = i + 2;
        while (j < n && /[0-9a-fA-F_]/.test(fonte[j])) j++;
      } else {
        while (j < n && /[0-9_]/.test(fonte[j])) j++;
        if (fonte[j] === '.' && ehDigito(fonte[j + 1] ?? '')) {
          j++;
          while (j < n && /[0-9_]/.test(fonte[j])) j++;
        }
      }
      empurrar('number', fonte.slice(i, j));
      i = j;
      continue;
    }

    // Identificador, palavra-chave, tipo ou chamada
    if (ehIdentInicio(c)) {
      let j = i;
      while (j < n && ehIdent(fonte[j])) j++;
      const palavra = fonte.slice(i, j);
      const anterior = ultimoSignificativo();
      const depoisDePonto = anterior?.kind === 'punct' && ['.', '?.'].includes(anterior.text);

      // Olha o próximo caractere não-espaço para detectar chamada
      let k = j;
      while (k < n && fonte[k] === ' ') k++;
      const chamada = fonte[k] === '(';

      if (LITERALS.has(palavra)) empurrar('literal', palavra);
      else if (depoisDePonto) empurrar(chamada ? 'function' : 'property', palavra);
      else if (DECLARATIONS.has(palavra)) empurrar('declaration', palavra);
      else if (KEYWORDS.has(palavra)) empurrar('keyword', palavra);
      else if (TYPES.has(palavra) || /^[A-Z]/.test(palavra)) empurrar('type', palavra);
      else if (chamada) empurrar('function', palavra);
      else empurrar('plain', palavra);
      i = j;
      continue;
    }

    // Operadores de vários caracteres
    const op = OPERATORS.find((o) => fonte.startsWith(o, i));
    if (op) {
      empurrar('operator', op);
      i += op.length;
      continue;
    }

    if (PUNCT.has(c)) {
      empurrar('punct', c);
      i++;
      continue;
    }

    empurrar('plain', c);
    i++;
  }

  return saida;
}

/** Classes CSS por tipo de token (definidas em app/globals.css). */
export const classePorTipo: Record<TokenKind, string> = {
  keyword: 'tk-keyword',
  declaration: 'tk-declaration',
  type: 'tk-type',
  string: 'tk-string',
  interp: 'tk-string',
  number: 'tk-number',
  comment: 'tk-comment',
  operator: 'tk-operator',
  punct: 'tk-punct',
  function: 'tk-function',
  literal: 'tk-literal',
  property: 'tk-property',
  plain: '',
};
