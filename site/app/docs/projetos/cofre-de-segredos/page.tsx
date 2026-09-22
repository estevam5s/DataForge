// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cofre de segredos",
  description: "Cifrar por envelope, rotacionar a chave sem reescrever os dados, e recusar o dado adulterado.",
};

const blocos: Bloco[] = [
  {"p": "Uma chave que nunca é trocada é uma chave que um dia vaza e continua valendo. O motivo de ninguém trocar é sempre o mesmo: trocá-la tornaria ilegível tudo que ela cifrou. O envelope resolve — os dados são cifrados por uma chave própria, e só essa chave pequena é cifrada pela mestra."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`Ch.cofre`", "as chaves com propósito e prazo"], ["`envelopar` / `desenvelopar`", "DEK por dado, KEK mestra"], ["`rotacionar`", "a chave nova, mantendo as antigas"], ["`recifrar`", "trocar a mestra sem tocar nos dados"]]}},
  {"h2": "Estrutura"},
  { code: `cofre/
  src/
    cofre.df       abrir, guardar, ler
    rotacao.df     o job mensal
  tests/`, lang: 'text' },
  { code: `[project]
name = "cofre"
version = "0.1.0"
description = "Cofre de segredos"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Chaves as Ch
adopt Arcane.Bytes as Bytes

cofre := Ch.cofre()
cofre.gerar("mestra", proposito := "cifrar")

segredos := {}
action guardar(nome, valor):
    segredos[nome] := cofre.envelopar(valor, "mestra")

// O envelope guarda BYTES: um segredo pode ser um certificado binario.
// Quem sabe que ali mora texto converte na saida.
action ler(nome):
    yield Bytes.para_texto(cofre.desenvelopar(segredos[nome]))

guardar("banco", "postgres://app:s3nh4@db/loja")
guardar("stripe", "chave-de-teste-ficticia")

// A rotacao: a chave nova passa a cifrar, a antiga continua abrindo.
nova := cofre.rotacionar("mestra", "cifrar")
assert ler("banco") is "postgres://app:s3nh4@db/loja"

// E o job de rotacao recifra so as DEKs — os dados ficam onde estao.
cycle nome in segredos.keys():
    segredos[nome] := cofre.recifrar(segredos[nome], "mestra")
assert segredos["banco"]["kid"] is nova.kid
out "rotacionado; o passado continua legivel"`, lang: 'df', title: `src/cofre.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/cofre as C

crucible "cofre":
    trial "o que se guarda volta igual":
        C.guardar("x", "valor")
        expect C.ler("x") is "valor"`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["envelope (DEK/KEK)", "trocar a mestra é reescrever cada segredo"], ["o `kid` dentro do envelope", "com cinco chaves, não se sabe qual abre o quê"], ["a chave tem **propósito**", "a chave que assina token também decifra backup"], ["a integridade é barulhenta", "o dado adulterado abre como `void` e o programa grava nada onde havia um valor"]]}},
  {"h2": "Para ir além"},
  {"list": ["O ciclo de vida inteiro: [Criptografia e chaves](/docs/seguranca/criptografia).", "Onde a mestra mora em produção: fora do processo — KMS ou variável de ambiente.", "A referência: [Arcane.Chaves](/docs/biblioteca/chaves)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cofre de segredos"}
      description={"Cifrar por envelope, rotacionar a chave sem reescrever os dados, e recusar o dado adulterado."}
      href={"/docs/projetos/cofre-de-segredos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
