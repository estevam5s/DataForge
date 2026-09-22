// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quando o import não resolve",
  description: "Os seis motivos de um adopt falhar, em ordem de frequência — e o comando que responde cada um.",
};

const blocos: Bloco[] = [
  {"p": "Um `adopt` que não resolve tem sempre uma de seis causas. Elas estão em ordem de frequência."},
  {"table": {"head": ["#", "Sintoma", "Causa", "O que fazer"], "rows": [["1", "`Module not found`", "caminho relativo errado — ele é relativo ao **arquivo**, e não ao diretório de trabalho", "`dataforge deps` mostra o que cada arquivo pede"], ["2", "acha em desenvolvimento e não no CI", "o pacote não está no `forge.toml`; funcionava pelo cache local", "`dataforge install` numa pasta limpa"], ["3", "`import cycle`", "A importa B, que importa A", "`dataforge check` mostra a cadeia"], ["4", "o nome existe e o símbolo não", "`relay` não o exporta", "confira o `relay` do outro arquivo"], ["5", "instalação velha no PATH", "há até três lugares: `.venv/`, `~/.dataforge/`, o Python do sistema", "`which dataforge` e `dataforge --version`"], ["6", "funciona no Mac e falha no Linux", "maiúscula no nome do arquivo — o macOS não diferencia", "renomeie tudo em minúsculas"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A instalação velha é a mais enganosa", "texto": "Uma cópia antiga no PATH produz erros que **não existem no repositório** — foi assim que um `LexError: Unexpected character: '$'` apareceu num arquivo que usava interpolação normalmente. O `.venv` deve estar em modo editável (`pip install -e .`), que aponta para a árvore e nunca envelhece."}},
  {"h2": "Onde a resolução mora"},
  {"p": "Num lugar só: `resolucao.py`. Isso não é organização — é uma correção. A regra já esteve escrita em **três** lugares, e os três divergiram."},
  {"table": {"head": ["Onde estava", "O que dava errado"], "rows": [["no analisador", "`nome.replace('.', os.sep)` transformava `'./mod'` em `'//mod'` — **795 de 795** avisos falsos num projeto de 21 mil linhas"], ["no `dataforge deps`", "uma expressão regular que começava em `[A-Za-z_]`, então `./vizinho` nunca casava: o comando dizia *“0 arquivos com imports próprios”* em todo projeto"], ["no interpretador", "a cópia que funcionava"]]}},
  {"callout": {"tipo": "dica", "titulo": "Um aviso que mente é pior que nenhum aviso", "texto": "Cada aviso de *“Module not found”* que o `check` emitia num `adopt` relativo era mentira — e um analisador que erra no caminho mais comum é um analisador que se desliga. `tests/test_resolucao.py` cobre os quatro casos e **proíbe a cópia voltar**."}},
  {"p": "Continue em [Resolução](/docs/modulos/resolucao) e [Organizar](/docs/modulos/organizar)."},
];

const headings = [{ id: 'onde-a-resolucao-mora', text: "Onde a resolução mora", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Quando o import não resolve"}
      description={"Os seis motivos de um adopt falhar, em ordem de frequência — e o comando que responde cada um."}
      href={"/docs/modulos/diagnostico"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
