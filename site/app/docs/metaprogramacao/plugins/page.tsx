// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/metaprogramacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Plugins do check",
  description: "A regra que o seu projeto cobra, rodando no mesmo comando das 177 embutidas — com linha, coluna, código e silenciamento.",
};

const blocos: Bloco[] = [
  {"p": "O `dataforge check` tem 177 regras. O que ele não sabe é a regra **do seu projeto**: \"toda rota precisa de `middleware de autenticação`\", \"nenhum blueprint de domínio pode adotar `Arcane.Http`\", \"nome de uma letra não passa\". Um plugin é um `.df` que responde isso."},
  {"h2": "Um plugin é uma ação"},
  { code: `adopt Arcane.Macro as M

action verificar(arvore, arquivo):
    achados := []

    action olhar(nodo):
        given nodo["tipo"] is "Identifier" and len(nodo["nome"]) is 1:
            achados.append({"linha": nodo["linha"], "coluna": nodo["coluna"],
                            "codigo": "sem-nome-curto",
                            "mensagem": "nome de uma letra nao diz nada",
                            "sugestao": "use um nome que se leia",
                            "severidade": "aviso"})

    M.percorrer(arvore, olhar)
    yield achados

relay verificar`, lang: 'df', title: `regras.df` },
  {"p": "Rode com `--plugin`, ou declare no manifesto e esqueça:"},
  { code: `dataforge check src/ --plugin=regras.df`, lang: 'bash' },
  { code: `[check]
plugins = ["regras.df"]`, lang: 'toml', title: `forge.toml` },
  {"h2": "O contrato"},
  {"table": {"head": ["Campo do achado", "O que é"], "rows": [["`linha`, `coluna`", "onde acusar — vêm do nó (`nodo[\"linha\"]`)"], ["`codigo`", "o nome da regra; aparece na mensagem e serve para silenciar"], ["`mensagem`", "o que está errado"], ["`sugestao`", "o que fazer — a parte que faz a diferença"], ["`severidade`", "`\"erro\"` (padrão) ou `\"aviso\"`; erro reprova o comando"]]}},
  {"p": "A ação recebe a **árvore** (o mesmo dado de [`M.arvore`](/docs/metaprogramacao/macros)) e o caminho do arquivo, e devolve um cluster de achados. Nada mais."},
  {"h2": "Silenciar uma regra de plugin"},
  {"p": "O mesmo escape das regras embutidas vale aqui — e vale porque, sem ele, a única saída de quem discorda seria desligar o plugin inteiro:"},
  { code: `x := 1    // df: permitir sem-nome-curto`, lang: 'df' },
  {"h2": "Um plugin quebrado não derruba o check"},
  {"p": "Se o plugin não carrega, ou falha no meio, isso vira **diagnóstico** — com o nome do arquivo e o motivo. Quem roda o `check` quer o relatório do código dele, e não a pilha do analisador."},
  { code: `// saída quando o plugin falha:
//
//   alvo.df:1:1: erro: o plugin 'ruim.df' falhou: quebrei
//       sugestão: conserte o plugin, ou tire-o da lista
out "veja o bloco acima" `, lang: 'df' },
  {"h2": "O que um plugin alcança"},
  {"table": {"head": ["Dá para fazer", "Como"], "rows": [["lint próprio", "percorrer a árvore e acusar o que a equipe combinou"], ["análise de fluxo simples", "seguir a ordem das instruções dentro de uma ação"], ["convenção de arquitetura", "olhar `adopt` e acusar dependência proibida entre camadas"], ["verificação de esquema", "ler um `.json` do projeto e conferir contra o que o código declara"]]}},
  {"table": {"head": ["Não dá", "Por quê"], "rows": [["transformar a árvore antes de rodar", "o plugin do `check` **analisa**; reescrever é trabalho de macro, que roda na carga do arquivo"], ["adicionar palavra à linguagem", "isso é o parser, e mexe no DataForge"], ["rodar a cada tecla no editor", "o LSP usa as regras embutidas; o plugin roda no comando"]]}},
];

const headings = [{ id: 'um-plugin-e-uma-acao', text: "Um plugin é uma ação", level: 2 as const }, { id: 'o-contrato', text: "O contrato", level: 2 as const }, { id: 'silenciar-uma-regra-de-plugin', text: "Silenciar uma regra de plugin", level: 2 as const }, { id: 'um-plugin-quebrado-nao-derruba-o-check', text: "Um plugin quebrado não derruba o check", level: 2 as const }, { id: 'o-que-um-plugin-alcanca', text: "O que um plugin alcança", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Plugins do check"}
      description={"A regra que o seu projeto cobra, rodando no mesmo comando das 177 embutidas — com linha, coluna, código e silenciamento."}
      href={"/docs/metaprogramacao/plugins"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
