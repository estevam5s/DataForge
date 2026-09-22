// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Janelas",
  description: "Média móvel, acumulado, defasagem, variação e posição — os cinco verbos de janela do Quadro.",
};

const blocos: Bloco[] = [
  {"p": "As cinco perguntas de toda série: *a média dos últimos dias*, *o total até agora*, *o valor de ontem*, *quanto variou*, *qual a posição*. São cinco verbos do `Quadro`, e cada um devolve um quadro novo com uma coluna a mais."},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"dia": "2026-09-01", "loja": "centro", "valor": 120},
    {"dia": "2026-09-02", "loja": "centro", "valor": 150},
    {"dia": "2026-09-03", "loja": "centro", "valor": void},
    {"dia": "2026-09-04", "loja": "centro", "valor": 90},
    {"dia": "2026-09-05", "loja": "centro", "valor": 200},
    {"dia": "2026-09-01", "loja": "norte", "valor": 80},
    {"dia": "2026-09-02", "loja": "norte", "valor": 60}])

centro := vendas.onde(lambda l: l["loja"] is "centro").ordenar("dia")
q := centro
    .janela("valor", 2)
    .acumulado("valor")
    .defasar("valor")
    .variacao("valor")
    .ranquear("valor")
out q.pegar("dia", "valor", "valor_media_2", "valor_soma_acumulado", "valor_variacao", "valor_posicao").texto()

assert q.coluna("valor_soma_acumulado") is [120, 270, 270, 360, 560]
assert q.coluna("valor_antes_1") is [void, 120, 150, void, 90]
assert q.coluna("valor_posicao") is [3, 2, void, 4, 1]`, lang: 'df' },
  {"table": {"head": ["Verbo", "Responde", "A ponta"], "rows": [["`janela(col, n, agregacao)`", "a média (ou soma, máximo…) dos últimos `n`", "`void` até haver `n` valores válidos"], ["`acumulado(col, agregacao)`", "o total (ou máximo…) até a linha", "a ausência é pulada, não zera"], ["`defasar(col, n)`", "o valor de `n` linhas atrás (`-n`: à frente)", "`void` fora do quadro"], ["`variacao(col)`", "a razão em relação à linha anterior", "`void` se a anterior for 0 ou ausente"], ["`ranquear(col)`", "a posição, 1 é o maior", "a ausência não entra e sai `void`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Ordene antes", "texto": "Todas as janelas seguem a **ordem das linhas**. Uma média móvel sobre linhas fora de ordem calcula a média de dias que não são vizinhos — e nada denuncia. `ordenar(\"dia\")` antes de qualquer janela."}},
  {"callout": {"tipo": "dica", "titulo": "Por que `void` nas primeiras linhas", "texto": "A média móvel de 7 dias no dia 2 não existe: há só 2 dias. Devolver a média desses 2 fingiria ser uma média de 7, e o gráfico mostraria uma subida que é só a janela enchendo. Com `minimo := 1` você pede, de propósito, a média do que houver."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Janelas"}
      description={"Média móvel, acumulado, defasagem, variação e posição — os cinco verbos de janela do Quadro."}
      href={"/docs/dados/janelas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
