// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O CI de uma biblioteca",
  description: "O que só quebra fora da sua máquina — e o formato de defeito que isso sempre tem.",
};

const blocos: Bloco[] = [
  {"p": "A suíte local **não é o que o CI roda**, e a diferença não é detalhe. Todo defeito desta classe tem o mesmo formato: uma decisão do ambiente que o repositório não contém."},
  { code: `name: ci
on: [push, pull_request]
jobs:
  testes:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-15, windows-latest]
        python: ["3.10", "3.13"]
    runs-on: \${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "\${{ matrix.python }}" }
      - run: pip install dataforge-lang
      - run: dataforge check . --strict
      - run: dataforge fmt . --check
      - run: dataforge test . --cobertura --minimo=80
      - run: dataforge install && dataforge test .   # numa pasta limpa`, lang: 'yaml' },
  {"h2": "As cinco do Windows"},
  {"table": {"head": ["Sintoma", "Causa"], "rows": [["`[Errno 22]` com o caminho mutilado", "`\"C:\\temp\"` numa string: `\\t` é tabulação. Em macOS e Linux é **pior** — o nome é válido, e o arquivo nasce em outro lugar sem erro nenhum"], ["traceback depois de o pacote estar pronto", "`which` é do Unix; use `shutil.which`, que também conhece `PATHEXT`"], ["`WSAEINVAL (10022)`", "`getsockname` num socket ainda **não ligado**; no Unix devolve 0"], ["a conexão “expira” onde devia ser recusada", "o firewall **descarta** o SYN de uma porta fechada"], ["saída ilegível de um subprocesso", "a saída do Windows não é UTF-8 — declare `encoding`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Um runner que não existe não dá erro: ele nunca começa", "texto": "O primeiro release deste projeto ficou meia hora com um job em `queued` enquanto os outros três terminavam — sem mensagem, sem falha, sem prazo. `macos-13` tinha sido **retirado** pelo GitHub. Não havia histórico dizendo que aquele runner nunca tinha funcionado, porque era o primeiro release. Prenda os rótulos de runner a uma lista conferida."}},
  {"h2": "O relatório também mente"},
  {"table": {"head": ["O quê", "O efeito"], "rows": [["`pytest -rf` lista o que **falhou**, não o que deu **erro**", "11 erros invisíveis no resumo por meses — use `-rfE`"], ["o resumo corta no primeiro `\\n`", "a anotação do job mostrou a **primeira linha de um stdout de sucesso** como motivo de reprovação"], ["o que é gerado fora do repositório não existe no CI", "todo pacote saiu com o manifesto e **zero** JavaScript, porque a compilação só rodava nesta máquina"]]}},
  {"p": "Continue em [Prometer desempenho](/docs/bibliotecas/desempenho) e [DevOps](/docs/devops)."},
];

const headings = [{ id: 'as-cinco-do-windows', text: "As cinco do Windows", level: 2 as const }, { id: 'o-relatorio-tambem-mente', text: "O relatório também mente", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O CI de uma biblioteca"}
      description={"O que só quebra fora da sua máquina — e o formato de defeito que isso sempre tem."}
      href={"/docs/bibliotecas/ci"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
