// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "8. O primeiro programa completo",
  description: "Um jogo de adivinhar o número — com a lógica separada da conversa, e testada.",
};

const blocos: Bloco[] = [
  {"p": "Tudo junto: o computador sorteia um número de 1 a 100, a pessoa chuta, e ele diz *“maior”* ou *“menor”* até ela acertar. O segredo de um programa que dá para testar é separar a **regra** (comparar o chute) da **conversa** (perguntar e mostrar)."},
  { code: `// ── a regra: nao pergunta nada, so decide ──
action avaliar(segredo, chute):
    given chute is segredo:
        yield "acertou"
    given chute smaller segredo:
        yield "maior"
    yield "menor"

action ler_chute(texto):
    monitor:
        n := int(texto)
    handle Error:
        yield void
    given n smaller 1 or n bigger 100:
        yield void
    yield n

// ── o teste da regra, sem ninguem digitando ──
assert avaliar(42, 42) is "acertou"
assert avaliar(42, 10) is "maior"
assert avaliar(42, 90) is "menor"
assert ler_chute("abc") is void
assert ler_chute("500") is void
assert ler_chute("37") is 37
out "a regra do jogo confere"`, lang: 'df', title: `regras.df` },
  { code: `// ── a conversa: usa a regra ──
segredo := randint(1, 100)
tentativas := 0
resposta := ""
persist resposta isnt "acertou":
    texto := input("Seu chute (1 a 100): ")
    given texto is void:
        out ""
        out "ate a proxima!"
        halt
    chute := ler_chute(texto)
    given chute is void:
        out "digite um numero de 1 a 100"
        skip
    tentativas += 1
    resposta := avaliar(segredo, chute)
    given resposta is "acertou":
        out $"Acertou em {tentativas} tentativa(s)!"
    otherwise:
        out $"O numero e {resposta}."`, lang: 'text', title: `jogo.df (junto de regras.df)` },
  {"callout": {"tipo": "dica", "titulo": "Por que separar", "texto": "A regra se testa em milissegundos, sem ninguém digitar nada, e os três `assert` provam que ela está certa. A conversa é fina o bastante para errar pouco. É a mesma separação que um sistema grande faz entre regra de negócio e tela — ver [os tipos de projeto](/docs/projetos)."}},
  {"p": "Próximo: [9. Ler um erro](/docs/primeiros-passos/erros-comuns)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"8. O primeiro programa completo"}
      description={"Um jogo de adivinhar o número — com a lógica separada da conversa, e testada."}
      href={"/docs/primeiros-passos/primeiro-programa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
