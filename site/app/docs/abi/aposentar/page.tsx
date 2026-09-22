// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Aposentar sem quebrar",
  description: "Renomear com relay … as, avisar com Evolucao.obsoleta, e só então remover — em duas versões, e não em uma.",
};

const blocos: Bloco[] = [
  {"p": "Um nome ruim numa biblioteca publicada não se troca de uma vez: quem o usa quebra no dia da atualização. O caminho tem três passos, e cada um é uma versão."},
  {"table": {"head": ["Versão", "Faz", "Quem usa o nome velho"], "rows": [["1.5 (menor)", "exporta o novo, e o velho como apelido: `relay somar, somar as soma`", "continua funcionando"], ["1.6 (menor)", "marca o velho com `Evolucao.obsoleta`", "funciona, com aviso na saída de erro"], ["2.0 (maior)", "remove o velho", "quebra — mas foi avisado por duas versões"]]}},
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

// o renomeio com apelido: o nome velho continua exportado
com_apelido := $"{pasta}/v15.df"
IO.write(com_apelido, "action somar(a, b):\\n    yield a + b\\naction duplicar(x):\\n    yield x * 2\\nrelay somar, duplicar, duplicar as dobro\\n")
assert Abi.veredito(antes, com_apelido) is "menor"        // nada quebrou

sem_apelido := $"{pasta}/v2.df"
IO.write(sem_apelido, "action somar(a, b):\\n    yield a + b\\naction duplicar(x):\\n    yield x * 2\\nrelay somar, duplicar\\n")
assert Abi.veredito(antes, sem_apelido) is "maior"        // o 'dobro' sumiu
IO.remove_tree(pasta)`, lang: 'df' },
  {"p": "O aviso da versão intermediária vem de [`Arcane.Evolucao`](/docs/bibliotecas/obsolescencia): `obsoleta(motivo, desde, use)` avisa **uma vez** por ação, na saída de erro, e `DF_OBSOLETOS=erro` transforma o aviso em falha — para o CI de quem depende descobrir antes do 2.0."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Aposentar sem quebrar"}
      description={"Renomear com relay … as, avisar com Evolucao.obsoleta, e só então remover — em duas versões, e não em uma."}
      href={"/docs/abi/aposentar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
