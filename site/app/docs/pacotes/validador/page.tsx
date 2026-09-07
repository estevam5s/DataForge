import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "validador",
  description: "Validação de dados: e-mail, CPF, CNPJ, CEP, telefone, cartão e senha, com regras encadeáveis.",
};

const blocos: Bloco[] = [
  { code: `dataforge add validador`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "26 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Validar CPF conferindo só o tamanho aceita `111.111.111-11`. Aqui os dígitos verificadores rodam de verdade — e o esquema devolve todos os erros de um formulário de uma vez, não o primeiro."},
  {"h2": "Uso"},
  { code: `adopt validador as V
out V.cpf("529.982.247-25")        // yes


regras := V.esquema({
    "email": [V.regra_obrigatorio(), V.regra_email()],
    "idade": [V.regra_entre(18, 120)]
})
resultado := V.validar(regras, dados)
out resultado.valido, resultado.erros`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 26 símbolos:"},
  { code: `email(valor)
cpf(valor)
cnpj(valor)
cep(valor)
telefone(valor)
cartao(valor)
forca_senha(senha)
nao_vazio(valor)
entre(valor, minimo, maximo)
tamanho_entre(texto, minimo, maximo)
url(valor)
so_digitos(texto)
record Regra
regra(nome, mensagem, verificar)
regra_obrigatorio(mensagem := "campo obrigatório")
regra_email(mensagem := "e-mail inválido")
regra_cpf(mensagem := "CPF inválido")
regra_cnpj(mensagem := "CNPJ inválido")
regra_cep(mensagem := "CEP inválido")
regra_telefone(mensagem := "telefone inválido")
regra_url(mensagem := "URL inválida")
regra_entre(minimo, maximo, mensagem := void)
regra_tamanho(minimo, maximo, mensagem := void)
regra_senha_forte(mensagem := "senha fraca")
esquema(campos)
validar(esquema, dados)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add validador
dataforge add validador@1.0.0
dataforge add validador@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"validador"}
      description={"Validação de dados: e-mail, CPF, CNPJ, CEP, telefone, cartão e senha, com regras encadeáveis."}
      href={"/docs/pacotes/validador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
