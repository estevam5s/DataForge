import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Módulos",
  description: "adopt, relay, imports seletivos e detecção de ciclos.",
};

const blocos: Bloco[] = [
  {"h2": "Importar"},
  { code: `adopt Arcane.Math as Math          # o módulo inteiro, sob um nome
adopt geometria as geo             # arquivo geometria.df ao lado

out Math.sqrt(16), geo.area_circulo(2)` },
  {"p": "A resolução segue esta ordem:"},
  {"list": ["módulos já carregados (cache — um arquivo só executa uma vez)", "biblioteca padrão (`Arcane.*` e os nomes curtos)", "arquivo `.df` **ao lado do arquivo que importa**"]},
  {"callout": {"tipo": "nota", "texto": "O terceiro ponto importa: o caminho é relativo ao **arquivo**, não ao diretório de onde você rodou o comando. Isso faz um projeto funcionar igual sendo executado da raiz ou de dentro de uma subpasta."}},
  {"h2": "Imports seletivos"},
  { code: `adopt Arcane.Math.{sqrt, floor}           # forma compacta
adopt {sqrt as raiz} from Arcane.Math     # com apelido

out sqrt(16), raiz(25)` },
  {"table": {"head": ["Forma", "Boa para"], "rows": [["`as geo`", "módulo com muitos símbolos; o prefixo documenta a origem"], ["`.{a, b}`", "dois ou três símbolos usados o tempo todo"], ["`{a as b} from`", "resolver conflito de nomes"]]}},
  {"p": "O prefixo não é burocracia: `Math.sqrt(x)` diz de onde `sqrt` veio. Num arquivo que importa cinco módulos, é o que evita a pergunta \"onde é que isso está definido?\"."},
  {"h3": "Apelidos resolvem colisões"},
  { code: `adopt {formatar as formatar_data} from datas
adopt {formatar as formatar_moeda} from dinheiro` },
  {"h2": "Exportar com relay"},
  { code: `// geometria.df
steady PI := 3.14159265

action area_circulo(raio):
    yield PI * raio ** 2

action _detalhe_interno():
    yield "nao deveria escapar"

relay PI, area_circulo`, title: `geometria.df` },
  {"table": {"head": ["No módulo", "Exporta"], "rows": [["nenhum `relay`", "tudo do nível superior"], ["pelo menos um `relay`", "só o que foi listado"]]}},
  {"p": "Sem `relay`, você tem a conveniência de um script. Com `relay`, tem uma **interface pública** — e o que ficou de fora é detalhe de implementação que pode ser reescrito sem quebrar ninguém."},
  { code: `adopt geometria as geo
out geo._detalhe_interno()
# Vault has no key '_detalhe_interno'` },
  {"p": "Essa é a diferença entre \"por convenção não use isso\" (o `_` do Python) e \"isso não está acessível\". A segunda é verificável."},
  {"h2": "Erros com mensagem útil"},
  { code: `Module 'Arcane.NaoExiste' not found.
Available: Analytics, Arcane.Analytics, Arcane.Async, …

Module 'geometria' does not export: nao_existe.
It exports: PI, area_circulo`, lang: 'text' },
  {"p": "As mensagens listam o que existe. Quase sempre o problema é um nome digitado errado, e ver a lista resolve sem abrir o outro arquivo."},
  {"h2": "Ciclos"},
  {"p": "Importes circulares são detectados, com a cadeia na mensagem:"},
  { code: `Circular import: ciclo_a.df → ciclo_b.df → ciclo_a.df.
Break the cycle by moving the shared part into a third module.`, lang: 'text' },
  {"h2": "Organizando um projeto"},
  { code: `src/
  modelo.df          record Produto, enum Situacao
  regras.df          decisões de negócio — puras
  apresentacao.df    como virar texto
  main.df            junta tudo
tests/
  regras_test.df
forge.toml`, lang: 'text' },
  {"p": "Cada camada depende só das de cima. O critério prático é **o que muda junto**: trocar o limite de estoque mexe só em `regras.df`; trocar o terminal por uma página web mexe só em `apresentacao.df`."},
  {"p": "Mais sobre isso em [Estrutura de projeto](/docs/tecnicas/projeto)."},
];

const headings = [{ id: 'importar', text: "Importar", level: 2 as const }, { id: 'imports-seletivos', text: "Imports seletivos", level: 2 as const }, { id: 'exportar-com-relay', text: "Exportar com relay", level: 2 as const }, { id: 'erros-com-mensagem-util', text: "Erros com mensagem útil", level: 2 as const }, { id: 'ciclos', text: "Ciclos", level: 2 as const }, { id: 'organizando-um-projeto', text: "Organizando um projeto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Módulos"}
      description={"adopt, relay, imports seletivos e detecção de ciclos."}
      href={"/docs/fundamentos/modulos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
