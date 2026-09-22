// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pseudonimizar, anonimizar, medir",
  description: "Por que um hash de CPF não protege, o que é k-anonimato, e a contagem com privacidade diferencial.",
};

const blocos: Bloco[] = [
  {"p": "Três técnicas que o código costuma confundir, e a lei não: **pseudonimizar** troca o identificador por um apelido que só volta com uma chave (o dado continua pessoal); **anonimizar** remove a possibilidade de reidentificar (o dado deixa de ser pessoal — art. 12); e **publicar agregados** com ruído protege quem está nos números."},
  {"h2": "O hash sem chave não protege"},
  { code: `adopt Arcane.Privacidade as P
adopt Arcane.Crypto as Crypto

cpf := "529.982.247-25"

// ERRADO: sha256 do CPF. Sao so 10^9 CPFs — um laptop calcula todos numa tarde.
fraco := Crypto.sha256(cpf)

// CERTO: HMAC com uma chave que mora FORA da base, por finalidade.
chave := "vem-do-ambiente-e-nao-da-base-x"
vendas := P.pseudonimizar(cpf, chave, "vendas")
rh := P.pseudonimizar(cpf, chave, "rh")
assert vendas is P.pseudonimizar(cpf, chave, "vendas")   // estavel: as juncoes funcionam
assert vendas isnt rh                                     // cruzar os dois exige a chave
out vendas`, lang: 'df' },
  {"h2": "Tirar o nome não anonimiza"},
  { code: `adopt Arcane.Privacidade as P

atendimentos := [
    {"cep": "01310-100", "idade": 34, "diagnostico": "A"},
    {"cep": "01310-200", "idade": 36, "diagnostico": "B"},
    {"cep": "04567-000", "idade": 52, "diagnostico": "C"},
    {"cep": "04567-111", "idade": 58, "diagnostico": "B"}
]

antes := P.k_anonimato(atendimentos, ["cep", "idade"])
out $"k = {antes['k']}: alguem esta sozinho numa combinacao"
assert antes["k"] is 1

generalizado := atendimentos >> morph a: {
    "cep": P.generalizar(a["cep"], "cep", 2),
    "idade": P.generalizar(a["idade"], "idade", 2),
    "diagnostico": a["diagnostico"]}
depois := P.k_anonimato(generalizado, ["cep", "idade"])
assert depois["k"] is 2
out $"depois de generalizar: k = {depois['k']}"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "k-anonimato não basta sozinho", "texto": "Se os dois do mesmo grupo têm o **mesmo** diagnóstico, saber o grupo revela o diagnóstico (ataque de homogeneidade). k-anonimato mede a primeira porta; a diversidade do atributo sensível dentro de cada grupo é a segunda — confira as duas antes de publicar."}},
  {"h2": "Publicar uma contagem"},
  { code: `adopt Arcane.Privacidade as P

// "3 casos no bairro" identifica os tres. Com ruido de Laplace, a presenca
// ou ausencia de UMA pessoa muda pouco o numero publicado.
publicado := P.contagem_privada(3, 0.5)
assert publicado bigger_eq 0
out $"publicado: {publicado} (o valor real nao sai)"`, lang: 'df' },
  {"table": {"head": ["ε (epsilon)", "Protege", "Erra"], "rows": [["0,1", "muito", "muito"], ["1", "bem", "pouco"], ["5", "pouco", "quase nada"]]}},
  {"p": "Cada publicação **gasta** privacidade: publicar a mesma contagem cem vezes com ruído novo deixa a média revelar o valor. Publique uma vez, e guarde o número publicado."},
];

const headings = [{ id: 'o-hash-sem-chave-nao-protege', text: "O hash sem chave não protege", level: 2 as const }, { id: 'tirar-o-nome-nao-anonimiza', text: "Tirar o nome não anonimiza", level: 2 as const }, { id: 'publicar-uma-contagem', text: "Publicar uma contagem", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pseudonimizar, anonimizar, medir"}
      description={"Por que um hash de CPF não protege, o que é k-anonimato, e a contagem com privacidade diferencial."}
      href={"/docs/seguranca/anonimizacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
