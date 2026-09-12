// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/kiln_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Instantâneos e isolamento",
  description: "Três ferramentas do Crucible para resultado grande, estado que sobra entre testes e falha que vai e volta.",
};

const blocos: Bloco[] = [
  {"p": "O que um teste comum não alcança bem."},
  {"h2": "Instantâneo"},
  { code: `adopt Crucible

crucible "o relatorio":
    trial "nao muda sem aviso":
        Crucible.snapshot("relatorio_mensal", gerar_relatorio())

    trial "e o HTML da pagina tambem":
        Crucible.snapshot("pagina_inicial", V.html_da_pagina())`, lang: 'df' },
  {"p": "Para o que é grande demais para escrever à mão no teste: o HTML de uma página, o relatório de trinta linhas, o JSON de uma rota. Escrever o esperado à mão para isso dá um teste que ninguém mantém — e um teste que ninguém mantém vira um teste que alguém comenta."},
  {"h3": "Na primeira vez ele grava e passa"},
  {"p": "É o único jeito de começar, e por isso o arquivo vai no **controle de versão**: é no diff do commit que alguém confere se o novo esperado está certo."},
  { code: `__snapshots__/relatorio_test.snap.json`, lang: 'text' },
  {"p": "Um JSON por arquivo de teste, ao lado dele — assim andam junto num `git mv`, e o diff mostra os dois lado a lado. As chaves saem **ordenadas**: um vault que muda de ordem de inserção faria o instantâneo falhar sem nada ter mudado de verdade."},
  {"h3": "Aceitar uma mudança intencional"},
  { code: `DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Nunca atualize por padrão", "texto": "Seria **pior que não ter instantâneo**: o teste passaria sempre, gravando o errado por cima do certo. A variável de ambiente existe para ser digitada de propósito, e para aparecer no histórico do shell de quem a digitou."}},
  {"h3": "Quando muda"},
  { code: `o instantaneo 'relatorio_mensal' mudou.
    @@ -3,7 +3,7 @@
       "clientes": 1240,
    -  "receita": 84200.0,
    +  "receita": 91800.0,
       "ticket": 67.9,
    para aceitar: DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible
    o arquivo:    __snapshots__/relatorio_test.snap.json`, lang: 'text' },
  {"p": "A mensagem traz o **diff**, e não os dois textos inteiros: trezentas linhas lado a lado num terminal são ilegíveis, e ter trezentas linhas é justamente o motivo de usar instantâneo."},
  {"h2": "Banco que se desfaz"},
  { code: `crucible "cadastro de livros":
    Crucible.before(lambda suite: Crucible.banco(db))

    trial "grava um livro":
        Banco.insert(db, "livros", {"titulo": "Duna", "preco": 79.9})
        Crucible.expect(Banco.count(db, "livros")).to_be(1)

    trial "e o seguinte nao ve o que ele gravou":
        Crucible.expect(Banco.count(db, "livros")).to_be(0)`, lang: 'df' },
  {"p": "O problema: um teste que grava deixa a linha lá, e o teste seguinte a encontra. A suíte passa **na ordem em que foi escrita** e falha em qualquer outra — e `--aleatorio` expõe isso de um jeito que parece intermitente."},
  {"p": "`Crucible.banco(db)` abre uma transação e a desfaz no fim do trial, sempre. Apagar tudo entre testes seria a alternativa, e é mais lenta e mais frágil: ela precisa saber a ordem das chaves estrangeiras."},
  {"callout": {"tipo": "dica", "titulo": "Vale para migração também", "texto": "Rode `Banco.migrate` uma vez no `before_all` e envolva cada trial em `Crucible.banco(db)`. O schema é criado uma vez; o dado, nunca sobra."}},
  {"h2": "Teste instável"},
  { code: `crucible "integracao":
    trial "consulta a API externa":
        r := Crucible.flaky(lambda: Http.get(URL).json(), 3, 0.5)
        Crucible.expect(r["ok"]).to_be(yes)`, lang: 'df' },
  {"p": "Existe para o que depende de rede, de relógio ou de escalonamento — e **não** para esconder um bug. Por isso ele devolve o número de tentativas:"},
  { code: `{"ok": yes, "tentativas": 3}`, lang: 'text' },
  {"p": "Um teste que precisa de três tentativas toda vez não é instável, **está quebrado**, e o número é o que denuncia isso. Se ele aparece como 3 no seu relatório, o problema não é a rede."},
  {"callout": {"tipo": "nota", "titulo": "`to_raise` não captura a desistência", "texto": "O que `flaky` levanta ao desistir é a própria falha de expectativa do Crucible, que é o **sinal de teste reprovado** — não um erro a capturar. Use `monitor`/`handle` quando quiser conferir a desistência."}},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/tecnicas/testes", "title": "Crucible", "meta": "50 símbolos", "desc": "Suítes, matchers, dublês, fixtures, propriedade e benchmark."}, {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "Quais linhas os testes executaram."}, {"href": "/docs/exercicios/31-qualidade", "title": "Os exercícios", "desc": "Instantâneo, isolamento e instabilidade, verificados."}]},
];

const headings = [{ id: 'instantaneo', text: "Instantâneo", level: 2 as const }, { id: 'na-primeira-vez-ele-grava-e-passa', text: "Na primeira vez ele grava e passa", level: 3 as const }, { id: 'aceitar-uma-mudanca-intencional', text: "Aceitar uma mudança intencional", level: 3 as const }, { id: 'quando-muda', text: "Quando muda", level: 3 as const }, { id: 'banco-que-se-desfaz', text: "Banco que se desfaz", level: 2 as const }, { id: 'teste-instavel', text: "Teste instável", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Instantâneos e isolamento"}
      description={"Três ferramentas do Crucible para resultado grande, estado que sobra entre testes e falha que vai e volta."}
      href={"/docs/tecnicas/instantaneos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
