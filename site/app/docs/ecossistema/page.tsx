// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O ecossistema",
  description: "O que a linguagem tem, o que ela não tem, e por quê — conferido contra o disco, e não escrito de memória.",
};

const blocos: Bloco[] = [
  {"p": "Esta seção responde perguntas sobre a linguagem como um todo: quais peças existem, quais não, que princípios decidiram o desenho, e onde o tempo de um programa vai. As respostas saem do **próprio código** — `Arcane.Ecossistema` confere o inventário contra os arquivos, e um módulo novo fora do mapa reprova a suíte."},
  { code: `adopt Arcane.Ecossistema as E

n := E.numeros()
assert n["modulos"] bigger 80
assert n["existem"] + n["equivalem"] + n["nao_existem"] is n["componentes"]
assert E.conferir()["ok"]`, lang: 'df' },
  {"cards": [{"href": "/docs/ecossistema/componentes", "title": "O ecossistema, conferido", "desc": "cada peça, com o arquivo que a implementa"}, {"href": "/docs/ecossistema/ausencias", "title": "O que não existe", "desc": "e o que há no lugar"}, {"href": "/docs/ecossistema/glossario", "title": "Glossário", "desc": "os termos, com a página que os explica"}, {"href": "/docs/ecossistema/comparacao", "title": "Comparada com outras", "desc": "Python, JavaScript, Go e Rust, lado a lado"}, {"href": "/docs/ecossistema/arquitetura", "title": "A arquitetura em arquivos", "desc": "onde mora cada fase"}, {"href": "/docs/ecossistema/decisoes", "title": "Decisões de desenho", "desc": "o que foi escolhido, e o que custou"}, {"href": "/docs/ecossistema/numeros", "title": "Os números", "desc": "contados do código, e não escritos à mão"}, {"href": "/docs/ecossistema/principios", "title": "Os dez princípios", "desc": "com prova que roda"}, {"href": "/docs/ecossistema/tensoes", "title": "As tensões", "desc": "onde dois princípios brigam"}, {"href": "/docs/ecossistema/percurso", "title": "Onde o tempo vai", "desc": "as fases de um arquivo, medidas"}, {"href": "/docs/ecossistema/referencia", "title": "Referência rápida", "desc": "a linguagem numa página"}, {"href": "/docs/ecossistema/mapa", "title": "Ecossistema: o mapa", "desc": "tudo, com o veredito"}]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O ecossistema"}
      description={"O que a linguagem tem, o que ela não tem, e por quê — conferido contra o disco, e não escrito de memória."}
      href={"/docs/ecossistema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
