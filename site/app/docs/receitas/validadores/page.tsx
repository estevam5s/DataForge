import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Validadores brasileiros",
  description: "Uma biblioteca publicável: CPF, e-mail e telefone, com interface pública e testes.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `156_projeto_biblioteca.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Text as Text

// ═══════════════════════════════════════════════════════════
//  VALIDADORES BR — uma biblioteca pequena e completa
//
//  Interface publica: validar_cpf, formatar_cpf, validar_cnpj,
//                     validar_email, validar_telefone
// ═══════════════════════════════════════════════════════════

// Guarda o resultado de uma validacao, com o motivo quando falha.
record Resultado:
    valido: Boolean
    motivo: String := ""

// Remove tudo que nao for digito.
action _so_digitos(texto: String) -> String:
    yield [c cycle c in texto given c.isdigit()].join("")

// Calcula um digito verificador de CPF.
action _digito_cpf(digitos: Cluster, peso_inicial: Integer) -> Integer:
    soma := 0
    peso := peso_inicial
    cycle d in digitos:
        soma += d * peso
        peso -= 1
    resto := (soma * 10) % 11
    yield 0 given resto is 10 otherwise resto

// Valida um CPF, com ou sem pontuacao.
action validar_cpf(cpf: String) -> Resultado:
    limpo := _so_digitos(cpf)
    given len(limpo) isnt 11:
        yield Resultado(no, $"esperava 11 digitos, veio {len(limpo)}")
    numeros := [cast c as Integer cycle c in limpo]
    given len(unique(numeros)) is 1:
        yield Resultado(no, "todos os digitos iguais")
    primeiro := _digito_cpf(numeros.slice(0, 9), 10)
    given primeiro isnt numeros[9]:
        yield Resultado(no, "primeiro digito verificador nao confere")
    segundo := _digito_cpf(numeros.slice(0, 10), 11)
    given segundo isnt numeros[10]:
        yield Resultado(no, "segundo digito verificador nao confere")
    yield Resultado(yes)

// Formata um CPF valido como 000.000.000-00.
action formatar_cpf(cpf: String) -> String:
    limpo := _so_digitos(cpf)
    guard len(limpo) is 11, "CPF precisa de 11 digitos"
    yield $"{limpo.slice(0, 3)}.{limpo.slice(3, 6)}.{limpo.slice(6, 9)}-{limpo.slice(9, 11)}"

// Valida um e-mail pela estrutura basica.
action validar_email(email: String) -> Resultado:
    texto := email.trim()
    given "@" not in texto:
        yield Resultado(no, "falta o @")
    partes := texto.split("@")
    given len(partes) isnt 2:
        yield Resultado(no, "mais de um @")
    given len(partes[0]) is 0:
        yield Resultado(no, "falta o usuario antes do @")
    given "." not in partes[1]:
        yield Resultado(no, "dominio sem ponto")
    yield Resultado(yes)

// Valida um telefone brasileiro (10 ou 11 digitos).
action validar_telefone(tel: String) -> Resultado:
    limpo := _so_digitos(tel)
    given len(limpo) smaller 10 or len(limpo) bigger 11:
        yield Resultado(no, $"esperava 10 ou 11 digitos, veio {len(limpo)}")
    given len(limpo) is 11 and limpo[2] isnt "9":
        yield Resultado(no, "celular deve comecar com 9 apos o DDD")
    yield Resultado(yes)

relay Resultado, validar_cpf, formatar_cpf, validar_email, validar_telefone

// ═══════════════════════════════════════════════════════════
//  DEMONSTRACAO
// ═══════════════════════════════════════════════════════════

out Text.box("Validadores BR")

out ""
out "── CPF ──"
cycle cpf in ["529.982.247-25", "52998224725", "111.111.111-11", "123", "529.982.247-26"]:
    r := validar_cpf(cpf)
    marca := "ok " given r.valido otherwise "nao"
    detalhe := formatar_cpf(cpf) given r.valido otherwise r.motivo
    out $"  {marca} {cpf.pad_end(16)} {detalhe}"

