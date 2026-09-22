// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Parar o que não se usa",
  description: "Efeito, inscrição, histórico e recurso seguram referências: sem parar, a tela fechada continua reagindo.",
};

const blocos: Bloco[] = [
  {"p": "Um efeito registrado num sinal fica vivo enquanto o sinal viver. Se a tela que o criou fecha e ninguém o para, ele continua rodando a cada mudança — redesenhando o que não existe, e segurando na memória tudo o que o fechamento dele alcança."},
  { code: `adopt Arcane.Reativo as R

contador := R.sinal(0)
execucoes := [0]

action mostrar():
    execucoes[0] += 1
    out $"contador: {contador.ler()}"

vigia := R.efeito(mostrar)

contador.escrever(1)
assert execucoes[0] is 2              // uma ao nascer, uma pela mudança

vigia.parar()
contador.escrever(2)
assert execucoes[0] is 2              // parado: não roda mais
assert contador.ouvintes() is 0       // e o sinal não o segura`, lang: 'df' },
  {"table": {"head": ["Peça", "Como parar"], "rows": [["efeito", "`e.parar()`"], ["inscrição num observável", "`inscricao.cancelar()`"], ["`sinal.observar(acao)`", "chamar o cancelador que ele devolveu"], ["histórico", "`h.parar()`"], ["recurso", "`r.parar()`"], ["observável que acabou", "`o.encerrar()` — avisa `ao_fim` de cada inscrito"]]}},
  {"callout": {"tipo": "dica", "titulo": "`ouvintes()` para o teste", "texto": "Todo sinal responde quantos o escutam. Um teste que abre e fecha a tela cem vezes e confere `ouvintes()` no fim é a forma barata de pegar um vazamento antes de ele virar lentidão."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Parar o que não se usa"}
      description={"Efeito, inscrição, histórico e recurso seguram referências: sem parar, a tela fechada continua reagindo."}
      href={"/docs/reativo/vazamentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
