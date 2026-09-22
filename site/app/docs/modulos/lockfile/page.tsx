// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O lockfile",
  description: "O que ele trava, por que ele precisa ser LIDO, e as duas regras que decidem os empates.",
};

const blocos: Bloco[] = [
  {"p": "O `forge.lock` guarda a versão exata e o **sha256** de cada pacote. Ele é versionado, e a razão é uma só: duas pessoas clonando o mesmo projeto em dias diferentes têm de receber a mesma árvore."},
  {"callout": {"tipo": "atencao", "titulo": "Um lockfile que ninguém lê não trava nada", "texto": "Este arquivo existia, era versionado, carregava o sha256 — e **nenhum caminho de instalação o consultava**. `_sincronizar` sempre resolvia as faixas do zero e reescrevia o arquivo. Duas pessoas recebiam árvores diferentes, e a “verificação de integridade” conferia um download **contra ele mesmo**. Vale conferir isso em qualquer gerenciador que você use: se `install` e `update` fazem a mesma coisa, o lock é decoração."}},
  {"table": {"head": ["Comando", "O que ele faz"], "rows": [["`install`", "instala **o que o lock fixa**, enquanto couber na faixa do `forge.toml`"], ["`update`", "resolve de novo dentro das faixas e **reescreve** o lock; com nomes, move só eles"], ["`add`", "move só o que está sendo adicionado — o resto continua travado"], ["`outdated`", "separa o que sobe com `update` do que exige mudar o `forge.toml`"]]}},
  {"h2": "As duas regras dos empates"},
  {"table": {"head": ["Regra", "Porque"], "rows": [["a **faixa do `forge.toml` vence o lock**", "o manifesto é a intenção; o lock é a memória da última resolução. Quem sobe o requisito está pedindo outra versão"], ["o **sha256 do lock é comparado com o que chegou**", "um tarball trocado numa versão já publicada **para a instalação**, com a mensagem dizendo o que fazer. É o ataque que um lockfile existe para impedir"]]}},
  {"h2": "O tarball é reprodutível"},
  {"p": "`mtime=0`, uid e gid zerados. Sem isso o sha256 mudaria a cada empacotamento, a verificação de integridade não significaria nada — e, pior, pareceria significar."},
  { code: `cd packages/validador
dataforge pack                      # o tarball, com sha256 estavel
dataforge pack && dataforge pack    # o MESMO sha256 nas duas vezes`, lang: 'bash' },
  {"p": "Continue em [O registro](/docs/modulos/registro) e [Versão e compatibilidade](/docs/bibliotecas/versao)."},
];

const headings = [{ id: 'as-duas-regras-dos-empates', text: "As duas regras dos empates", level: 2 as const }, { id: 'o-tarball-e-reprodutivel', text: "O tarball é reprodutível", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O lockfile"}
      description={"O que ele trava, por que ele precisa ser LIDO, e as duas regras que decidem os empates."}
      href={"/docs/modulos/lockfile"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
