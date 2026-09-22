// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dividir um arquivo grande",
  description: "Quando partir, por onde partir, e como fazer isso sem quebrar quem já adota o arquivo.",
};

const blocos: Bloco[] = [
  {"p": "Um arquivo com mil linhas ainda funciona; o problema é que ninguém mais acha nada nele, e toda mudança conflita com outra. Partir é mecânico **se** for feito na ordem certa."},
  {"h2": "Quando"},
  {"table": {"head": ["Sinal", "Medido por"], "rows": [["o arquivo passou de 400 linhas", "`dataforge stats`"], ["dois assuntos que não se chamam", "`dataforge deps`"], ["um blueprint com baixa coesão", "`dataforge oop` (LCOM alto)"]]}},
  {"h2": "Como, sem quebrar ninguém"},
  {"list": ["Crie os arquivos novos e **mova** o código para eles.", "No arquivo original, troque o conteúdo por uma fachada: `relay from ./parte1`, `relay from ./parte2`.", "Rode `dataforge abi antigo.df novo.df`: o veredito precisa ser `correcao` — a superfície não mudou.", "Só depois, se quiser, migre quem adota o arquivo original para os novos."], "ordered": true},
  { code: `dataforge stats src/loja.df
dataforge abi git-show-antigo/loja.df src/loja.df   # precisa dar 'correcao'
dataforge check src/                                 # nenhum ciclo novo`, lang: 'bash' },
  { code: `// O que o 'abi' confere, em miniatura: a mesma superficie antes e depois.
action total(v):
    yield v * 1.1
action frete(uf):
    yield 20 given uf is "SP" otherwise 35
assert total(100) bigger 109 and frete("SP") is 20`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Parta por assunto, não por tipo", "texto": "`pedidos/`, `clientes/`, `estoque/` — e não `modelos/`, `servicos/`, `rotas/`. Uma mudança de regra deveria tocar uma pasta. Ver [Organizar um projeto grande](/docs/modulos/organizar)."}},
];

const headings = [{ id: 'quando', text: "Quando", level: 2 as const }, { id: 'como-sem-quebrar-ninguem', text: "Como, sem quebrar ninguém", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Dividir um arquivo grande"}
      description={"Quando partir, por onde partir, e como fazer isso sem quebrar quem já adota o arquivo."}
      href={"/docs/modulos/dividir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