out ""
out "── e-mail ──"
cycle email in ["ana@exemplo.com", "sem-arroba", "@x.com", "a@b@c.com", "a@semponto"]:
    r := validar_email(email)
    out $"  {"ok " given r.valido otherwise "nao"} {email.pad_end(18)} {r.motivo}"

out ""
out "── telefone ──"
cycle tel in ["(48) 99999-1234", "4833334444", "(48) 8888-1234 5", "123"]:
    r := validar_telefone(tel)
    out $"  {"ok " given r.valido otherwise "nao"} {tel.pad_end(18)} {r.motivo}"

// ═══════════════════════════════════════════════════════════
//  TESTES
// ═══════════════════════════════════════════════════════════

action test_cpf_valido():
    assert validar_cpf("529.982.247-25").valido is yes, "com pontuacao"
    assert validar_cpf("52998224725").valido is yes, "sem pontuacao"

action test_cpf_invalido():
    assert validar_cpf("111.111.111-11").valido is no, "digitos repetidos"
    assert validar_cpf("529.982.247-26").valido is no, "verificador errado"
    assert validar_cpf("123").valido is no, "curto demais"

action test_cpf_explica_o_motivo():
    assert validar_cpf("123").motivo is "esperava 11 digitos, veio 3", "motivo"

action test_formatar():
    assert formatar_cpf("52998224725") is "529.982.247-25", "formatacao"

action test_email():
    assert validar_email("ana@exemplo.com").valido is yes, "valido"
    assert validar_email("sem-arroba").motivo is "falta o @", "sem arroba"
    assert validar_email("a@semponto").motivo is "dominio sem ponto", "dominio"

action test_telefone():
    assert validar_telefone("(48) 99999-1234").valido is yes, "celular"
    assert validar_telefone("4833334444").valido is yes, "fixo"
    assert validar_telefone("123").valido is no, "curto"

out ""
out Text.box("Testes")
casos := [
    ["cpf_valido", test_cpf_valido],
    ["cpf_invalido", test_cpf_invalido],
    ["cpf_explica_o_motivo", test_cpf_explica_o_motivo],
    ["formatar", test_formatar],
    ["email", test_email],
    ["telefone", test_telefone]
]
falhas := 0
cycle caso in casos:
    nome, acao := caso
    monitor:
        acao()
        out $"  ok    {nome}"
    handle e:
        falhas += 1
        out $"  FALHA {nome}: {e.message}"

out ""
out $"{len(casos) - falhas}/{len(casos)} testes passaram"
assert falhas is 0, "a biblioteca deve estar verde"`, title: `156_projeto_biblioteca.df` },
  {"h2": "A anatomia de uma biblioteca"},
  {"list": ["**Cabeçalho** — o que é e o que expõe", "**Tipos** — os dados que atravessam a interface", "**Implementação** — o interno (`_`) e o público", "**`relay`** — a fronteira"]},
  {"h2": "Devolver o motivo, não só \"no\""},
  {"p": "Esta é a decisão de desenho mais importante:"},
  { code: `validar_cpf("123")     # no
validar_cpf("123")     # Resultado(no, "esperava 11 digitos, veio 3")` },
  {"p": "A primeira obriga quem chama a adivinhar o que está errado. A segunda pode ser mostrada ao usuário direto. O custo é um record; o ganho é toda a mensagem de erro que você não escreve de novo em cada tela."},
  {"h2": "Testar os dois lados"},
  {"p": "O que deve passar, o que deve falhar — e **por quê**. Testar a mensagem pega o caso em que o validador rejeita pelo motivo errado."},
];

const headings = [{ id: 'a-anatomia-de-uma-biblioteca', text: "A anatomia de uma biblioteca", level: 2 as const }, { id: 'devolver-o-motivo-nao-so-no', text: "Devolver o motivo, não só \"no\"", level: 2 as const }, { id: 'testar-os-dois-lados', text: "Testar os dois lados", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Validadores brasileiros"}
      description={"Uma biblioteca publicável: CPF, e-mail e telefone, com interface pública e testes."}
      href={"/docs/receitas/validadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
