// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O sistema de módulos",
  description: "adopt e relay — o que é público, onde mora cada módulo, e como isso se compara a CommonJS e a ECMAScript.",
};

const blocos: Bloco[] = [
  {"p": "Toda linguagem grande acaba precisando responder quatro perguntas sobre módulos: **o que um arquivo oferece**, **onde mora o que ele pede**, **quantas vezes ele carrega** e **o que acontece quando dois se pedem em círculo**. Esta seção responde as quatro, com o comportamento medido — não com a intenção."},
  {"p": "As duas palavras:"},
  { code: `adopt Arcane.Math as Math          // o módulo inteiro, com apelido
adopt Arcane.Math.{sqrt, floor}    // só o que interessa
adopt {sqrt as raiz} from Arcane.Math
adopt ./util as U                  // um arquivo vizinho

relay somar, Ponto                 // o que ESTE arquivo oferece
`, lang: 'df' },
  {"h2": "Ao lado de CommonJS e ECMAScript"},
  {"p": "A tabela existe para quem chega de uma das duas. Onde a DataForge difere, ela difere de propósito, e a coluna da direita diz por quê."},
  {"table": {"head": ["Pergunta", "CommonJS", "ECMAScript (ESM)", "DataForge"], "rows": [["importar", "`require('x')`", "`import x from 'x'`", "`adopt x as X`"], ["exportar", "`module.exports =`", "`export`", "`relay`"], ["export padrão", "sim (`module.exports`)", "sim (`export default`)", "**não existe**"], ["quando resolve", "em execução", "antes de executar", "em execução, e o `check` confere antes"], ["carrega quantas vezes", "uma", "uma", "**uma**"], ["o que é público sem declarar", "nada", "nada", "**tudo**"], ["ciclo", "devolve o parcial", "vive com TDZ", "**erro**"], ["import dinâmico", "`require()` em qualquer lugar", "`import()`", "não existe"], ["ordem de `export`", "irrelevante", "içado", "**depois** da declaração"]]}},
  {"callout": {"tipo": "nota", "titulo": "Sem export padrão, de propósito", "texto": "O `export default` obriga quem importa a inventar um nome, e dois arquivos que importam o mesmo módulo o chamam de coisas diferentes. Aqui o nome vem de quem escreveu (`relay somar`) ou do apelido explícito (`as U`) — e procurar por `somar` no projeto acha todos os usos."}},
  {"h2": "Tudo é público até você dizer o contrário"},
  {"p": "Um arquivo **sem** `relay` oferece tudo o que declara no topo. É o oposto do padrão de CommonJS e ESM, e a razão é o arquivo pequeno: obrigar um `relay` num módulo de três ações é cerimônia sem ganho."},
  { code: `interno := 42

action publica():
    yield "oi"
`, lang: 'df', title: `aberto.df` },
  { code: `adopt ./aberto as A
out A.publica(), A.interno       // oi 42 — os dois visíveis
`, lang: 'df' },
  {"p": "**O primeiro `relay` fecha a porta.** A partir dele, o arquivo declara o que exporta, e o resto vira interno:"},
  { code: `interno := 42

action publica():
    yield "oi"

relay publica          // agora 'interno' não atravessa mais
`, lang: 'df' },
  {"p": "Essa é também a fronteira que o analisador usa: um módulo com `relay` diz o que é contrato, e `A.interno` passa a ser acusado **antes de rodar**."},
  {"h2": "`relay` vem depois, e isso não é detalhe"},
  {"p": "Em JavaScript, `export function f(){}` funciona em qualquer posição, porque a declaração é içada. Aqui o `relay` **lê** os nomes que já existem:"},
  { code: `relay usar              // erro: 'usar' ainda não existe

action usar():
    yield 1
`, lang: 'df' },
  { code: `erro: 'usar' is not defined
  dica: define it before the 'relay', or remove it from the list
`, lang: 'text' },
  {"p": "A forma certa é o `relay` no fim do arquivo, que é também onde ele se lê melhor — a última linha responde \"o que este arquivo oferece?\" sem obrigar a percorrer tudo."},
  {"h2": "Um módulo carrega uma vez, e o estado é compartilhado"},
  {"p": "Como em CommonJS e em ESM. Dois arquivos que adotam o mesmo módulo recebem **o mesmo** módulo — e o estado dele é único no programa:"},
  { code: `out "carregando contador.df"
total := 0

action somar():
    total += 1
    yield total

relay somar
`, lang: 'df', title: `contador.df` },
  { code: `adopt ./contador as C

action usar():
    yield C.somar()

relay usar
`, lang: 'df', title: `a.df` },
  { code: `adopt ./contador as C
adopt ./a as A

out C.somar()      // 1
out A.usar()       // 2  — o MESMO contador
out C.somar()      // 3
`, lang: 'df', title: `main.df` },
  { code: `carregando contador.df
1
2
3
`, lang: 'text', title: `saída` },
  {"p": "A mensagem de carga aparece **uma vez**. É o que torna um módulo um bom lugar para configuração e um lugar perigoso para estado mutável: `total` acima é global ao programa, e duas rotas de um servidor escrevendo nele perdem atualizações — ver [concorrência](/docs/tecnicas/concorrencia)."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/modulos/resolucao", "title": "Resolução", "desc": "o algoritmo exato: onde a linguagem procura, e em que ordem"}, {"href": "/docs/modulos/carga", "title": "Carga e ciclos", "desc": "quando o arquivo executa, e o que acontece num círculo"}, {"href": "/docs/modulos/superficie", "title": "A superfície", "desc": "como o analisador atravessa a fronteira e confere a chamada"}, {"href": "/docs/modulos/templates", "title": "Templates", "desc": "a camada de visão, e por que ela não é a linguagem"}, {"href": "/docs/bibliotecas", "title": "Escrever uma biblioteca", "desc": "do primeiro arquivo ao pacote publicado"}]},
];

const headings = [{ id: 'ao-lado-de-commonjs-e-ecmascript', text: "Ao lado de CommonJS e ECMAScript", level: 2 as const }, { id: 'tudo-e-publico-ate-voce-dizer-o-contrario', text: "Tudo é público até você dizer o contrário", level: 2 as const }, { id: 'relay-vem-depois-e-isso-nao-e-detalhe', text: "`relay` vem depois, e isso não é detalhe", level: 2 as const }, { id: 'um-modulo-carrega-uma-vez-e-o-estado-e-compartilhado', text: "Um módulo carrega uma vez, e o estado é compartilhado", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O sistema de módulos"}
      description={"adopt e relay — o que é público, onde mora cada módulo, e como isso se compara a CommonJS e a ECMAScript."}
      href={"/docs/modulos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
