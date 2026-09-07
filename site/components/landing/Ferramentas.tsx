import { Vitrine, type Aba } from './Vitrine';

/* Todas as saídas abaixo foram copiadas de execuções reais das ferramentas. */

const verificar: Aba[] = [
  {
    titulo: 'Erros com sugestão',
    texto: 'O analisador confere nomes, campos e aridade antes de rodar — e diz o que fazer, não só o que houve.',
    terminal: 'dataforge check',
    linhas: [
      { t: 'dataforge check pedido.df', c: 'cmd' },
      { t: '' },
      { t: "pedido.df:9:5: erro: Action 'desconto' is missing argument(s): taxa", c: 'erro' },
      { t: '    sugestão: Call it as desconto(p, taxa)', c: 'dim' },
      { t: "pedido.df:10:5: erro: Record 'Pedido' has no field 'totall'", c: 'erro' },
      { t: "    sugestão: Did you mean 'total'?", c: 'dim' },
      { t: '' },
      { t: '✗ 2 erro(s), 0 aviso(s)', c: 'erro' },
    ],
  },
  {
    titulo: 'Otimista de propósito',
    texto: 'Quando não consegue provar que algo está errado, fica calado. Falso alarme ensina o usuário a ignorar mensagem.',
    terminal: 'dataforge check .',
    linhas: [
      { t: 'dataforge check .', c: 'cmd' },
      { t: '' },
      { t: '152_imports_seletivos.df:37:1: aviso:', c: 'aviso' },
      { t: "    Module 'geometria' was not found", c: 'aviso' },
      { t: '    sugestão: Available: Analytics, Arcane.Async…', c: 'dim' },
      { t: '' },
      { t: '✓ sem erros, 74 aviso(s) em 286 arquivo(s)', c: 'ok' },
    ],
  },
  {
    titulo: 'Rastro de pilha real',
    texto: 'Quando algo estoura em execução, o erro traz arquivo, linha, coluna, a linha do código e a cadeia de chamadas.',
    terminal: 'dataforge run',
    linhas: [
      { t: 'dataforge run relatorio.df', c: 'cmd' },
      { t: '' },
      { t: 'RuntimeError: Division by zero', c: 'erro' },
      { t: '  em relatorio.df:5:11', c: 'dim' },
      { t: '' },
      { t: '     5 |     yield soma ~/ len(itens)', c: 'info' },
      { t: '       |           ^', c: 'erro' },
      { t: '' },
      { t: '  Pilha de chamadas (mais recente primeiro):', c: 'info' },
      { t: '    em media                  relatorio.df:8', c: 'dim' },
      { t: '    em resumo                 relatorio.df:10', c: 'dim' },
    ],
  },
];

const padronizar: Aba[] = [
  {
    titulo: 'Formatador idempotente',
    texto: 'Formatar duas vezes dá o mesmo resultado — há teste para isso. A profundidade vem do lexer, nunca da contagem de espaços.',
    terminal: 'dataforge fmt',
    linhas: [
      { t: 'dataforge fmt torto.df', c: 'cmd' },
      { t: '  formatado  torto.df', c: 'info' },
      { t: '1 de 1 arquivo(s) reescritos', c: 'ok' },
      { t: '' },
      { t: '- action  soma(a,b):', c: 'erro' },
      { t: '-   x:=a+b', c: 'erro' },
      { t: '+ action soma(a, b):', c: 'ok' },
      { t: '+     x := a + b', c: 'ok' },
    ],
  },
  {
    titulo: 'Treze regras de higiene',
    texto: 'Nome fora do padrão, variável escrita e nunca lida, ramo redundante. Avisos, não erros — a decisão continua sua.',
    terminal: 'dataforge lint',
    linhas: [
      { t: 'dataforge lint sujo.df', c: 'cmd' },
      { t: '' },
      { t: "sujo.df:1:1: aviso: Action 'Calcular' does not follow snake_case", c: 'aviso' },
      { t: "    sugestão: Rename it to 'calcular'", c: 'dim' },
      { t: "sujo.df:2:5: aviso: Variable 'naoUsada' is assigned but never read", c: 'aviso' },
      { t: "    sugestão: Remove it, or rename it to '_naoUsada'", c: 'dim' },
      { t: "sujo.df:3:5: aviso: The 'otherwise' is redundant", c: 'aviso' },
      { t: '' },
      { t: '3 aviso(s) em 1 arquivo(s)', c: 'aviso' },
    ],
  },
  {
    titulo: 'Pronto para a esteira',
    texto: '--check não reescreve nada: apenas lista o que está fora do padrão e sai com código diferente de zero.',
    terminal: 'ci',
    linhas: [
      { t: 'dataforge fmt src/ --check', c: 'cmd' },
      { t: '' },
      { t: '  precisa formatar  src/relatorio.df', c: 'aviso' },
      { t: '  precisa formatar  src/pedido.df', c: 'aviso' },
      { t: '' },
      { t: '2 arquivo(s) fora do formato, 0 com erro', c: 'aviso' },
      { t: '' },
      { t: 'echo $?', c: 'cmd' },
      { t: '1', c: 'erro' },
    ],
  },
];

