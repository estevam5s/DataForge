// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Produção",
  description: "Subir, recarregar ao salvar, observar, estender com plugins e o que colocar na frente.",
};

const blocos: Bloco[] = [
  {"h2": "A linha de comando"},
  { code: `dataforge vitrine new meupainel   # cria o projeto
dataforge vitrine dev             # sobe recarregando ao salvar
dataforge vitrine run             # sobe, sem recarregar
dataforge vitrine doctor          # diz por que ela não sobe

dataforge vitrine dev --porta=8600 --host=0.0.0.0`, lang: 'bash' },
  {"p": "Sem argumento, ele procura `main.df`, `app.df`, `painel.df` e `src/main.df`, nessa ordem, e depois a entrada do `forge.toml`. A porta e o host da linha de comando **vencem** o que está escrito no arquivo — é o que permite trocar a porta sem editar o programa."},
  {"p": "O `doctor` responde as perguntas de quem está vendo uma tela em branco, da causa mais provável para a menos: o módulo carrega, o Kiln está lá, existe um arquivo que sobe, ele compila, ele adota a Vitrine, ele chama `V.subir`, a porta está livre."},
  {"callout": {"tipo": "nota", "titulo": "Não há `build` nem `deploy`", "texto": "Não existe etapa de build numa aplicação Vitrine: sem bundler, sem transpilação, sem `node_modules` — o que roda é o próprio `.df`. E `deploy` seria inventar uma opinião sobre Docker, systemd ou nuvem que o projeto não tem. Os dois comandos existem só para **explicar isso** a quem veio de outro framework, em vez de responder \"comando desconhecido\"."}},
  {"p": "Para distribuir o projeto, `dataforge pack`."},
  {"h2": "Subir"},
  { code: `V.rodar(painel, porta := 8501)                 // uma página
V.subir(porta := 8501, recarregar := yes)      // com hot reload
porta := V.servir(0)                            // em segundo plano
V.parar_servidor()`, lang: 'df' },
  {"p": "`V.servir(0)` deixa o sistema escolher a porta e devolve qual foi — é o que torna um teste de integração independente de porta ocupada."},
  {"h2": "Hot reload"},
  {"p": "Com `recarregar := yes`, salvar um `.df` do projeto **reinicia o processo**. Reiniciar, e não recarregar o módulo: o estado de um módulo recarregado pela metade produz erros que não existem no código, e depurar isso custa mais do que o segundo do reinício."},
  {"h2": "Configuração"},
  { code: `V.app("Painel",
      icone := "📊",
      descricao := "Vendas da Forja Ltda.",
      tema := "escuro",
      producao := yes,
      validade_sessao := 1800,
      limite_upload := 4194304)

V.configurar("atualizar_a_cada", 30)`, lang: 'df' },
  {"table": {"head": ["Chave", "Faz"], "rows": [["`titulo` · `icone` · `descricao`", "aba do navegador e metadados"], ["`tema`", "`\"claro\"`, `\"escuro\"` ou um vault de cores"], ["`modo_tema`", "`\"automatico\"` segue o sistema de quem abre"], ["`producao`", "esconde o detalhe do erro e o diagnóstico"], ["`validade_sessao`", "segundos até a sessão ociosa sair da memória"], ["`limite_upload`", "bytes por arquivo enviado"], ["`atualizar_a_cada`", "segundos entre recargas automáticas"], ["`css` · `javascript`", "o seu, injetado na página"], ["`manifesto`", "serve um manifesto PWA em `/__vitrine__/manifesto.json`"], ["`https`", "marca o cookie de sessão como `Secure`"]]}},
  {"h3": "Tema"},
  { code: `V.configurar("tema", {
    "primaria": "#0F62FE",
    "raio": "4px",
    "largura": "1400px"
})`, lang: 'df' },
  {"p": "Um tema é um vault de variáveis CSS. Mudar a cor primária muda o botão, o link, o foco, a borda do campo e a primeira série do gráfico ao mesmo tempo — e não em nove lugares. Um tema parcial completa o que falta a partir do claro **e** do escuro, para que quem trocou a primária não perca o modo escuro por isso."},
  {"h2": "Observabilidade"},
  { code: `V.registrar("consulta lenta", "aviso", {"ms": 1840})
V.logs(50, "erro")
V.metricas()      // execuções, erros, média em ms, sessões, cache
V.saude()         // o que um balanceador pergunta`, lang: 'df' },
  {"p": "Duas rotas vêm prontas: `GET /__vitrine__/saude` e `GET /__vitrine__/metricas`. O log em memória tem teto de 2 000 linhas — sem teto, ele é um vazamento que só aparece depois de semanas no ar."},
  {"h2": "Middleware"},
  { code: `action so_de_dia(ctx):
    given Time.hora() bigger 22:
        V.aviso("O painel está fechado à noite.")
        yield no                  // 'no' interrompe a página
    yield yes

V.antes(so_de_dia)`, lang: 'df' },
  {"p": "`V.antes` roda antes de toda página e pode interromper; `V.depois` recebe o contexto já montado. Para middleware de **HTTP** — CORS, limite de taxa, compressão —, use o do Kiln sobre `V.montar()`."},
  {"h2": "Trabalho fora do pedido"},
  { code: `V.tarefa(enviar_email, destinatario)    // roda numa thread, não espera
V.agendar(recalcular_totais, 3600)      // de hora em hora`, lang: 'df' },
  {"p": "`V.tarefa` é para o que a página não vai mostrar agora. Para um resultado que a página precisa, `Arcane.Async`, que tem `await`. O primeiro disparo de `V.agendar` é depois do primeiro intervalo — agendar algo \"a cada hora\" não deveria fazê-lo agora e de novo em uma hora."},
  {"h2": "Plugins"},
  { code: `action tema_da_empresa(app):
    app.configurar("tema", {"primaria": "#7B1FA2"})
    app.configurar("css", ".v-titulo { letter-spacing: -.03em }")

V.plugin("tema-empresa", tema_da_empresa)`, lang: 'df' },
  {"p": "Um plugin é uma ação que recebe a aplicação e acrescenta algo. Registrar duas vezes o mesmo nome é **erro**, e não substituição silenciosa: quase sempre é um `adopt` duplicado, e descobrir isso por um comportamento que sumiu é caro."},
  {"h2": "O que colocar na frente"},
  {"callout": {"tipo": "atencao", "titulo": "Em produção pública, ponha um nginx ou Caddy na frente", "texto": "A Vitrine roda sobre o Kiln, que roda sobre o `http.server` do Python: não há HTTP/2, TLS nem streaming de resposta. O proxy cuida de TLS, compressão e arquivos estáticos; a Vitrine cuida da aplicação."}},
  {"p": "E a sessão vive **na memória do processo**. Com mais de um processo, dois pedidos da mesma pessoa caem em memórias diferentes — para escalar horizontalmente, uma sessão compartilhada precisa existir primeiro. Um processo por aplicação, com o proxy na frente, é a forma testada."},
  {"h2": "Atualização automática"},
  { code: `action acompanhar():
    V.atualizar_a_cada(15)
    V.metrica("Fila", tamanho_da_fila())`, lang: 'df' },
  {"p": "A página se recarrega sozinha nesse intervalo — e **não** quando a aba está escondida, porque cobrar do servidor por uma página que ninguém está vendo é desperdício puro."},
  {"p": "É o \"tempo real\" do framework, e ele é por pergunta e não por empurrão: o Kiln não tem WebSocket. Para um painel que muda a cada segundos, perguntar é suficiente e não quebra atrás de proxy nenhum."},
];

const headings = [{ id: 'a-linha-de-comando', text: "A linha de comando", level: 2 as const }, { id: 'subir', text: "Subir", level: 2 as const }, { id: 'hot-reload', text: "Hot reload", level: 2 as const }, { id: 'configuracao', text: "Configuração", level: 2 as const }, { id: 'tema', text: "Tema", level: 3 as const }, { id: 'observabilidade', text: "Observabilidade", level: 2 as const }, { id: 'middleware', text: "Middleware", level: 2 as const }, { id: 'trabalho-fora-do-pedido', text: "Trabalho fora do pedido", level: 2 as const }, { id: 'plugins', text: "Plugins", level: 2 as const }, { id: 'o-que-colocar-na-frente', text: "O que colocar na frente", level: 2 as const }, { id: 'atualizacao-automatica', text: "Atualização automática", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Produção"}
      description={"Subir, recarregar ao salvar, observar, estender com plugins e o que colocar na frente."}
      href={"/docs/vitrine/producao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
