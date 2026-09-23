// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Editor: cores, autocompletar e depurador",
  description: "O que a extensão faz, o que o LSP responde, e como parar o programa numa linha — inclusive por ssh.",
};

const blocos: Bloco[] = [
  {"p": "A pergunta costuma vir como *\"tem plugin?\"*. Tem, e ele é instalado pela própria CLI — a gramática de cores é **gerada** do `tokens.py`, então ela não pode discordar do lexer."},
  {"h2": "Instalar"},
  { code: `$ dataforge editor`, lang: 'bash' },
  {"p": "Ele instala no VS Code e nos derivados (Cursor, VSCodium, Windsurf). A coloração, os snippets, o ícone do `.df`, o cliente do LSP e o adaptador de depuração vão juntos."},
  {"callout": {"tipo": "atencao", "titulo": "Instalado por `pip`, a extensão precisa estar compilada", "texto": "`editor/vscode/out/` é gerado por `tsc` e não é versionado. Um wheel construído sem ele sai com o manifesto e **zero JavaScript**: o VS Code carrega a extensão e nada acontece. Há teste que constrói o wheel e olha dentro — conferir o texto do `pyproject.toml` não diz o que o build produz."}},
  {"h2": "O que o LSP responde"},
  {"table": {"head": ["Recurso", "O que faz"], "rows": [["hover", "o tipo e a doc do que está sob o cursor"], ["ir-para-definição", "inclusive atravessando `adopt`"], ["completar", "**olha o contexto**: depois de `p.`, os membros de `p`"], ["diagnósticos", "os mesmos do `dataforge check`, enquanto você digita"], ["`// df: permitir <regra>`", "silencia ali, lido do **texto do editor**"]]}},
  {"p": "Os nomes do **próprio arquivo** vêm antes dos 2323 símbolos da biblioteca — é o que se procura em nove de cada dez vezes. E o comentário que silencia uma regra é lido do buffer, não do disco: num arquivo não salvo, ler do disco silenciaria a regra errada — ou nenhuma."},
  {"h2": "Depurar"},
  { code: `$ dataforge debug programa.df      # no terminal, e serve por ssh
$ dataforge dap                    # o mesmo no painel do editor (F5)`, lang: 'bash' },
  {"table": {"head": ["Comando", "Faz"], "rows": [["`n`", "a próxima linha, sem entrar"], ["`s`", "entra na ação"], ["`c`", "segue até a próxima parada"], ["`w saldo`", "para quando `saldo` **mudar**"], ["`r saldo`", "para quando `saldo` for **lido**"]]}},
  {"callout": {"tipo": "nota", "titulo": "Vigiar leitura é outro mecanismo, não uma opção", "texto": "`w` responde *quem mudou isto?* e compara uma foto estrutural depois de cada instrução. `r` responde *quem está consultando isto?* — e uma leitura não muda nada, então não há foto a comparar: ela intercepta os dois caminhos que leem. Custo zero quando não há nenhuma vigia."}},
  {"p": "O depurador **desliga a compilação para fechamentos**: ele para em cada linha sombreando `execute`, e o corpo compilado passaria por fora. Um depurador que enxerga metade das instruções é pior que um interpretador mais lento."},
  {"cards": [{"href": "/docs/editor", "title": "Editor", "desc": "a extensão em detalhe"}, {"href": "/docs/tecnicas/lsp", "title": "O servidor de linguagem", "desc": "como ele responde"}, {"href": "/docs/cli/debug", "title": "Depurador", "desc": "parar, ver e andar"}]},
];

const headings = [{ id: 'instalar', text: "Instalar", level: 2 as const }, { id: 'o-que-o-lsp-responde', text: "O que o LSP responde", level: 2 as const }, { id: 'depurar', text: "Depurar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Editor: cores, autocompletar e depurador"}
      description={"O que a extensão faz, o que o LSP responde, e como parar o programa numa linha — inclusive por ssh."}
      href={"/docs/faq/editor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
