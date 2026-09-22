// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Projetos",
  description: "Três projetos completos e vinte e dois tipos de projeto, cada um montado e testado a cada build.",
};

const blocos: Bloco[] = [
  {"p": "Dois níveis de exemplo. Os **projetos completos** moram em `projetos/` no repositório, com `forge.toml`, dependências reais e testes próprios. Os **vinte e dois tipos** abaixo mostram o que muda de um tipo de programa para outro — e cada um é conferido a cada build: o manifesto, o núcleo e o teste são escritos numa pasta, e `dataforge test` precisa passar."},
  { code: `cd projetos/gestor-tarefas
dataforge install
dataforge test tests/
dataforge run src/main.df -- listar`, lang: 'bash' },
  {"h2": "Projetos completos"},
  {"table": {"head": ["Projeto", "O que faz", "Bibliotecas"], "rows": [["[Gestor de tarefas](/docs/projetos/gestor-tarefas)", "CLI com prazos e persistência", "6"], ["[Análise de vendas](/docs/projetos/analise-vendas)", "CSV → relatório estatístico", "6"], ["[API de links](/docs/projetos/api-links)", "Encurtador com servidor HTTP", "6"]]}},
  {"h2": "Os vinte e dois tipos"},
  {"p": "Cada página traz a estrutura de pastas, o `forge.toml`, um núcleo que roda sozinho, o teste, a tabela de decisões — *o que quebra sem cada uma* — e para onde ir depois."},
  {"h3": "Terminal e ferramentas"},
  {"table": {"head": ["Tipo", "O que ele mostra"], "rows": [["[CLI de anotações](/docs/projetos/cli-notas)", "Uma ferramenta de terminal com subcomandos, persistência em JSON e saída legível."], ["[Jogo de terminal](/docs/projetos/jogo)", "Jogo da velha com um adversário que não perde — minimax com poda."], ["[Interpretador de expressões](/docs/projetos/interpretador)", "Lexer, parser recursivo descendente e avaliador — uma calculadora com variáveis."], ["[Agendador cron](/docs/projetos/agendador)", "Ler uma expressão cron, dizer quando ela roda — e recusar a que nunca roda."], ["[Gerador de site estático](/docs/projetos/site-estatico)", "Markdown para HTML com modelo, índice gerado e o texto sempre escapado."]]}},
  {"h3": "Web e serviços"},
  {"table": {"head": ["Tipo", "O que ele mostra"], "rows": [["[API REST com CRUD](/docs/projetos/api-rest)", "Os cinco verbos sobre um recurso, com os status certos e validação na entrada."], ["[Serviço de autenticação](/docs/projetos/autenticacao)", "Cadastro, login com scrypt, bloqueio progressivo e token assinado com prazo."], ["[Bot de atendimento](/docs/projetos/bot-atendimento)", "Um bot de Telegram com menu, conversa em etapas e fallback — testado sem token e sem rede."], ["[Painel de dados](/docs/projetos/painel)", "Um dashboard com filtro, métricas e tabela — testado com a sonda, sem navegador."], ["[Pedido distribuído](/docs/projetos/saga)", "Reservar, cobrar e despachar em três serviços — e desfazer em ordem inversa quando um falha."]]}},
  {"h3": "Dados"},
  {"table": {"head": ["Tipo", "O que ele mostra"], "rows": [["[Pipeline ETL](/docs/projetos/etl)", "Extrair, converter, validar e carregar — e separar a linha ruim em vez de parar tudo."], ["[Classificador de clientes](/docs/projetos/classificador)", "Treinar, medir no que o modelo não viu, e explicar o que ele aprendeu."], ["[Planilha reativa](/docs/projetos/planilha-reativa)", "Células que dependem de células — recalculadas sozinhas, só quando alguém lê, e sem o valor que nunca existiu."], ["[Planejador de rotas](/docs/projetos/rotas)", "Menor caminho com Dijkstra, o caminho reconstruído e o bairro inalcançável tratado."]]}},
  {"h3": "Negócio"},
  {"table": {"head": ["Tipo", "O que ele mostra"], "rows": [["[Motor de regras](/docs/projetos/motor-de-regras)", "Regras de desconto e elegibilidade como dados, com o motivo de cada decisão."], ["[Cálculo financeiro](/docs/projetos/folha-de-pagamento)", "Folha de pagamento com faixas progressivas — em Decimal, e com o centavo que sobra repartido."], ["[Fluxo de pedido](/docs/projetos/maquina-de-estados)", "Uma máquina de estados explícita, que recusa a transição impossível e guarda o histórico."], ["[Controle de estoque](/docs/projetos/estoque)", "Entrada, saída, reserva e o estoque mínimo — com a invariante que nunca deixa o saldo negativo."], ["[Processador de fila](/docs/projetos/fila-de-trabalho)", "Tarefas com retentativa, recuo exponencial e carta morta — sem perder nenhuma."]]}},
  {"h3": "Segurança"},
  {"table": {"head": ["Tipo", "O que ele mostra"], "rows": [["[Detector em log](/docs/projetos/detector-de-intrusao)", "Ler um log de acesso, correlacionar por IP e alertar força bruta com os eventos que a causaram."], ["[Cofre de segredos](/docs/projetos/cofre-de-segredos)", "Cifrar por envelope, rotacionar a chave sem reescrever os dados, e recusar o dado adulterado."]]}},
  {"h3": "Ecossistema"},
  {"table": {"head": ["Tipo", "O que ele mostra"], "rows": [["[Biblioteca publicável](/docs/projetos/biblioteca)", "Validador de placas de veículo — com `relay`, erro que diz o motivo e o pacote pronto para o registro."]]}},
  {"h2": "Começar um projeto"},
  {"p": "`dataforge new` cria o esqueleto de dez modelos — e todo projeto criado passa nos próprios testes antes de você mexer em qualquer coisa."},
  { code: `dataforge new loja --modelo=api
cd loja
dataforge test tests/`, lang: 'bash' },
  {"table": {"head": ["Modelo", "Parte de"], "rows": [["`cli`", "[CLI de anotações](/docs/projetos/cli-notas)"], ["`api`", "[API REST com CRUD](/docs/projetos/api-rest)"], ["`data`", "[Pipeline ETL](/docs/projetos/etl)"], ["`painel`", "[Painel de dados](/docs/projetos/painel)"], ["`bot`", "[Bot de atendimento](/docs/projetos/bot-atendimento)"], ["`lib`", "[Biblioteca publicável](/docs/projetos/biblioteca)"]]}},
  {"callout": {"tipo": "dica", "titulo": "A regra de todos", "texto": "A regra de negócio nunca conhece o transporte. A rota, o comando e a mensagem do bot só traduzem — o que decide mora numa ação que se testa em milissegundos, sem socket, sem terminal e sem token."}},
];

const headings = [{ id: 'projetos-completos', text: "Projetos completos", level: 2 as const }, { id: 'os-vinte-e-dois-tipos', text: "Os vinte e dois tipos", level: 2 as const }, { id: 'terminal-e-ferramentas', text: "Terminal e ferramentas", level: 3 as const }, { id: 'web-e-servicos', text: "Web e serviços", level: 3 as const }, { id: 'dados', text: "Dados", level: 3 as const }, { id: 'negocio', text: "Negócio", level: 3 as const }, { id: 'seguranca', text: "Segurança", level: 3 as const }, { id: 'ecossistema', text: "Ecossistema", level: 3 as const }, { id: 'comecar-um-projeto', text: "Começar um projeto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Projetos"}
      description={"Três projetos completos e vinte e dois tipos de projeto, cada um montado e testado a cada build."}
      href={"/docs/projetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
