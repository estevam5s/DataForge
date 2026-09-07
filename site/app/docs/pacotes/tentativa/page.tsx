import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "tentativa",
  description: "Repetição com recuo exponencial, jitter e circuit breaker.",
};

const blocos: Bloco[] = [
  { code: `dataforge add tentativa`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "8 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Repetir só ajuda quando a falha é transitória. Repetir uma falha determinística — senha errada, JSON inválido — é gastar tempo para chegar ao mesmo lugar; por isso `parar_se` existe."},
  {"h2": "Uso"},
  { code: `adopt tentativa as R

dados := R.repetir(lambda => buscar_api(), 3)

politica := R.politica(5, 0.1, 2.0)
dados := R.com_politica(lambda => buscar_api(), politica)`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 8 símbolos:"},
  { code: `record Politica
blueprint Disjuntor
politica(tentativas := 3, espera_inicial := 0.1, fator := 2.0,
                espera_maxima := 30.0, jitter := yes)
espera_da_tentativa(p, n)
com_politica(acao, p, parar_se := void)
repetir(acao, tentativas := 3)
repetir_ate(condicao, tentativas := 10, espera := 0.1)
disjuntor(limite := 5, descanso := 30.0)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add tentativa
dataforge add tentativa@1.0.0
dataforge add tentativa@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"tentativa"}
      description={"Repetição com recuo exponencial, jitter e circuit breaker."}
      href={"/docs/pacotes/tentativa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
