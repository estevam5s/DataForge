// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Condição de corrida",
  description: "Ler, somar e escrever não é uma operação — e duas threads fazendo isso perdem metade das somas, caladas.",
};

const blocos: Bloco[] = [
  {"p": "`v[\"n\"] := v[\"n\"] + 1` parece uma operação e são três: **ler**, somar, **escrever**. Entre o ler e o escrever de uma thread, outra thread lê o mesmo valor velho — e as duas escrevem o mesmo resultado. Uma soma some, sem erro nenhum."},
  {"table": {"head": ["Operação, 4 threads", "Esperado", "Medido"], "rows": [["`v[\"n\"] := v[\"n\"] + 1` sem trava", "40.000", "**33.740**"], ["`xs.append(i)` sem trava", "20.000", "20.000 — o GIL protege a operação inteira"], ["com `P.mutex` ou `P.ator`", "20.000", "20.000"]]}},
  {"p": "O `append` sozinho não perde porque é **uma** operação do interpretador, protegida pelo GIL. O que perde é o que **lê para decidir o que escrever**: `+= 1`, `pop`, `remove`, `insert`, `sort`. É essa a lista que o `check` usa."},
  {"h2": "O check avisa"},
  { code: `adopt Arcane.Process as Proc
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-corrida-{randint(100000, 999999)}"
IO.mkdir(pasta)
arquivo := $"{pasta}/corrida.df"
IO.write(arquivo, "total := {\\"n\\": 0}\\nparallel:\\n    total[\\"n\\"] := total[\\"n\\"] + 1\\n    total[\\"n\\"] := total[\\"n\\"] + 1\\n")

// o 'check' do mesmo Python que roda este programa — e não um do PATH
r := Proc.run([OS.executable(), "-m", "dataforge", "check", arquivo])
saida := r["stdout"] + r["stderr"]
assert saida.contains("corrida.df:3") and saida.contains("'total'")   // o aviso, na linha certa
IO.remove_tree(pasta)`, lang: 'df' },
  {"p": "`dataforge check` num arquivo assim avisa `escrita-concorrente`: um `thread`, `parallel` ou **`route`** escrevendo num nome que vem de fora. A rota é o caso que mais importa, porque o Kiln atende cada pedido numa thread, e ali a concorrência é **invisível** — quem escreve a rota não vê thread nenhuma. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram 1 de 6."},
  {"callout": {"tipo": "dica", "titulo": "É aviso, e não erro", "texto": "Um acumulador protegido por mutex passa pelo aviso igual — a análise não segue a chamada até o `com_trava`. Recusar proibiria o uso correto; avisar deixa quem escreveu decidir, com `// df: permitir escrita-concorrente` quando a proteção existe."}},
];

const headings = [{ id: 'o-check-avisa', text: "O check avisa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Condição de corrida"}
      description={"Ler, somar e escrever não é uma operação — e duas threads fazendo isso perdem metade das somas, caladas."}
      href={"/docs/concorrencia/corridas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
