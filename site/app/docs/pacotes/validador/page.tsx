import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "validador",
  description: "Validação de dados com mensagens em português, e um esquema para formulários inteiros.",
};

const blocos: Bloco[] = [
  { code: `dataforge add validador`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"]]}},
  {"h2": "Por que existe"},
  {"p": "Validar CPF conferindo só o tamanho aceita `111.111.111-11`. Este pacote roda os dígitos verificadores de verdade — e devolve todos os erros de um formulário de uma vez, não o primeiro."},
  {"h2": "Exemplo"},
  { code: `adopt validador as V

// direto
out V.email("ana@exemplo.com")      // yes
out V.cpf("529.982.247-25")         // yes
out V.cpf("111.111.111-11")         // no — repetido não vale
out V.cartao("4539 1488 0343 6467") // yes (Luhn)

// um formulário inteiro
regras := V.esquema({
    "email": [V.regra_obrigatorio(), V.regra_email()],
    "cpf": [V.regra_cpf()],
    "idade": [V.regra_entre(18, 120)]
})

r := V.validar(regras, {"email": "invalido", "cpf": "111", "idade": 5})
out r["valido"]     // no
out r["erros"]      // {email: e-mail inválido, cpf: CPF inválido, ...}`, lang: 'df' },
  {"h2": "API"},
  {"table": {"head": ["Função", "O que faz"], "rows": [["`email(v)`", "formato de e-mail"], ["`cpf(v)`", "CPF com dígitos verificadores"], ["`cnpj(v)`", "CNPJ com dígitos verificadores"], ["`cep(v)`", "CEP brasileiro"], ["`telefone(v)`", "fixo ou celular, com o nono dígito"], ["`cartao(v)`", "número de cartão, por Luhn"], ["`forca_senha(v)`", "nota de 0 a 5 e o que falta"], ["`url(v)`", "URL http/https"], ["`nao_vazio(v)`", "texto, lista ou vault com conteúdo"], ["`entre(v, min, max)`", "faixa numérica"], ["`esquema(campos)`", "monta o conjunto de regras"], ["`validar(esquema, dados)`", "roda tudo, devolve `{valido, erros}`"], ["`regra(nome, msg, fn)`", "sua própria regra"]]}},
  {"h2": "Instalar"},
  { code: `dataforge add validador
dataforge add validador@1.0.0
dataforge add validador@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'exemplo', text: "Exemplo", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"validador"}
      description={"Validação de dados com mensagens em português, e um esquema para formulários inteiros."}
      href={"/docs/pacotes/validador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
