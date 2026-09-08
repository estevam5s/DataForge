import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dublês",
  description: "Mock, spy e stub — e por que aqui são um objeto só.",
};

const blocos: Bloco[] = [
  {"p": "Um dublê finge ser outro objeto e anota o que lhe pediram. Serve para três coisas que costumam se confundir:"},
  {"table": {"head": ["", "O que faz"], "rows": [["**stub**", "devolve o que você mandou devolver"], ["**spy**", "deixa passar para o real e anota as chamadas"], ["**mock**", "as duas, mais expectativas sobre as chamadas"]]}},
  {"p": "Aqui é **um objeto só**, porque a diferença entre eles é como se usa, não o que são — e obrigar a escolher o nome certo antes de escrever o teste atrapalha mais que ajuda."},
  {"h2": "Programando respostas"},
  { code: `crucible "Dublês":
    trial "devolve o programado":
        m := Crucible.mock("servico")
        m.quando("buscar").devolve([1, 2, 3])
        expect m.buscar() is [1, 2, 3]

    trial "em sequência":
        m := Crucible.mock()
        m.quando("proximo").devolve_em_sequencia([1, 2, 3])
        expect [m.proximo(), m.proximo(), m.proximo()] is [1, 2, 3]

    trial "levanta o programado":
        m := Crucible.mock()
        m.quando("falhar").levanta("indisponível")
        expect(lambda => m.falhar()).to_raise()`, lang: 'df' },
  {"h2": "Verificando as chamadas"},
  { code: `crucible "Chamadas":
    trial "anota tudo":
        m := Crucible.mock("api")
        m.buscar(1)
        m.buscar(2)
        m.salvar("x")

        expect m.vezes("buscar") is 2
        expect m.foi_chamado("salvar") is yes
        expect m.foi_chamado("apagar") is no
        expect m.chamado_com("salvar", "x") is yes
        expect m.argumentos_de("buscar") is [[1], [2]]`, lang: 'df' },
  {"h2": "Spy: deixa passar e anota"},
  { code: `blueprint Calculadora:
    action dobro(x):
        yield x * 2

crucible "Spy":
    trial "o real roda, e a chamada fica registrada":
        espiao := Crucible.spy(spawn Calculadora())
        expect espiao.dobro(4) is 8
        expect espiao.chamado_com("dobro", 4) is yes`, lang: 'df' },
  {"h2": "Stub: só as respostas"},
  { code: `crucible "Stub":
    trial "programado de uma vez":
        s := Crucible.stub({"buscar": [1, 2], "contar": 2})
        expect s.buscar() is [1, 2]
        expect s.contar() is 2`, lang: 'df' },
  {"h2": "Onde isso encaixa no projeto"},
  {"p": "Dublê é o que torna [inversão de dependência](/docs/oop/solid) prática. Um serviço que recebe o repositório por parâmetro se testa sem banco nenhum:"},
  { code: `trait Repositorio:
    action salvar(nome)

blueprint Servico:
    action setup(repositorio):
        self.repositorio := repositorio

    action cadastrar(nome):
        given len(nome) smaller 2:
            trigger "nome curto demais"
        yield self.repositorio.salvar(nome)

crucible "Cadastro":
    trial "salva o que passa na validação":
        repo := Crucible.mock("repositorio")
        repo.quando("salvar").devolve("Ana")

        s := spawn Servico(repo)
        expect s.cadastrar("Ana") is "Ana"
        expect repo.chamado_com("salvar", "Ana") is yes

    trial "não salva o que não passa":
        repo := Crucible.mock("repositorio")
        s := spawn Servico(repo)

        expect(lambda => s.cadastrar("A")).to_raise()
        expect repo.foi_chamado("salvar") is no`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Cobre o que NÃO aconteceu", "texto": "O segundo trial cobra que o repositório **não** foi chamado. Sem o dublê, verificar isso exigiria olhar o banco — e um teste que precisa de banco para verificar uma regra de nome está testando a coisa errada."}},
  {"h2": "Congelando o relógio"},
  {"p": "Todo teste que toca data e hora falha uma vez por ano, na virada, se não congelar:"},
  { code: `crucible "Tempo":
    trial "instante fixo":
        relogio := Crucible.freeze_time(1700000000)
        expect yes
        relogio.liberar()`, lang: 'df' },
];

const headings = [{ id: 'programando-respostas', text: "Programando respostas", level: 2 as const }, { id: 'verificando-as-chamadas', text: "Verificando as chamadas", level: 2 as const }, { id: 'spy-deixa-passar-e-anota', text: "Spy: deixa passar e anota", level: 2 as const }, { id: 'stub-so-as-respostas', text: "Stub: só as respostas", level: 2 as const }, { id: 'onde-isso-encaixa-no-projeto', text: "Onde isso encaixa no projeto", level: 2 as const }, { id: 'congelando-o-relogio', text: "Congelando o relógio", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Dublês"}
      description={"Mock, spy e stub — e por que aqui são um objeto só."}
      href={"/docs/crucible/dubles"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
