// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge debug, dap e lsp",
  description: "Parar numa linha, vigiar um valor, e o editor com breakpoints na margem.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge debug` roda o programa parando onde você mandar. Ele funciona por ssh, num contêiner, em qualquer terminal — e é a mesma máquina que o editor usa pelo `dap`."},
  { code: `dataforge debug conta.df                         # para na primeira instrucao
dataforge debug conta.df --parar=42,57           # paradas nas linhas 42 e 57
dataforge debug conta.df --vigiar=saldo          # para quando 'saldo' MUDAR
dataforge debug conta.df --vigiar-leitura=saldo  # para quando 'saldo' for LIDO`, lang: 'bash' },
  {"h2": "Dentro do depurador"},
  {"table": {"head": ["Comando", "Faz"], "rows": [["`p`", "passo: entra na ação chamada"], ["`n`", "próximo: passa por cima da chamada"], ["`f`", "sai da ação atual"], ["`c`", "continua até a próxima parada"], ["`vars`", "o escopo onde você parou"], ["`pilha`", "quem chamou quem"], ["`w saldo` / `r saldo`", "vigia de escrita / de leitura, a partir daqui"], ["qualquer expressão", "avaliada no quadro onde você parou"]]}},
  {"h2": "Vigia de escrita e de leitura são perguntas diferentes"},
  {"table": {"head": ["", "`--vigiar`", "`--vigiar-leitura`"], "rows": [["pergunta", "*quem mudou isto?*", "*quem está consultando isto?*"], ["como", "compara uma foto estrutural depois de cada instrução", "intercepta a leitura do nome e de `obj.campo`"], ["onde para", "na linha que **acabou** de mudar", "na linha que leu"]]}},
  {"callout": {"tipo": "dica", "titulo": "Custo zero quando desligado", "texto": "O depurador não é um `if` no caminho quente: ele **substitui** o método de execução enquanto roda, e sai com `del`. O programa sem depurador não paga nada por ele existir."}},
  {"h2": "No editor"},
  {"p": "`dataforge dap` fala o Debug Adapter Protocol — breakpoints na margem, pilha no painel, variáveis em árvore, data breakpoints de escrita **e** de leitura. Você não o roda à mão: a extensão o inicia no F5. `dataforge lsp` é o servidor de linguagem: hover, completar, ir para a definição, os diagnósticos do `check` enquanto você digita."},
  { code: `dataforge editor          # instala a extensao (cores, snippets, LSP, DAP)
dataforge editor status   # onde ela esta instalada`, lang: 'bash' },
  {"p": "Continue em [O editor](/docs/editor) e [LSP](/docs/tecnicas/lsp)."},
];

const headings = [{ id: 'dentro-do-depurador', text: "Dentro do depurador", level: 2 as const }, { id: 'vigia-de-escrita-e-de-leitura-sao-perguntas-diferentes', text: "Vigia de escrita e de leitura são perguntas diferentes", level: 2 as const }, { id: 'no-editor', text: "No editor", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge debug, dap e lsp"}
      description={"Parar numa linha, vigiar um valor, e o editor com breakpoints na margem."}
      href={"/docs/cli/debug"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
