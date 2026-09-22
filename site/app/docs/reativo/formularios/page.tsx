// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um formulário reativo",
  description: "Cada campo um sinal, cada erro um derivado, e o botão que só habilita quando tudo está certo.",
};

const blocos: Bloco[] = [
  {"p": "Um formulário é o caso de uso que o modelo reativo resolve melhor: a regra de cada campo é uma **fórmula** sobre o valor dele, e \"pode enviar?\" é uma fórmula sobre os erros. Nada é recalculado à mão, e nenhum campo esquece de revalidar."},
  { code: `adopt Arcane.Reativo as R

email := R.sinal("")
senha := R.sinal("")
confirma := R.sinal("")

erro_email := R.derivado(lambda => (void given email.ler().contains("@") otherwise "e-mail inválido"))
erro_senha := R.derivado(lambda => (void given len(senha.ler()) bigger_eq 8 otherwise "mínimo 8 caracteres"))
erro_confirma := R.derivado(lambda => (void given confirma.ler() is senha.ler() otherwise "as senhas diferem"))
pode_enviar := R.derivado(lambda => [erro_email.ler(), erro_senha.ler(), erro_confirma.ler()] is [void, void, void])

assert not pode_enviar.ler()
email.escrever("ana@exemplo.br")
senha.escrever("segredo-longo")
assert erro_confirma.ler() is "as senhas diferem"
confirma.escrever("segredo-longo")
assert pode_enviar.ler()

senha.escrever("curta")                   // mudar a senha revalida a confirmação
assert erro_confirma.ler() is "as senhas diferem" and not pode_enviar.ler()`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O ternário num lambda vai entre parênteses", "texto": "O corpo de um `lambda` liga mais forte que `given … otherwise`: sem os parênteses, `lambda => void given c otherwise \"erro\"` vira um ternário **sobre o lambda**, e o derivado recebe um texto no lugar da ação. O mesmo vale para `>>`. A mensagem de erro mostra a forma certa."}},
  {"callout": {"tipo": "dica", "titulo": "A confirmação depende das duas", "texto": "`erro_confirma` lê `senha` e `confirma`, e as dependências são **descobertas** na execução. Trocar a senha depois de confirmar revalida a confirmação sozinho — é o caso que um formulário imperativo esquece, e o botão fica habilitado com senhas diferentes."}},
  {"p": "Na Vitrine, o mesmo raciocínio vale campo a campo: ver [Estado e cache](/docs/vitrine/estado)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Um formulário reativo"}
      description={"Cada campo um sinal, cada erro um derivado, e o botão que só habilita quando tudo está certo."}
      href={"/docs/reativo/formularios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
