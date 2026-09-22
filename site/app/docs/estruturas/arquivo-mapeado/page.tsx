// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arquivo mapeado em memória",
  description: "Um arquivo de gigabytes como um bloco, sem lê-lo inteiro: o sistema traz só as páginas tocadas.",
};

const blocos: Bloco[] = [
  {"p": "`IO.read_bytes` lê o arquivo **inteiro** para a memória. Para um arquivo de 4 GB cujo cabeçalho de 64 bytes você quer ler, isso são 4 GB de leitura. `Est.mapear` entrega o arquivo como um `Bloco`, e o sistema operacional traz para a memória só as páginas que forem tocadas."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-mapa-{randint(100000, 999999)}"
IO.mkdir(pasta)
caminho := $"{pasta}/contadores.bin"

Contador := Est.definir("Contador", [["id", "u32"], ["visitas", "u64"]], "rede", yes)
IO.write_bytes(caminho, Est.bloco(Contador.tamanho * 3).bytes())   // três registros zerados

mapa := Est.mapear(caminho, yes)                   // yes: para escrever
registros := Est.janelas(mapa, Contador)
registros[1]["id"] := 7
registros[1]["visitas"] := registros[1]["visitas"] + 1
mapa.sincronizar()                                 // garante que chegou ao disco
mapa.liberar()

de_novo := Est.janelas(IO.read_bytes(caminho), Contador)
assert de_novo[1]["id"] is 7 and de_novo[1]["visitas"] is 1
IO.remove_tree(pasta)`, lang: 'df' },
  {"table": {"head": ["Use", "Quando"], "rows": [["`IO.read_bytes`", "arquivo pequeno, lido inteiro de qualquer jeito"], ["`Est.mapear(c)`", "arquivo grande, e você lê pedaços — um índice, um cabeçalho"], ["`Est.mapear(c, yes)`", "atualizar registros no lugar, sem reescrever o arquivo"]]}},
  {"list": ["**Só leitura por padrão.** Escrever num mapa aberto sem `yes` é recusado com a dica — e não um `TypeError` do sistema.", "**O arquivo não pode estar vazio**: o mapa de zero bytes não existe. Crie-o no tamanho que o formato exige antes.", "**`sincronizar()` antes de confiar.** Sem ele, o que foi escrito pode ainda estar só na memória quando outro processo lê o arquivo.", "**`liberar()` fecha o mapa.** Toda janela sobre ele passa a recusar leitura — em vez de ler memória que já não é do arquivo."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Arquivo mapeado em memória"}
      description={"Um arquivo de gigabytes como um bloco, sem lê-lo inteiro: o sistema traz só as páginas tocadas."}
      href={"/docs/estruturas/arquivo-mapeado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