const provar: Aba[] = [
  {
    titulo: 'Runner de testes',
    texto: 'Descobre as ações que começam com test_, roda cada uma isolada e mostra o que falhou e por quê.',
    terminal: 'dataforge test',
    linhas: [
      { t: 'dataforge test soma_test.df', c: 'cmd' },
      { t: '' },
      { t: '✗ soma_test.df (2/3)', c: 'erro' },
      { t: '    FALHOU test_falha_de_proposito', c: 'erro' },
      { t: '      Expected 5, got 4', c: 'dim' },
      { t: '' },
      { t: '2 passaram, 1 falharam em 1 arquivo(s) — 0.02s', c: 'aviso' },
    ],
  },
  {
    titulo: 'REPL que responde tipo',
    texto: ':type mostra o tipo inferido, :ast a árvore, :check o diagnóstico. Dá para inspecionar sem sair do console.',
    terminal: 'dataforge repl',
    linhas: [
      { t: 'dataforge repl', c: 'cmd' },
      { t: '' },
      { t: 'forge> :type [1, 2, 3]', c: 'cmd' },
      { t: 'Cluster  = [1, 2, 3]', c: 'info' },
      { t: 'forge> :type "oi"', c: 'cmd' },
      { t: 'String  = oi', c: 'info' },
      { t: 'forge> [1,2,3,4] >> sift n: n % 2 is 0 >> morph n: n * 10', c: 'cmd' },
      { t: '=> [20, 40]', c: 'ok' },
    ],
  },
  {
    titulo: 'Documentação do código',
    texto: 'dataforge doc lê os comentários das ações e blueprints e escreve o Markdown da API.',
    terminal: 'dataforge doc',
    linhas: [
      { t: 'dataforge doc src/ --out=doc/API.md', c: 'cmd' },
      { t: '' },
      { t: '  lido      src/pedido.df      3 ações, 1 record', c: 'dim' },
      { t: '  lido      src/relatorio.df   5 ações', c: 'dim' },
      { t: '  escrito   doc/API.md', c: 'info' },
      { t: '' },
      { t: '✓ 8 símbolo(s) documentado(s)', c: 'ok' },
    ],
  },
];

export function Ferramentas() {
  return (
    <>
      <Vitrine
        titulo="Verificar"
        subtitulo="Análise estática com sugestão de correção, antes de a primeira linha rodar."
        abas={verificar}
      />
      <Vitrine
        titulo="Padronizar"
        subtitulo="Formatador idempotente e treze regras de higiene, com modo --check para a esteira."
        abas={padronizar}
      />
      <Vitrine
        titulo="Provar"
        subtitulo="Runner de testes, console interativo e gerador de documentação, tudo no mesmo binário."
        abas={provar}
      />
    </>
  );
}
