// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_api.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes",
  description: "Tudo sobre testar em DataForge: o corredor, os matchers, dublês, propriedades, cobertura e CI.",
};

const blocos: Bloco[] = [
  {"p": "Testar não é uma biblioteca que se instala: `crucible`, `trial` e `expect` são **palavras da linguagem**, e `dataforge test` já está no executável. Não há dependência, não há configuração, e o arquivo de teste é um `.df` comum."},
  { code: `adopt Arcane.Crucible as C

action somar(a, b):
    yield a + b

crucible "soma":
    trial "soma dois numeros":
        expect somar(2, 3) is 5

    trial "aceita decimais":
        expect somar(0.5, 0.25) is 0.75

C.run()
`, lang: 'df', title: `tests/soma_test.df` },
  { code: `$ dataforge test tests/

✓ tests/soma_test.df (2/2)

2 passaram em 1 arquivo(s) — 0.03s
Tudo verde.
`, lang: 'bash' },
  {"h2": "O caminho inteiro"},
  {"cards": [{"href": "/docs/crucible", "title": "Crucible", "desc": "o corredor: crucible, trial, expect e como ele descobre os arquivos"}, {"href": "/docs/crucible/matchers", "title": "Os matchers", "desc": "is, contains, matches, throws — e o que cada um relata ao falhar"}, {"href": "/docs/crucible/fixtures", "title": "Fixtures e ganchos", "desc": "antes, depois, e o estado que não pode vazar entre testes"}, {"href": "/docs/crucible/dubles", "title": "Dublês", "desc": "substituir o que é lento, caro ou de fora"}, {"href": "/docs/crucible/propriedades", "title": "Teste por propriedade", "desc": "milhares de entradas, e a menor que quebra"}, {"href": "/docs/crucible/relatorios", "title": "Relatórios e CI", "desc": "JUnit, cobertura mínima e o código de saída"}, {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "os dois jeitos de o número mentir"}, {"href": "/docs/tecnicas/instantaneos", "title": "Instantâneos", "desc": "saída grande, e banco isolado por teste"}, {"href": "/docs/bibliotecas/testes", "title": "Testar uma biblioteca", "desc": "importar pelo nome público, e não pelo caminho"}]},
  {"h2": "Onde os testes moram"},
  {"table": {"head": ["Padrão", "Encontrado por"], "rows": [["`tests/`", "`dataforge test`"], ["`*_test.df` em qualquer lugar", "`dataforge test`"], ["`[scripts] test = …` no `forge.toml`", "`dataforge test` sem argumento"], ["`forge_modules/`", "**ignorado** de propósito"]]}},
  {"p": "A última linha é uma correção: um projeto com 13 testes relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca que ninguém daquele projeto escreveu."},
  {"h2": "As quatro perguntas que um teste responde"},
  {"table": {"head": ["Pergunta", "Forma"], "rows": [["dá o valor certo?", "`expect f(x) is esperado`"], ["falha quando deve?", "`expect f(ruim) throws ValidationError`"], ["mudou o que não devia?", "`expect saida matches snapshot`"], ["vale para **qualquer** entrada?", "teste por propriedade"]]}},
  {"p": "A segunda é a mais esquecida, e a que mais rende: um código que só é testado no caminho feliz costuma ter a mensagem de erro errada — ou nenhuma."},
  {"h2": "Um teste que reprova de verdade"},
  {"callout": {"tipo": "atencao", "titulo": "\"Tudo verde\" com um trial reprovado", "texto": "Um arquivo com `crucible`/`trial` **registra** as suítes; quem as roda é `C.run()`. O corredor caía no caso \"sem ações `test_`, o próprio arquivo é o caso\" e contava o arquivo como **um teste que passou** — dez `trial` com um quebrado saíam com código 0. Um teste que falha reportando \"Tudo verde\" é a pior falha possível num corredor: a suíte fica vermelha e o CI passa."}},
  {"p": "Hoje há um resultado por **trial**, e não por arquivo: \"1 de 2 falhou\" sem dizer qual não serve para nada."},
  {"h2": "Estado entre testes"},
  { code: `crucible "carrinho":
    setup:
        carrinho := []            // roda antes de CADA trial

    trial "comeca vazio":
        expect len(carrinho) is 0

    trial "aceita um item":
        carrinho.append("cafe")
        expect len(carrinho) is 1
`, lang: 'df' },
  {"p": "Se o segundo `trial` visse o carrinho do primeiro, a ordem dos testes passaria a importar — e um teste cuja aprovação depende da ordem não prova nada."},
  {"h2": "No CI"},
  { code: `dataforge check .
dataforge test tests/ --cobertura --minimo=80
dataforge lint src/
dataforge fmt . --check
`, lang: 'bash' },
  {"p": "Os quatro saem com código diferente de zero quando acham algo — é o que o CI lê. E `--minimo` é o que impede a cobertura de cair devagar até virar decoração."},
  {"h2": "O que testar, e o que não"},
  {"table": {"head": ["Vale o teste", "Não vale"], "rows": [["a regra de negócio", "o que a linguagem já garante"], ["a borda (vazio, zero, negativo, `void`)", "que um `+` soma"], ["o **tipo** do erro levantado", "o texto exato da mensagem"], ["o que já quebrou uma vez", "código que só repassa valor"], ["o contrato de um módulo público", "a ordem interna das chamadas"]]}},
  {"p": "A linha mais importante é a quarta: **todo bug corrigido merece um teste que falha sem a correção**. É a única forma de ele não voltar — e é a regra que este repositório segue para as centenas de correções que carrega."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/crucible", "title": "Crucible, em detalhe", "desc": "o próximo passo"}, {"href": "/docs/cli/test", "title": "dataforge test", "desc": "as opções do comando"}, {"href": "/docs/exercicios/25-testes-crucible", "title": "Exercícios", "desc": "praticar com casos que se verificam sozinhos"}]},
];

const headings = [{ id: 'o-caminho-inteiro', text: "O caminho inteiro", level: 2 as const }, { id: 'onde-os-testes-moram', text: "Onde os testes moram", level: 2 as const }, { id: 'as-quatro-perguntas-que-um-teste-responde', text: "As quatro perguntas que um teste responde", level: 2 as const }, { id: 'um-teste-que-reprova-de-verdade', text: "Um teste que reprova de verdade", level: 2 as const }, { id: 'estado-entre-testes', text: "Estado entre testes", level: 2 as const }, { id: 'no-ci', text: "No CI", level: 2 as const }, { id: 'o-que-testar-e-o-que-nao', text: "O que testar, e o que não", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes"}
      description={"Tudo sobre testar em DataForge: o corredor, os matchers, dublês, propriedades, cobertura e CI."}
      href={"/docs/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
