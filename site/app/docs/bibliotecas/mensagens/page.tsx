// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Mensagens para quem não leu o código",
  description: "O erro de uma biblioteca é lido por quem a usa — o que ele precisa dizer, e o que nunca dizer.",
};

const blocos: Bloco[] = [
  {"p": "A mensagem de erro da sua biblioteca aparece no terminal de alguém que nunca abriu o seu código. Ela precisa dizer **o que aconteceu**, **com qual valor**, e **o que fazer** — nessa ordem."},
  { code: `action validar_cep(cep):
    digitos := "".join([c cycle c in str(cep) given c.isdigit()])
    given len(digitos) isnt 8:
        trigger $"CEP '{cep}' tem {len(digitos)} digitos, e um CEP tem 8. Confira se nao faltou um zero a esquerda."
    yield digitos

monitor:
    validar_cep(1310100)
    assert no
handle Error as e:
    out e.message
    assert "tem 7 digitos" in e.message`, lang: 'df' },
  {"table": {"head": ["Ruim", "Bom"], "rows": [["`CEP inválido`", "`CEP '1310100' tem 7 dígitos, e um CEP tem 8. Confira se não faltou um zero à esquerda.`"], ["`KeyError: 'nome'`", "`o cliente não tem 'nome'. Campos recebidos: email, idade.`"], ["`erro ao conectar`", "`não conectei em db:5432 em 30 s — o banco está no ar?`"]]}},
  {"h2": "O que nunca vai numa mensagem"},
  {"table": {"head": ["Nunca", "Porque"], "rows": [["a senha, o token, a chave", "a mensagem vai para o log, e o log é lido por muita gente"], ["o CPF inteiro, o cartão", "`Seguranca.mascarar_pii` antes"], ["o traceback do Python", "fala de arquivos que quem usa nunca viu"], ["o nome de um tipo do Python (`list`, `dict`)", "a linguagem os chama de `Cluster` e `Vault`"]]}},
];

const headings = [{ id: 'o-que-nunca-vai-numa-mensagem', text: "O que nunca vai numa mensagem", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Mensagens para quem não leu o código"}
      description={"O erro de uma biblioteca é lido por quem a usa — o que ele precisa dizer, e o que nunca dizer."}
      href={"/docs/bibliotecas/mensagens"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
