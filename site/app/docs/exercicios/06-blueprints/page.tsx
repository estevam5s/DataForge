// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "06 · Blueprints",
  description: "14 exercícios: campos, métodos, herança, traits e records.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 06`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["063", "**Blueprint com construtor**", "modele um ponto no plano com campos e um metodo."], ["064", "**Construtor com setup**", "use o metodo setup como construtor tradicional."], ["065", "**Estado mutavel**", "uma conta bancaria que muda de saldo."], ["066", "**Heranca com extends**", "especialize um blueprint reutilizando o pai."], ["067", "**root (super)**", "chame a implementacao do pai a partir do filho."], ["068", "**Traits (interfaces)**", "declare um contrato e implemente em dois blueprints."], ["069", "**Polimorfismo**", "calcule a area de formas diferentes pela mesma interface."], ["070", "**Membros estaticos**", "conte quantas instancias foram criadas."], ["071", "**Sobrecarga de operadores**", "some e multiplique vetores com + e *."], ["072", "**Composicao**", "um pedido composto por varios itens."], ["073", "**Cadeia de heranca**", "tres niveis de heranca e resolucao de metodos."], ["074", "**Introspeccao**", "descubra campos, metodos e tipo de uma instancia."], ["075", "**Padrao Singleton**", "garanta uma unica instancia de configuracao usando membro estatico."], ["076", "**Padrao Observador**", "notifique varios assinantes quando o estado mudar."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/06-blueprints/063_blueprint_basico.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"06 · Blueprints"}
      description={"14 exercícios: campos, métodos, herança, traits e records."}
      href={"/docs/exercicios/06-blueprints"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
