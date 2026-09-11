// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "05 · Acoes",
  description: "14 exercícios: parâmetros, padrões, retorno, closures e recursão.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 05`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["049", "**Acao basica**", "escreva uma acao que soma e outra sem retorno."], ["050", "**Parametros com valor padrao**", "permita chamar a acao com menos argumentos."], ["051", "**Argumentos nomeados**", "passe argumentos fora de ordem usando o nome."], ["052", "**Verificacao de aridade**", "comprove que argumentos faltando ou sobrando disparam erro."], ["053", "**Acoes tipadas**", "anote parametros e retorno e comprove a checagem."], ["054", "**Recursao**", "fatorial, fibonacci e soma de digitos."], ["055", "**Limite de recursao**", "comprove que recursao infinita vira erro controlado."], ["056", "**Acoes de alta ordem**", "passe acoes como argumento e devolva acoes."], ["057", "**Closures**", "crie um contador que preserva estado entre chamadas."], ["058", "**Lambdas**", "use acoes anonimas em variaveis e como argumento."], ["059", "**Decoradores com mark**", "envolva uma acao com log sem alterar seu corpo."], ["060", "**defer**", "agende limpeza que roda ao sair da acao."], ["061", "**Escopo e shadow**", "entenda quando uma acao le e quando cria uma variavel."], ["062", "**Memoizacao manual**", "acelere fibonacci guardando resultados ja calculados."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/05-acoes/049_acao_basica.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"05 · Acoes"}
      description={"14 exercícios: parâmetros, padrões, retorno, closures e recursão."}
      href={"/docs/exercicios/05-acoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
