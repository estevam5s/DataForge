import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Estrutura de projeto",
  description: "Camadas, forge.toml e como organizar código que cresce.",
};

const blocos: Bloco[] = [
  {"h2": "Começar"},
  { code: `dataforge init meu-app
cd meu-app`, lang: 'bash' },
  { code: `meu-app/
  forge.toml                 manifesto
  src/main.df                o programa
  tests/principal_test.df    os testes`, lang: 'text' },
  {"h2": "As quatro camadas"},
  {"table": {"head": ["Camada", "Contém", "Depende de"], "rows": [["**Modelo**", "records, enums, invariantes", "nada"], ["**Regras**", "decisões de negócio", "modelo"], ["**Apresentação**", "como virar texto", "modelo, regras"], ["**Aplicação**", "orquestra o fluxo", "todas"]]}},
  {"p": "As setas apontam sempre para baixo. O modelo não sabe que existe apresentação; as regras não sabem se o resultado vira terminal, HTTP ou CSV."},
  {"h2": "Num projeto real"},
  { code: `src/
  modelo.df          record Produto, enum Situacao
  regras.df          situacao_de, precisa_repor
  apresentacao.df    formatar_produto, cabecalho
  main.df            junta tudo
tests/
  regras_test.df
forge.toml`, lang: 'text' },
  {"p": "E cada módulo declara sua interface:"},
  { code: `// regras.df
relay LIMITE_CRITICO, situacao_de, precisa_repor` },
  {"h2": "Por que separar"},
  {"p": "O critério prático é **o que muda junto**:"},
  {"list": ["Trocar o limite de estoque crítico → mexe só em `regras.df`", "Trocar o terminal por uma página web → mexe só em `apresentacao.df`", "Acrescentar um campo ao produto → mexe em `modelo.df` e em quem usa o campo"]},
  {"p": "Quando tudo está num arquivo, qualquer mudança arrisca qualquer coisa."},
  {"h2": "Regras puras são testáveis"},
  { code: `action situacao_de(p: Produto) -> Situacao:
    given p.estoque is 0:
        yield Situacao.EmFalta
    orif p.estoque smaller LIMITE_CRITICO:
        yield Situacao.Critico
    yield Situacao.Normal` },
  {"p": "Essa ação não imprime, não lê arquivo, não consulta banco. O teste é uma linha e roda em microssegundos."},
  {"h2": "Converter na fronteira"},
  {"p": "O banco guarda linhas; o programa trabalha com records:"},
  { code: `action buscar_todos():
    linhas := DB.query(conn, "SELECT id, nome, preco FROM produtos")
    yield linhas >> morph l: Produto(l["id"], l["nome"], l["preco"])` },
  {"p": "Essa conversão paga por si: dali em diante o código usa `p.nome` com verificação de tipo, em vez de `l[\"nome\"]` com risco de digitar errado. E se a coluna mudar de nome, só esta linha muda."},
  {"h2": "O ciclo de trabalho"},
  { code: `dataforge check src/          # nomes, tipos, aridade
dataforge lint src/           # estilo e higiene
dataforge fmt src/            # formatar
dataforge test tests/ -v      # testes
dataforge doc src/ --out=doc/API.md
dataforge run                 # executar`, lang: 'bash' },
];

const headings = [{ id: 'comecar', text: "Começar", level: 2 as const }, { id: 'as-quatro-camadas', text: "As quatro camadas", level: 2 as const }, { id: 'num-projeto-real', text: "Num projeto real", level: 2 as const }, { id: 'por-que-separar', text: "Por que separar", level: 2 as const }, { id: 'regras-puras-sao-testaveis', text: "Regras puras são testáveis", level: 2 as const }, { id: 'converter-na-fronteira', text: "Converter na fronteira", level: 2 as const }, { id: 'o-ciclo-de-trabalho', text: "O ciclo de trabalho", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Estrutura de projeto"}
      description={"Camadas, forge.toml e como organizar código que cresce."}
      href={"/docs/tecnicas/projeto"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
