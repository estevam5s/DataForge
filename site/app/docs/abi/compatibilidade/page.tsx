// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_e_alvos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que quebra, e qual versão subir",
  description: "Onze regras nomeadas, o veredito de semver que a mudança exige, e o terceiro balde para o que a superfície não decide sozinha.",
};

const blocos: Bloco[] = [
  {"p": "O [gerenciador de pacotes](/docs/cli/pacotes) já tinha semver, `forge.lock` e verificação de integridade. O que faltava era **o que decide o número**: nada conferia se a versão nova quebra a anterior, e o bump era escolhido a olho."},
  { code: `dataforge abi v1/lib.df v2/lib.df        # sai com 2 se quebrou
dataforge abi a.df b.df --json           # para o CI ler
dataforge abi a.df b.df --estrito        # o indecidivel conta como quebra`, lang: 'bash' },
  {"h2": "As regras que quebram"},
  {"table": {"head": ["Regra", "Por que quebra"], "rows": [["`simbolo-removido`", "um nome que o módulo exportava deixou de existir; quem o adotava para de compilar no dia da atualização"], ["`especie-trocada`", "o nome continua e virou outra coisa (uma ação virou `record`): toda forma de uso muda junto"], ["`aridade-incompativel`", "uma chamada que era válida deixou de ser — mais argumento exigido, ou menos aceito"], ["`parametro-renomeado`", "**a chamada com nome existe aqui** (`somar(a := 1, b := 2)`), então o nome do parâmetro é contrato e não só a posição"], ["`tipo-de-parametro`", "quem passava o tipo antigo passa a ser recusado pelo `check`"], ["`retorno-trocado`", "o tipo de retorno **atravessa** a fronteira do `adopt`: quem usava o valor perde a conferência, ou é acusado"], ["`campo-removido`", "todo acesso ao campo passa a ser erro"]]}},
  {"callout": {"tipo": "nota", "titulo": "`parametro-renomeado` é a regra que uma ferramenta feita para C não precisaria ter", "texto": "Em C o argumento é posicional e o nome do parâmetro não sai do cabeçalho. Nesta linguagem a chamada com nome existe, então trocar `a` por `x` quebra `somar(a := 1, b := 2)` — e quebra **em silêncio**, porque o `check` de quem consome vai acusar um nome que a pessoa nunca escreveu errado."}},
  {"h2": "As que não quebram"},
  {"table": {"head": ["Regra", "Por que é compatível"], "rows": [["`simbolo-novo`", "ninguém depende dele ainda"], ["`parametro-opcional-novo`", "quem chamava com os antigos continua chamando igual"], ["`campo-novo-opcional`", "num blueprint, a construção antiga continua valendo"]]}},
  {"h2": "E o terceiro balde"},
  {"p": "Há um caso que a superfície **não consegue decidir**, e fingir que decide seria pior que não ter a ferramenta."},
  {"callout": {"tipo": "atencao", "titulo": "`campo-novo-em-record` — a superfície não carrega valor padrão", "texto": "Acrescentar um campo a um `record` quebra `Ponto(3, 4)` **se o campo não tiver padrão**. Se tiver, é compatível. A superfície lê a declaração sem executá-la e não sabe qual dos dois é. Acusar quebra reprovaria um release correto; calar deixaria passar um que quebra. O honesto é um **terceiro balde**, em destaque no relatório — e `--estrito` o transforma em quebra para quem prefere o alarme."}},
  { code: `  1 ponto(s) que a superficie NAO decide sozinha:
   ? Ponto  [campo-novo-em-record]
      um campo foi acrescentado a um record. Quebra SE ele nao tiver
      valor padrao — e a superficie nao carrega padroes, entao esta e
      uma decisao que so quem escreveu pode tomar
      → se o campo tem valor padrão, é compatível; se não tem, dê um
        — ou suba a versão maior`, lang: 'text' },
  {"h2": "O veredito"},
  {"table": {"head": ["Veredito", "Quando", "Saída do comando"], "rows": [["`maior`", "alguma coisa quebrou", "**2** — reprova no CI"], ["`menor`", "só acréscimos compatíveis", "0"], ["`correcao`", "a superfície não mudou", "0"], ["`desconhecido`", "um dos lados não compila", "1, com o motivo"]]}},
  {"callout": {"tipo": "nota", "titulo": "Uma superfície que não compila não julga", "texto": "`veredito` devolve `desconhecido` com o motivo, em vez de acusar quebra. Um falso alarme aqui reprova um release que está certo — e a segunda vez que isso acontece, a conferência inteira é desligada. Um analisador sem escape ensina a ignorá-lo; um que erra ensina a removê-lo."}},
  {"h2": "No CI"},
  { code: `# no seu pipeline, antes de publicar
git show HEAD~1:src/main.df > /tmp/antes.df
dataforge abi /tmp/antes.df src/main.df || exit 1`, lang: 'bash', title: `Conferir contra o commit anterior` },
  {"p": "Cada quebra vem com **o que fazer** ao lado — e quase sempre há um caminho que evita o bump: dar valor padrão ao parâmetro novo, manter o nome antigo como casca que chama o novo, aceitar os dois tipos por um ciclo."},
];

const headings = [{ id: 'as-regras-que-quebram', text: "As regras que quebram", level: 2 as const }, { id: 'as-que-nao-quebram', text: "As que não quebram", level: 2 as const }, { id: 'e-o-terceiro-balde', text: "E o terceiro balde", level: 2 as const }, { id: 'o-veredito', text: "O veredito", level: 2 as const }, { id: 'no-ci', text: "No CI", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O que quebra, e qual versão subir"}
      description={"Onze regras nomeadas, o veredito de semver que a mudança exige, e o terceiro balde para o que a superfície não decide sozinha."}
      href={"/docs/abi/compatibilidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
