// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Resolução de módulos",
  description: "O algoritmo exato: as cinco formas de pedir um módulo, e a ordem em que a linguagem procura cada uma.",
};

const blocos: Bloco[] = [
  {"p": "\"Module not found\" é uma das mensagens mais frustrantes que existem, e quase sempre porque o algoritmo de busca é folclore. Aqui ele é curto o bastante para caber numa página — e é **uma implementação só**, em `resolucao.py`, usada pelo interpretador e pelo analisador."},
  {"callout": {"tipo": "atencao", "titulo": "Por que uma só", "texto": "A regra já esteve escrita em dois lugares, e eles divergiram: o analisador transformava `./mod` em `//mod`, e **todo** `adopt` relativo de **todo** projeto gerava um aviso falso — 795 de 795 num projeto de 21 mil linhas. Um aviso que está sempre errado é pior que nenhum aviso."}},
  {"h2": "As cinco formas"},
  {"table": {"head": ["O que você escreve", "Resolve contra"], "rows": [["`Arcane.Math`", "a biblioteca padrão"], ["`Python.numpy`", "a ponte para o Python (não passa pela busca em disco)"], ["`./util`, `../lib/util`", "a pasta do **arquivo que escreve o import**"], ["`sub.modulo`", "a pasta do arquivo, depois o diretório atual"], ["`validador`", "`forge_modules/`, subindo até achar um `forge.toml`"]]}},
  {"p": "**Relativo resolve a partir do arquivo, nunca do diretório de onde se rodou.** É o que permite mover a pasta inteira sem quebrar nada, e o que torna a leitura do arquivo suficiente para saber o que ele importa."},
  {"h2": "A ordem, para um caminho relativo"},
  {"p": "`adopt ./util` procura, nesta ordem:"},
  { code: `./util               (o caminho exato, se for um arquivo)
./util.df
./util/main.df
./util/src/main.df
`, lang: 'text' },
  {"p": "A ordem importa porque um arquivo e uma pasta com o mesmo nome podem coexistir. Sem ela declarada, a escolha dependeria da ordem em que o sistema de arquivos devolve os nomes."},
  {"h2": "A ordem, para um nome pontilhado"},
  {"p": "`adopt sub.modulo` troca o ponto por separador de pasta — **e só aqui**, depois de o caso relativo ter sido descartado:"},
  { code: `<pasta do arquivo>/sub/modulo.df
<pasta do arquivo>/sub/modulo/main.df
<pasta do arquivo>/sub/modulo/src/main.df
<diretório atual>/sub/modulo.df
<diretório atual>/sub/modulo/main.df
<diretório atual>/sub/modulo/src/main.df
`, lang: 'text' },
  {"h2": "Hífen num caminho relativo"},
  {"p": "`adopt ./minha-lib as L` funciona, e não é óbvio que devesse: o lexer entrega o hífen como operador de subtração. O segmento de caminho cola `-`, `.` e dígitos ao nome exigindo **adjacência de coluna** — sem essa guarda, `a - b` viraria um arquivo chamado `a-b`."},
  {"h2": "Um pacote se importa pelo próprio nome"},
  {"p": "O teste de uma biblioteca escreve `adopt validador`, e não `adopt ../src/main`, porque precisa exercitá-la pelo caminho que um usuário usaria. A busca sobe até o `forge.toml` mais próximo e olha o `forge_modules/` dali."},
  { code: `meu-projeto/
  forge.toml              o que você pediu      (versionado)
  forge.lock              o que foi instalado   (versionado)
  forge_modules/          os pacotes            (NÃO versionado)
  src/main.df
`, lang: 'text' },
  {"h2": "Quando não acha"},
  {"p": "A mensagem nomeia o que foi procurado, e não só o que faltou — um \"não encontrado\" sem a lista de tentativas obriga a adivinhar qual das cinco formas a linguagem achou que você estava usando."},
  {"p": "O `dataforge deps` mostra o grafo de imports do projeto e acusa ciclo, usando o mesmo `resolucao.py`. Ele já teve uma **terceira** cópia da regra — uma expressão regular que começava em `[A-Za-z_]`, de modo que `./vizinho` nunca casava — e dizia \"0 arquivos com imports próprios\" em todo projeto do repositório."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/modulos/carga", "title": "Carga e ciclos", "desc": "quando o arquivo executa, e o que acontece num círculo"}, {"href": "/docs/pacotes", "title": "Gerenciador de pacotes", "desc": "add, install, lock e o registro estático"}]},
];

const headings = [{ id: 'as-cinco-formas', text: "As cinco formas", level: 2 as const }, { id: 'a-ordem-para-um-caminho-relativo', text: "A ordem, para um caminho relativo", level: 2 as const }, { id: 'a-ordem-para-um-nome-pontilhado', text: "A ordem, para um nome pontilhado", level: 2 as const }, { id: 'hifen-num-caminho-relativo', text: "Hífen num caminho relativo", level: 2 as const }, { id: 'um-pacote-se-importa-pelo-proprio-nome', text: "Um pacote se importa pelo próprio nome", level: 2 as const }, { id: 'quando-nao-acha', text: "Quando não acha", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Resolução de módulos"}
      description={"O algoritmo exato: as cinco formas de pedir um módulo, e a ordem em que a linguagem procura cada uma."}
      href={"/docs/modulos/resolucao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
