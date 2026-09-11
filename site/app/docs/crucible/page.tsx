// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/crucible_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Crucible — testes",
  description: "No cadinho o metal é provado no fogo. DataForge molda, Kiln assa, Crucible prova.",
};

const blocos: Bloco[] = [
  {"p": "**Crucible** é o framework de testes da linguagem. Tem sintaxe própria — dez palavras contextuais — e 59 matchers."},
  { code: `crucible "Calculadora":

    setup:
        base := 10

    trial "soma dois números":
        expect 2 + 2 is 4

    trial "recusa divisão por zero":
        expect(lambda => 1 / 0).to_raise(DivisionByZeroError)

    trial "vê o setup":
        expect base is 10`, lang: 'df' },
  { code: `$ dataforge crucible

  ✓ Calculadora  3 trial(s), 84µs

  ────────────────────────────────────────
  3 passou   em 100µs`, lang: 'bash' },
  {"h2": "Por que um framework próprio"},
  {"p": "O `dataforge test` que já existia roda arquivos `*_test.df` e conta `assert`. Isso responde \"passou?\" e nada mais. Quando falha, a mensagem diz que uma expressão deu falso — não o que se esperava, o que veio, nem qual dos quarenta casos daquele arquivo era."},
  {"p": "O Crucible responde as outras perguntas:"},
  { code: `$ dataforge crucible

  ✗ Carrinho  4 trial(s), 1.2ms
      ✗ soma o frete

  ────────────────────────────────────────

  1) Carrinho > soma o frete
     testes/carrinho.df:18

     devia ser {"total": 130, "frete": 30}, e veio
     {"total": 100, "frete": 30}

     ~ "total": esperava 130, veio 100`, lang: 'bash' },
  {"p": "Comparar dois vaults de dez chaves lendo os dois inteiros não se faz — o Crucible aponta a chave que difere."},
  {"h2": "As garantias"},
  {"list": ["**Um trial não vaza para o próximo.** Cada um roda no próprio quadro de escopo, com as fixtures reconstruídas. Um teste que passa sozinho e falha na suíte seria bug do framework.", "**A limpeza roda mesmo com falha.** `teardown` e a parte da fixture depois do `provide` rodam em qualquer saída.", "**A ordem não importa.** Com `--aleatorio` a suíte embaralha; um teste que depende de ordem falha ali, e não seis meses depois.", "**A diferença é mostrada, não descrita.**"]},
  {"h2": "Isolamento, na prática"},
  { code: `crucible "Isolamento":
    setup:
        contador := 0

    trial "o primeiro soma":
        contador := contador + 1
        expect contador is 1

    trial "o segundo vê o valor original":
        expect contador is 0`, lang: 'df' },
  {"p": "Os dois passam. O `setup` roda antes de cada trial, num quadro novo — o que o primeiro escreveu não existe para o segundo."},
  {"h2": "As dez palavras"},
  {"table": {"head": ["Palavra", "O que abre"], "rows": [["`crucible`", "uma suíte; suítes aninham"], ["`trial`", "um caso de teste"], ["`expect`", "uma cobrança"], ["`setup`", "roda antes de cada trial (`setup all` uma vez)"], ["`teardown`", "roda depois de cada trial"], ["`fixture`", "preparo e limpeza no mesmo lugar"], ["`provide`", "entrega o valor preparado, e divide a fixture"], ["`tagged`", "marca, para filtrar depois"], ["`pending`", "não roda, e o relatório diz por quê"], ["`bench`", "mede em vez de cobrar"]]}},
  {"callout": {"tipo": "nota", "titulo": "Nenhuma delas é reservada", "texto": "`setup` é o nome do construtor de blueprint, e `expect` e `trial` são nomes bons demais para tirar de quem escreve. Elas só valem dentro de um bloco `crucible`; fora dele seguem sendo identificadores livres."}},
  {"h2": "Rodando"},
  { code: `dataforge crucible                      # tudo
dataforge crucible -v                   # mostra também o que passou
dataforge crucible --filtro=carrinho    # só os que casam
dataforge crucible --tag=rapido         # só os marcados
dataforge crucible --sem-tag=rede       # pula os marcados
dataforge crucible --aleatorio          # embaralha a ordem
dataforge crucible --semente=42         # repete um embaralhamento
dataforge crucible --repetir=10         # cada trial 10 vezes
dataforge crucible --prazo=500          # falha o que passar de 500ms
dataforge crucible --fail-fast          # para na primeira falha
dataforge crucible --formato=junit --out=r.xml
dataforge crucible --matchers           # lista os 59`, lang: 'bash' },
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/crucible/matchers", "title": "Os 59 matchers", "desc": "igualdade, tipos, coleções, erros, desempenho"}, {"href": "/docs/crucible/fixtures", "title": "Fixtures e ganchos", "desc": "preparo, limpeza e por que elas ficam juntas"}, {"href": "/docs/crucible/dubles", "title": "Dublês", "desc": "mock, spy e stub — e a diferença entre eles"}, {"href": "/docs/crucible/propriedades", "title": "Teste por propriedade", "desc": "a regra em vez dos casos, com contraexemplo encolhido"}, {"href": "/docs/crucible/relatorios", "title": "Relatórios e CI", "desc": "texto, JUnit, JSON, TAP — e benchmark com p95"}]},
];

const headings = [{ id: 'por-que-um-framework-proprio', text: "Por que um framework próprio", level: 2 as const }, { id: 'as-garantias', text: "As garantias", level: 2 as const }, { id: 'isolamento-na-pratica', text: "Isolamento, na prática", level: 2 as const }, { id: 'as-dez-palavras', text: "As dez palavras", level: 2 as const }, { id: 'rodando', text: "Rodando", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Crucible — testes"}
      description={"No cadinho o metal é provado no fogo. DataForge molda, Kiln assa, Crucible prova."}
      href={"/docs/crucible"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
