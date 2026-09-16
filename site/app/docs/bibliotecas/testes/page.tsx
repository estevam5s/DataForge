// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes de biblioteca",
  description: "Testar pelo nome público, e por que o caminho relativo esconde exatamente o bug que importa.",
};

const blocos: Bloco[] = [
  {"p": "O teste de uma biblioteca tem um trabalho a mais que o de um programa: **ele é o primeiro usuário**. Se ele chega ao código por um caminho que nenhum usuário usaria, ele deixa de testar a única coisa que só ele pode testar — a fronteira."},
  {"h2": "Importe pelo nome, não pelo caminho"},
  { code: `adopt ../src/main as V        // NÃO: nenhum usuário escreve isto
adopt minha-lib as V          // SIM: é assim que ela será usada
`, lang: 'df' },
  {"p": "A segunda forma exercita a resolução de verdade: o `entry` do manifesto, o `relay`, o nome do pacote. A primeira pula tudo isso e testa arquivos soltos."},
  {"callout": {"tipo": "atencao", "titulo": "Isto já quebrou aqui", "texto": "As suítes dos **vinte** pacotes deste repositório falhavam porque um pacote não sabia se importar pelo próprio nome — e a CI não apanhava, porque ela não rodava `dataforge test` dentro de `packages/`. O teste que passa pelo caminho relativo teria continuado verde."}},
  {"h2": "A forma de um teste"},
  { code: `adopt Arcane.Crucible as C

action cpf(texto):
    yield len(texto) is 11

crucible "cpf":
    trial "aceita um CPF com 11 digitos":
        expect cpf("52998224725") is yes

    trial "recusa o numero de digitos errado":
        expect cpf("123") is no

C.run()
`, lang: 'df', title: `tests/cpf_test.df` },
  { code: `dataforge test tests/
`, lang: 'bash' },
  {"h2": "Teste o contrato, e não a implementação"},
  {"table": {"head": ["Teste isto", "Não isto"], "rows": [["o que uma ação pública devolve", "o valor de uma variável interna"], ["o **tipo** do erro levantado", "o texto exato da mensagem"], ["que o campo `valido` existe", "a ordem dos campos do record"], ["o comportamento na borda (vazio, zero, negativo)", "o caminho que o código toma por dentro"]]}},
  {"p": "A regra prática: um teste que quebra quando você **melhora** a implementação sem mudar o comportamento é um teste que está no lugar errado."},
  {"h2": "As bordas que uma biblioteca precisa cobrir"},
  {"list": ["**Vazio** — texto vazio, cluster `[]`, vault `{}`. É o que mais chega de formulário.", "**Void** — quem usa vai passar `void` um dia, e a mensagem precisa dizer o que fazer.", "**O tipo errado** — um número onde se espera texto. Com anotação de tipo, o `check` pega antes; sem ela, o teste é a única defesa.", "**O limite** — o maior valor aceito, e o primeiro recusado.", "**A repetição** — chamar duas vezes devolve o mesmo? Se não, há estado escondido."]},
  {"h2": "Cobertura, e o número que mente"},
  { code: `dataforge test tests/ --cobertura --minimo=80
`, lang: 'bash' },
  {"p": "Uma ação **nunca chamada** aparece com 0%, e não com 20% — a linha da declaração não conta, o corpo conta. E um arquivo que nenhum teste toca aparece no relatório com 0% em vez de sumir dele: sumir é o que faz uma cobertura de 95% conviver com metade do sistema sem teste."},
  {"p": "`forge_modules/` fica de fora da descoberta. Sem isso, um projeto com 13 testes relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca que ninguém escreveu."},
  {"h2": "Instantâneo, para saída grande"},
  {"p": "Quando o que se testa é um texto longo — um relatório, um HTML, um CSV —, comparar à mão é inviável. O instantâneo grava na primeira vez e compara nas seguintes; `DF_ATUALIZAR_SNAPSHOT=1` aceita a mudança."},
  {"p": "Atualizar por padrão seria pior que não ter instantâneo: o teste passaria a concordar com qualquer mudança, inclusive a errada."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/crucible", "title": "Crucible", "desc": "o corredor de testes inteiro"}, {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "os dois jeitos de o número mentir"}, {"href": "/docs/bibliotecas/versao", "title": "Versão", "desc": "o próximo passo"}]},
];

const headings = [{ id: 'importe-pelo-nome-nao-pelo-caminho', text: "Importe pelo nome, não pelo caminho", level: 2 as const }, { id: 'a-forma-de-um-teste', text: "A forma de um teste", level: 2 as const }, { id: 'teste-o-contrato-e-nao-a-implementacao', text: "Teste o contrato, e não a implementação", level: 2 as const }, { id: 'as-bordas-que-uma-biblioteca-precisa-cobrir', text: "As bordas que uma biblioteca precisa cobrir", level: 2 as const }, { id: 'cobertura-e-o-numero-que-mente', text: "Cobertura, e o número que mente", level: 2 as const }, { id: 'instantaneo-para-saida-grande', text: "Instantâneo, para saída grande", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes de biblioteca"}
      description={"Testar pelo nome público, e por que o caminho relativo esconde exatamente o bug que importa."}
      href={"/docs/bibliotecas/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
