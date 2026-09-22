// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Decisões de desenho",
  description: "Doze escolhas que definem a linguagem, com o que cada uma evita e o que cada uma custa.",
};

const blocos: Bloco[] = [
  {"p": "Toda linguagem é um conjunto de escolhas, e cada escolha tem um preço. Esta página as lista com o preço junto — uma lista de decisões sem custo seria propaganda."},
  {"table": {"head": ["Decisão", "Evita", "Custa"], "rows": [["dependência zero em execução", "instalação que quebra, rede fechada sem pacote", "reescrever o que o ecossistema Python já tem"], ["`//` é comentário; divisão é `~/`", "confusão com o comentário de C/JS", "`// 3 parcelas` divide — e o parser agora recusa"], ["uma instrução por linha", "a instrução solta que some calada", "nenhum — nada no repositório usava duas"], ["o analisador cala quando não prova", "o falso alarme que ensina a ignorar", "deixa passar o que não consegue provar"], ["o campo vence o método", "o método que nunca roda", "`v.nome()` inalcançável se houver campo `nome`"], ["`record` imutável", "o objeto que muda por baixo de quem o guardou", "`with` para cada mudança"], ["mensagens em português, com `DF_IDIOMA=en`", "o erro de execução numa língua e o do `check` em outra", "a tradução é no desenho, e cobre parte"], ["`given` compartilha escopo; `cycle` não", "o nome decidido em dois ramos que não existe depois", "—"], ["erro de sistema é da família certa", "`handle RuntimeError` pegando tudo", "saber o nome da família"], ["concorrência sem sincronização automática", "o custo de trava em todo acesso", "o `check` avisa, mas a trava é sua"], ["`@f()` é fábrica, `@f` é aplicação", "`@app.texto()` recebendo a ação como padrão", "—"], ["o corpo de `lambda` absorve ternário e `??`", "`lambda x: v[x] ?? 0` que nunca usa o padrão", "o pipeline continua precisando de parênteses"]]}},
  {"callout": {"tipo": "nota", "titulo": "As três últimas são desta versão", "texto": "Foram achadas escrevendo a documentação: um bloco que devia rodar e não rodava, e a causa era da linguagem. É o motivo de todo bloco desta documentação ser **executado** pela suíte de testes."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Decisões de desenho"}
      description={"Doze escolhas que definem a linguagem, com o que cada uma evita e o que cada uma custa."}
      href={"/docs/ecossistema/decisoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
