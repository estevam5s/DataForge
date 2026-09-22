// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os erros da sua biblioteca",
  description: "A classe do erro é o contrato — e um erro genérico mata a distinção na fronteira do handle.",
};

const blocos: Bloco[] = [
  {"p": "Quem usa a sua biblioteca escreve `handle`. O que ele consegue escrever ali é decidido inteiramente por você."},
  {"callout": {"tipo": "atencao", "titulo": "`trigger \"texto\"` em tudo apaga a distinção", "texto": "Para quem escreve o `handle`, *violar uma regra de negócio* e *dividir por zero* viram a mesma coisa — e a única saída passa a ser comparar o **texto** da mensagem, que quebra na primeira tradução e na primeira correção de vírgula."}},
  { code: `record FalhaDeLeitura:
    caminho: String
    motivo: String

record FalhaDeFormato:
    linha: Integer
    esperado: String

action carregar(caminho):
    given not caminho.endswith(".csv"):
        trigger FalhaDeFormato(1, "um arquivo .csv")
    given caminho.startswith("/nao-existe"):
        trigger FalhaDeLeitura(caminho, "nao encontrado")
    yield ["ok"]

monitor:
    carregar("dados.txt")
handle FalhaDeFormato as e:
    f := e.value
    out $"linha {f.linha}: esperava {f.esperado}"
handle FalhaDeLeitura as e:
    f := e.value
    out $"nao li {f.caminho}: {f.motivo}"

assert carregar("dados.csv") is ["ok"]`, lang: 'df' },
  {"h2": "Uma base por família"},
  {"p": "Quando a biblioteca tem seis erros, quem a usa quase nunca quer os seis separados — quer *“qualquer coisa que a sua biblioteca levante”*. Uma base comum entrega isso, e ela tem de ser conferida nas **duas** direções."},
  {"table": {"head": ["A conferir", "O que quebra sem isso"], "rows": [["a base pega **todas** as suas", "uma nova nasce fora da família, e o `handle` do usuário passa a deixá-la escapar"], ["a base **não** pega as de fora", "`handle SuaBase` vira um `handle` sem tipo — e engole o `1 / 0` do usuário"]]}},
  {"h2": "A mensagem diz o que fazer"},
  {"table": {"head": ["Ruim", "Bom"], "rows": [["`Invalid assignment target`", "`'no' é palavra reservada e não pode receber valor. Escolha outro nome.`"], ["`KeyError: cidad`", "`A chave \"cidad\" não está neste vault. Você quis dizer \"cidade\"?`"], ["`Connection failed`", "`Não conectei em localhost:5432 — o banco está no ar? 'docker compose up banco' sobe o do projeto.`"]]}},
  {"callout": {"tipo": "dica", "titulo": "Nenhuma mensagem cita tipo do Python", "texto": "`int`, `str`, `list`, `dict` e `NoneType` não existem nesta linguagem, e uma mensagem nesses termos manda a pessoa procurar na documentação errada — ela não tem como saber que `list` é `Cluster`. Há teste sobre o **código** do interpretador proibindo `type(x).__name__` dentro de f-string de mensagem: foi assim que cinco delas chegaram lá, e a trava achou outras três que ninguém tinha visto."}},
  {"p": "Continue em [Erros](/docs/erros) e [O vault de opções](/docs/bibliotecas/opcoes)."},
];

const headings = [{ id: 'uma-base-por-familia', text: "Uma base por família", level: 2 as const }, { id: 'a-mensagem-diz-o-que-fazer', text: "A mensagem diz o que fazer", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Os erros da sua biblioteca"}
      description={"A classe do erro é o contrato — e um erro genérico mata a distinção na fronteira do handle."}
      href={"/docs/bibliotecas/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
