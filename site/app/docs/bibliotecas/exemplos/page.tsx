// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Quatro bibliotecas de verdade",
  description: "Os pacotes deste repositório, e a decisão de desenho que cada um demonstra.",
};

const blocos: Bloco[] = [
  {"p": "`packages/` tem quatro bibliotecas escritas em DataForge, publicadas no registro do site e somando 46 testes. Elas servem de referência — e de prova de que o gerenciador funciona ponta a ponta."},
  {"table": {"head": ["Pacote", "O quê", "A decisão que ele demonstra"], "rows": [["`validador`", "CPF, CNPJ, e-mail e esquema de formulário", "a validação devolve **o motivo**, e não `no`"], ["`tabela`", "saída para terminal", "medir a largura do que é impresso, e não do que é guardado"], ["`datas`", "datas em pt-BR, com feriados", "o que a biblioteca **não** faz: fuso horário"], ["`cofre`", "configuração em camadas", "a ordem das fontes é o recurso"]]}},
  {"h2": "O validador: o motivo, e não o booleano"},
  { code: `action validar_cpf(texto):
    digitos := "".join([c cycle c in texto given c.isdigit()])
    given len(digitos) is 0:
        yield {"ok": no, "motivo": "vazio"}
    given len(digitos) is not 11:
        yield {"ok": no, "motivo": $"tem {len(digitos)} digitos, e nao 11"}
    given digitos is digitos[0] * 11:
        yield {"ok": no, "motivo": "todos os digitos iguais"}
    yield {"ok": yes, "motivo": ""}

assert validar_cpf("529.982.247-25")["ok"]
out validar_cpf("111.111.111-11")["motivo"]
out validar_cpf("123")["motivo"]`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Um validador que devolve `no` obriga o chamador a adivinhar", "texto": "E o que ele adivinha vai para a tela do usuário final: *“CPF inválido”* é a mensagem mais inútil de um formulário. Devolver o motivo custa um vault e resolve o problema onde ele aparece."}},
  {"h2": "O cofre: a ordem é o recurso"},
  { code: `// A ordem e sempre a mesma, e e ela que faz um segredo de producao
// vencer o padrao do arquivo sem ninguem editar nada:
//
//   padrao  <  arquivo  <  ambiente  <  argumento de linha

action resolver(padrao, arquivo, ambiente, argumento):
    valor := padrao
    cycle fonte in [arquivo, ambiente, argumento]:
        given fonte is not void:
            valor := fonte
    yield valor

assert resolver(5432, 5433, void, void) is 5433
assert resolver(5432, 5433, 6000, void) is 6000
assert resolver(5432, 5433, 6000, 7000) is 7000`, lang: 'df' },
  { code: `cd packages/validador
dataforge test .
dataforge pack
dataforge publish --registry=../../site/public/registry`, lang: 'bash' },
  {"p": "Continue em [Estrutura](/docs/bibliotecas/estrutura) e [Publicar](/docs/bibliotecas/publicar)."},
];

const headings = [{ id: 'o-validador-o-motivo-e-nao-o-booleano', text: "O validador: o motivo, e não o booleano", level: 2 as const }, { id: 'o-cofre-a-ordem-e-o-recurso', text: "O cofre: a ordem é o recurso", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Quatro bibliotecas de verdade"}
      description={"Os pacotes deste repositório, e a decisão de desenho que cada um demonstra."}
      href={"/docs/bibliotecas/exemplos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
