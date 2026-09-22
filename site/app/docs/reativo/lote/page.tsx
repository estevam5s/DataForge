// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escrever em lote",
  description: "Três escritas, uma notificação: o estado intermediário que ninguém deveria ver.",
};

const blocos: Bloco[] = [
  {"p": "Trocar nome e sobrenome são duas escritas. Entre elas, o nome completo vale \"Bia Souza\" com o sobrenome velho — um valor que nunca foi verdade. Um efeito que roda entre as duas escritas mostra esse valor na tela, ou pior, grava."},
  { code: `adopt Arcane.Reativo as R

nome := R.sinal("Ana")
sobrenome := R.sinal("Souza")
completo := R.derivado(lambda => $"{nome.ler()} {sobrenome.ler()}")
vistos := []
R.efeito(lambda => vistos.append(completo.ler()))

action trocar():
    nome.escrever("Bia")
    sobrenome.escrever("Lima")

R.lote(trocar)
assert vistos is ["Ana Souza", "Bia Lima"]     // "Bia Souza" nunca apareceu`, lang: 'df' },
  {"p": "Sem o lote, `vistos` teria três valores, e o do meio seria \"Bia Souza\". Dentro dele, os avisos são adiados até o fim, e cada efeito roda **uma vez**, vendo o estado final."},
  {"list": ["**Todo comando que muda mais de um sinal é um lote.** Carregar um formulário do servidor, aplicar um filtro com três campos, desfazer uma colagem.", "**O [histórico](/docs/reativo/historico) anota um lote como um passo** — é o mesmo mecanismo.", "**Uma escrita dentro de um efeito abre a próxima onda**, e não entra na atual: a fila não cresce enquanto é percorrida."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Escrever em lote"}
      description={"Três escritas, uma notificação: o estado intermediário que ninguém deveria ver."}
      href={"/docs/reativo/lote"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
