import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fixtures e ganchos",
  description: "Preparo e limpeza no mesmo lugar — e por que isso não é detalhe.",
};

const blocos: Bloco[] = [
  {"h2": "Os ganchos"},
  { code: `crucible "Ganchos":
    setup all:
        // uma vez, antes de tudo
        origem := "arquivo.csv"

    setup:
        // antes de CADA trial, num quadro novo
        base := 10

    teardown:
        // depois de cada trial, mesmo se ele falhar
        expect yes

    trial "usa o setup":
        expect base is 10`, lang: 'df' },
  {"p": "Os ganchos rodam da raiz para dentro: o `setup` mais geral prepara o terreno, o mais específico ajusta. A ordem inversa faria o ajuste ser sobrescrito pelo preparo."},
  {"h2": "Fixture: preparo e limpeza juntos"},
  {"p": "`provide` divide a fixture em duas metades. O que vem antes prepara; o que vem depois limpa:"},
  { code: `crucible "Banco":
    fixture banco():
        adopt Forge
        db := Forge.conectar(":memory:")
        Forge.executar(db, "create table t (id integer primary key)")
        provide db
        Forge.fechar(db)

    trial "usa o banco":
        expect banco() exists`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Por que juntos", "texto": "Escrever preparo e limpeza no mesmo lugar é o que impede a limpeza de ser esquecida — que é o modo mais comum de uma suíte passar a depender de ordem. Um recurso aberto e não fechado derruba o próximo teste por um motivo que não é dele."}},
  {"h2": "Suítes aninhadas"},
  {"p": "Uma suíte dentro de outra herda os ganchos e as fixtures da de fora:"},
  { code: `crucible "Loja":
    setup:
        estoque := 100

    crucible "Venda":
        trial "vê o estoque do pai":
            expect estoque is 100

    crucible "Devolução":
        setup:
            devolvidos := 5

        trial "vê os dois":
            expect estoque + devolvidos is 105`, lang: 'df' },
  {"p": "No relatório, o caminho aparece inteiro: `Loja > Devolução > vê os dois`."},
  {"h2": "Modificadores do trial"},
  { code: `crucible "Modificadores":
    trial "marcado" tagged "rápido", "unitário":
        expect 1 is 1

    trial "adiado" pending "esperando a API do fornecedor":
        expect 1 is 2

    trial "com prazo" within 100:
        expect 1 is 1

    trial "repetido" repeat 5:
        expect 1 is 1

    trial "é par" over [2, 4, 6]:
        expect caso % 2 is 0`, lang: 'df' },
  {"table": {"head": ["Modificador", "Faz"], "rows": [["`tagged \"a\", \"b\"`", "marca, para `--tag` e `--sem-tag`"], ["`pending \"motivo\"`", "não roda; o relatório mostra o motivo"], ["`only`", "com um `only` na suíte, **só** os focados rodam"], ["`repeat n`", "roda n vezes — instabilidade aparece"], ["`within ms`", "falha se passar do prazo"], ["`over [a, b, c]`", "um trial por linha, com `caso` ligado"]]}},
  {"h2": "Trial parametrizado"},
  {"p": "`over` gera um resultado por linha, e o nome do trial mostra qual falhou:"},
  { code: `crucible "Tabela":
    trial "dobra certo" over [[1, 2], [2, 4], [3, 6]]:
        expect caso[0] * 2 is caso[1]`, lang: 'df' },
  {"p": "Se o segundo caso falhar, o relatório diz `dobra certo [[2, 4]]` — não \"um dos três\"."},
  {"h2": "Foco"},
  {"p": "Com um `only` em qualquer trial da suíte, só os focados rodam. É para depurar, não para versionar:"},
  { code: `crucible "Depurando":
    trial "este" only:
        expect 1 is 1

    trial "aquele não roda":
        expect 1 is 2`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`only` esquecido é perigoso", "texto": "Um `only` commitado faz o CI rodar um teste e reportar verde. Vale uma regra de revisão — ou um `grep only` antes do push."}},
];

const headings = [{ id: 'os-ganchos', text: "Os ganchos", level: 2 as const }, { id: 'fixture-preparo-e-limpeza-juntos', text: "Fixture: preparo e limpeza juntos", level: 2 as const }, { id: 'suites-aninhadas', text: "Suítes aninhadas", level: 2 as const }, { id: 'modificadores-do-trial', text: "Modificadores do trial", level: 2 as const }, { id: 'trial-parametrizado', text: "Trial parametrizado", level: 2 as const }, { id: 'foco', text: "Foco", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fixtures e ganchos"}
      description={"Preparo e limpeza no mesmo lugar — e por que isso não é detalhe."}
      href={"/docs/crucible/fixtures"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
