// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Referência da CLI",
  description: "Todo comando, com uso, opções, exemplos e apelidos — gerada do catálogo.",
};

const blocos: Bloco[] = [
  {"p": "Todo comando, na ordem do `dataforge help`. Esta página é **gerada** do catálogo `cli.GRUPOS` — o mesmo que o `help`, o autocompletar e `/api/comandos.json` leem."},
  {"h2": "Projeto"},
  {"h3": "init"},
  {"p": "Cria forge.toml e o esqueleto do projeto. Ver [a página](/docs/cli/init)."},
  { code: `dataforge init [pasta]`, lang: 'bash' },
  { code: `Escreve o manifesto, a pasta src/ com um main.df e a tests/.
Sem argumento, usa a pasta atual.`, lang: 'text' },
  { code: `dataforge init                                       # aqui mesmo
dataforge init meu-app                               # numa pasta nova`, lang: 'bash' },
  {"p": "Veja: `new`, `info`."},
  {"h3": "api"},
  {"p": "exporta a API de um servidor Kiln. Ver [a página](/docs/tecnicas/api)."},
  { code: `dataforge api <arquivo.df> [--formato]`, lang: 'bash' },
  { code: `As rotas sao a fonte da verdade: o arquivo e executado
para que elas se registrem, e o resultado sai do que
esta la — nao de uma descricao escrita a mao, que
divergiria na primeira semana.

Aponte para o modulo que MONTA o servidor ('app.df'), e
nao para o que sobe ('main.df').`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--openapi`", "OpenAPI 3.1 — Swagger, geradores de cliente"], ["`--insomnia`", "colecao do Insomnia, uma requisicao por rota"], ["`--postman`", "colecao do Postman v2.1"], ["`--curl`", "um comando curl por rota"], ["`--markdown`", "a tabela de rotas (padrao)"], ["`--saida=<arq>`", "grava em vez de imprimir"]]}},
  { code: `dataforge api src/app.df                             # a tabela de rotas
dataforge api src/app.df --openapi -o=openapi.json
dataforge api src/app.df --insomnia -o=insomnia.json`, lang: 'bash' },
  {"p": "Veja: `run`, `test`."},
  {"h3": "converter"},
  {"p": "traduz Python para DataForge. Ver [a página](/docs/cli/scripts)."},
  { code: `dataforge converter <arquivo.py|pasta>`, lang: 'bash' },
  { code: `Le com o 'ast' do Python, e nao com expressao regular.
O que nao tem equivalente honesto vira um comentario
'TODO(converter)' com o codigo original ao lado — um
conversor que erra em silencio e pior que um que aponta
onde errou.

O relatorio no fim conta as duas coisas: o que saiu pronto
e o que precisa de voce.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--saida=<arq>`", "onde gravar (um arquivo so)"], ["`--seco`", "mostra sem gravar"], ["`--forcar`", "sobrescreve um .df que ja exista"]]}},
  { code: `dataforge converter app.py                           # grava app.df ao lado
dataforge converter src/                             # a pasta inteira, recursiva
dataforge converter app.py --seco                    # so mostra`, lang: 'bash' },
  {"p": "Também: `convert`, `migrar`. Veja: `check`, `fmt`."},
  {"h3": "new"},
  {"p": "Cria um projeto a partir de um modelo. Ver [a página](/docs/cli/new)."},
  { code: `dataforge new [modelo] [nome]`, lang: 'bash' },
  { code: `10 modelos, e todos produzem um projeto que RODA e
passa nos proprios testes — nao um esqueleto com TODOs:

  cli      Lê argumentos, imprime tabela colorida, tem --help
  api      Servidor com rotas, JSON, 404/405 e testes sem socket
  web      Templates HTML, arquivos estáticos e escape automático
  data     Banco, estatística e exportação para Excel
  lib      Um pacote com relay, testes e pronto para publicar
  oop      Blueprints, traits, propriedades e operadores
  script   Arquivos, JSON, datas e processos do sistema
  painel   Um dashboard: métricas, gráficos, filtros e testes
  bot      Comandos, botões, conversa com estado e testes sem rede
  test     Como testar em DataForge: asserts, erros e cobertura

Sem argumento, pergunta na tela.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--list`", "so lista os modelos, sem perguntar nada"]]}},
  { code: `dataforge new                                        # escolhe na tela
dataforge new api                                    # usa o modelo, pergunta o nome
dataforge new api minha-api                          # direto ao ponto
dataforge new --list                                 # so os modelos`, lang: 'bash' },
  {"p": "Veja: `init`, `run`, `test`."},
  {"h3": "info"},
  {"p": "Mostra o manifesto do projeto atual. Ver [a página](/docs/cli/new)."},
  { code: `dataforge info`, lang: 'bash' },
  { code: `Nome, versao, entrada, scripts e dependencias declaradas.`, lang: 'text' },
  {"p": "Veja: `init`, `list`."},
  {"h2": "Executar"},
  {"h3": "run"},
  {"p": "Executa um programa. Ver [a página](/docs/cli/run)."},
  { code: `dataforge run [arquivo.df] [-- args]`, lang: 'bash' },
  { code: `Sem arquivo, usa a entrada declarada no forge.toml.
O que vier depois de '--' chega ao programa em OS.argv().`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--time`", "mostra o tempo de execucao"], ["`--debug`", "mostra tokens, AST e traceback completo"]]}},
  { code: `dataforge run ola.df
dataforge run                                        # usa a entrada do forge.toml
dataforge run app.df -- --porta 8080                 # passa argumentos ao programa`, lang: 'bash' },
  {"p": "Veja: `eval`, `watch`, `repl`."},
  {"h3": "eval"},
  {"p": "Executa uma linha de codigo direto. Ver [a página](/docs/cli/scripts)."},
  { code: `dataforge eval '<codigo>'`, lang: 'bash' },
  { code: `Para experimentar sem criar arquivo. Multiplas instrucoes
podem ser separadas por ponto e virgula ou quebra de linha.`, lang: 'text' },
  { code: `dataforge eval 'out 2 ** 10'
dataforge eval 'out [1,2,3] >> morph n: n * 2'`, lang: 'bash' },
  {"p": "Veja: `run`, `repl`."},
  {"h3": "watch"},
  {"p": "Reexecuta a cada mudanca no arquivo. Ver [a página](/docs/cli/watch)."},
  { code: `dataforge watch [arquivo.df]`, lang: 'bash' },
  { code: `Fica observando e roda de novo quando voce salva.
Ctrl+C para sair.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--test`", "roda a suite em vez do arquivo"], ["`--check`", "roda a analise estatica"]]}},
  { code: `dataforge watch src/main.df
dataforge watch --test                               # TDD: a suite a cada save`, lang: 'bash' },
  {"p": "Veja: `run`, `test`."},
  {"h3": "repl"},
  {"p": "Console interativo. Ver [a página](/docs/cli/repl)."},
  { code: `dataforge repl`, lang: 'bash' },
  { code: `Comandos internos: :type <expr>, :ast <expr>, :check <expr>,
:load <arquivo>, :vars, :help, :quit.`, lang: 'text' },
  {"p": "Veja: `run`, `eval`."},
  {"h2": "Qualidade"},
  {"h3": "check"},
  {"p": "Analise estatica: nomes, aridade, tipos e alcance. Ver [a página](/docs/cli/check)."},
  { code: `dataforge check [alvo]`, lang: 'bash' },
  { code: `Aceita arquivo, pasta ou padrao. Sem alvo, analisa a pasta atual.
Sai com codigo 1 se houver erro — serve na esteira de CI.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--strict`", "trata avisos como erros"], ["`--syntax-only`", "so a sintaxe, sem analise semantica"], ["`--formato=github`", "anotacoes do Actions: o erro aparece na linha do PR"]]}},
  { code: `dataforge check .                                    # o projeto inteiro
dataforge check src/ --strict                        # avisos viram erros
dataforge check . --formato=github                   # no CI do GitHub`, lang: 'bash' },
  {"p": "Veja: `lint`, `explain`."},
  {"h3": "test"},
  {"p": "Executa a suite de testes. Ver [a página](/docs/cli/test)."},
  { code: `dataforge test [alvo]`, lang: 'bash' },
  { code: `Descobre *_test.df e a pasta tests/. Cada acao que comeca
com 'test_' vira um caso.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--verbose, -v`", "mostra cada caso"], ["`--filter=<texto>`", "so os casos cujo nome contem o texto"], ["`--fail-fast`", "para na primeira falha"], ["`--cobertura`", "quais linhas os testes executaram"], ["`--minimo=<n>`", "falha se a cobertura ficar abaixo de n%"], ["`--linhas`", "lista as linhas descobertas, em faixas"]]}},
  { code: `dataforge test
dataforge test tests/ -v
dataforge test --cobertura                           # com o relatorio
dataforge test --minimo=80                           # exige 80% no CI
dataforge test --filter=soma                         # so o que casa`, lang: 'bash' },
  {"p": "Veja: `bench`, `watch`."},
  {"h3": "fmt"},
  {"p": "Formata o codigo. Ver [a página](/docs/cli/fmt)."},
  { code: `dataforge fmt [alvo]`, lang: 'bash' },
  { code: `Idempotente: formatar duas vezes da o mesmo resultado.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--check`", "so verifica, nao reescreve (sai 1 se houver pendencia)"]]}},
  { code: `dataforge fmt .                                      # reescreve
dataforge fmt . --check                              # para a esteira de CI`, lang: 'bash' },
  {"p": "Veja: `lint`."},
  {"h3": "lint"},
  {"p": "Aponta problemas de estilo e higiene. Ver [a página](/docs/cli/lint)."},
  { code: `dataforge lint [alvo]`, lang: 'bash' },
  { code: `Treze regras: nome fora do padrao, variavel escrita e nunca
lida, ramo redundante, e outras.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--strict`", "trata avisos como erros"]]}},
  {"p": "Veja: `fmt`, `check`."},
  {"h3": "seguranca"},
  {"p": "Procura segredo escrito no codigo e padrao arriscado. Ver [a página](/docs/cli/seguranca)."},
  { code: `dataforge seguranca [alvo]`, lang: 'bash' },
  { code: `Duas varreduras sobre cada arquivo. A primeira acha SEGREDO pelo
formato — chave da AWS, token do GitHub, 'sk_live' da Stripe,
bloco de chave privada, token do PyPI —, e por isso acha o que
voce esqueceu, que e o unico tipo que importa. A segunda aplica
dez regras sintaticas: SQL concatenado, shell com interpolacao,
MD5 para assinatura, senha sem derivacao, verificacao desligada.

Ela le TEXTO, e nao a arvore, de proposito: um analisador de
seguranca que tenta provar fluxo de dado erra nos dois sentidos,
e o que se faz com o alarme errado e desligar tudo.

Alem de '.df', ela le '.env', '.json', '.toml', '.yml', '.sh' e
'.ts' — um segredo vaza do arquivo de configuracao muito mais do
que do codigo.

'// df: permitir <regra>' na linha, ou na de cima, silencia ali.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--strict`", "sai com 1 se houver qualquer achado"], ["`--json`", "a saida como dado, para a esteira de CI"], ["`--so=<gravidade>`", "'alto' esconde os medios"]]}},
  { code: `dataforge seguranca .                                # o projeto inteiro
dataforge seguranca src/ --strict                    # reprova o CI
dataforge seguranca . --json                         # para outra ferramenta`, lang: 'bash' },
  {"p": "Também: `sec`, `audit`. Veja: `lint`, `check`."},
  {"h3": "bench"},
  {"p": "Mede o tempo de execucao, repetindo. Ver [a página](/docs/cli/bench)."},
  { code: `dataforge bench <arquivo.df>`, lang: 'bash' },
  { code: `Roda varias vezes e mostra minimo, mediana e desvio.
Descarta as primeiras execucoes, que aquecem o cache.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--runs=<n>`", "quantas repeticoes (padrao 10)"]]}},
  { code: `dataforge bench algoritmo.df
dataforge bench alg.df --runs=50`, lang: 'bash' },
  {"p": "Veja: `test`, `run`."},
  {"h2": "Pacotes"},
  {"h3": "add"},
  {"p": "Instala uma dependencia e grava no forge.toml. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge add <pacote>[@versao] …`, lang: 'bash' },
  { code: `Sem faixa, grava '^' da versao mais recente. Aceita tambem
caminho local, git+URL e URL de tarball.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--offline`", "so com o cache local"]]}},
  { code: `dataforge add validador
dataforge add tabela@^2.0                            # faixa de versoes
dataforge add ../lib-interna                         # pasta local`, lang: 'bash' },
  {"p": "Veja: `install`, `remove`, `search`."},
  {"h3": "remove"},
  {"p": "Desinstala e tira do forge.toml. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge remove <pacote> …`, lang: 'bash' },
  {"p": "Também: `rm`, `uninstall`. Veja: `add`, `list`."},
  {"h3": "install"},
  {"p": "Instala o que o forge.lock fixa. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge install`, lang: 'bash' },
  { code: `O comando que se roda depois de clonar um projeto.

Ele HONRA o forge.lock: a versao travada vence enquanto
couber na faixa do forge.toml. Duas pessoas que clonam o
mesmo projeto em dias diferentes recebem o mesmo codigo,
e o sha256 do lock e conferido contra o que chegou.

Para MOVER as versoes, 'dataforge update'.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--dry-run`", "mostra o plano sem baixar"], ["`--offline`", "so com o cache local"]]}},
  {"p": "Também: `i`, `sync`. Veja: `update`, `add`, `list`, `tree`."},
  {"h3": "update"},
  {"p": "Move as versoes e reescreve o forge.lock. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge update [pacote …]`, lang: 'bash' },
  { code: `Resolve de novo dentro das faixas declaradas. Sem nome,
atualiza tudo; com nomes, so eles — o resto continua
travado, que e o que torna a atualizacao controlada.

Sair da faixa exige mudar o forge.toml: 'dataforge
outdated' mostra os dois casos separados.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--dry-run`", "mostra o plano sem baixar"], ["`--offline`", "so com o cache local"]]}},
  { code: `dataforge update                                     # tudo, dentro das faixas
dataforge update tabela                              # so este pacote`, lang: 'bash' },
  {"p": "Também: `up`. Veja: `install`, `outdated`, `list`."},
  {"h3": "list"},
  {"p": "Mostra o que esta instalado. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge list`, lang: 'bash' },
  { code: `Marca as transitivas e o que sumiu do disco.`, lang: 'text' },
  {"p": "Também: `ls`. Veja: `tree`, `outdated`."},
  {"h3": "tree"},
  {"p": "Desenha a arvore de dependencias. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge tree`, lang: 'bash' },
  { code: `Mostra quem trouxe cada pacote, e onde ha versao compartilhada.`, lang: 'text' },
  {"p": "Veja: `list`, `why`."},
  {"h3": "why"},
  {"p": "Explica por que um pacote esta instalado. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge why <pacote>`, lang: 'bash' },
  { code: `Mostra a cadeia desde o forge.toml ate ele.`, lang: 'text' },
  { code: `dataforge why tabela`, lang: 'bash' },
  {"p": "Veja: `tree`, `list`."},
  {"h3": "outdated"},
  {"p": "Lista dependencias com versao mais nova disponivel. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge outdated`, lang: 'bash' },
  { code: `Separa o que cabe na faixa declarada do que exigiria
mudar o forge.toml — os primeiros sobem com
'dataforge update'.`, lang: 'text' },
  {"p": "Veja: `update`, `add`, `list`."},
  {"h3": "search"},
  {"p": "Procura pacotes no registro. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge search <termo>`, lang: 'bash' },
  { code: `Busca no nome, na descricao e nas tags.`, lang: 'text' },
  { code: `dataforge search cpf
dataforge search ""                                  # lista tudo`, lang: 'bash' },
  {"p": "Veja: `add`."},
  {"h3": "pack"},
  {"p": "Empacota este projeto para publicar. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge pack`, lang: 'bash' },
  { code: `Gera dist/<nome>-<versao>.tar.gz com o sha256.
Reprodutivel: mesma fonte, mesmo hash.`, lang: 'text' },
  {"p": "Veja: `publish`."},
  {"h3": "publish"},
  {"p": "Publica o pacote num registro. Ver [a página](/docs/cli/pacotes)."},
  { code: `dataforge publish --registry=<pasta>`, lang: 'bash' },
  { code: `Dois destinos, e eles resolvem problemas diferentes:

  --registry=<pasta>  um indice estatico, para um registro
                      interno de empresa — espera um PR
  --remoto            o registro da comunidade, por chamada
                      autenticada, e o pacote entra na fila
                      de revisao

O tarball NAO sobe: o que se envia e o endereco dele e o
sha256. Hospedar binario exige cota, expiracao e politica de
abuso; um release do GitHub ja faz isso melhor, e o hash e o
que torna a origem irrelevante.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--registry=<pasta>`", "um indice estatico numa pasta"], ["`--remoto`", "o registro da comunidade, com revisao"], ["`--tarball=<url>`", "o endereco do tarball ja hospedado"]]}},
  { code: `dataforge publish --registry=../registro             # interno
dataforge publish --remoto                           # a comunidade`, lang: 'bash' },
  {"p": "Veja: `pack`, `login`."},
  {"h3": "versions"},
  {"p": "As versoes instaladas, a ativa e a que o projeto exige. Ver [a página](/docs/cli/versoes)."},
  { code: `dataforge versions`, lang: 'bash' },
  { code: `Cada versao mora numa venv propria em
'~/.dataforge/versoes/<versao>'. A escolha global fica no
arquivo 'atual'; a do projeto, no campo 'dataforge' do
forge.toml — o mesmo que o manifesto ja lia.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--json`", "o resultado como dado"]]}},
  {"p": "Também: `versoes`. Veja: `use`, `upgrade`."},
  {"h3": "use"},
  {"p": "Fixa a versao do DataForge deste projeto. Ver [a página](/docs/cli/versoes)."},
  { code: `dataforge use <versao> [--global]`, lang: 'bash' },
  { code: `Sem '--global', escreve 'dataforge = "<versao>"' na secao
[project] do forge.toml — e o arquivo e reescrito LINHA A
LINHA, para nao apagar comentarios nem reordenar campos.

E o pino VALE: 'dataforge run' num projeto que exige outra
versao entrega a execucao a ela, quando ela esta instalada.
Quando nao esta, recusa e diz como instalar — rodar na
versao errada e o que o pino existe para impedir.

'DATAFORGE_SEM_TROCA=1' desliga a troca.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--global`", "escolhe para a maquina, e nao para o projeto"]]}},
  { code: `dataforge use 1.0.0                                  # fixa no projeto
dataforge use 1.0.0 --global                         # fixa para a maquina`, lang: 'bash' },
  {"p": "Também: `switch`. Veja: `versions`, `upgrade`."},
  {"h3": "upgrade"},
  {"p": "Instala uma versao AO LADO da atual. Ver [a página](/docs/cli/versoes)."},
  { code: `dataforge upgrade [versao]`, lang: 'bash' },
  { code: `Sem versao, pergunta ao site qual e a mais nova. A instalacao
e uma venv propria: a versao que ja roda nao e tocada, e por
isso um upgrade que falha no meio nao deixa a maquina sem
DataForge.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--check`", "mostra os passos sem executar nenhum"], ["`--force`", "reinstala mesmo que ja exista"]]}},
  { code: `dataforge upgrade                                    # a mais nova publicada
dataforge upgrade 1.0.0 --check                      # so diz o que faria`, lang: 'bash' },
  {"p": "Veja: `versions`, `use`."},
  {"h3": "workspace"},
  {"p": "Todos os pacotes da arvore, e os conflitos de faixa. Ver [a página](/docs/cli/workspace)."},
  { code: `dataforge workspace [pasta]`, lang: 'bash' },
  { code: `Cada pacote tem o seu forge.toml, e a unica forma de saber se
dois deles pedem faixas incompativeis do mesmo terceiro era
instalar os dois e esperar o erro — que aparece na maquina de
quem consome.

Ele LE e relata: nao instala nada. Sai com 2 quando ha
conflito, porque instalar duas copias em versoes diferentes
gera bug irreproduzivel.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--json`", "o resultado como dado"]]}},
  { code: `dataforge workspace                                  # a arvore daqui para baixo
dataforge workspace --json                           # para o CI ler`, lang: 'bash' },
  {"p": "Também: `ws`. Veja: `install`, `tree`."},
  {"h3": "login"},
  {"p": "Guarda o token de publicacao no registro da comunidade. Ver [a página](/docs/pacotes/publicar)."},
  { code: `dataforge login [token]`, lang: 'bash' },
  { code: `O token e criado no painel do site e aparece UMA vez. Ele
fica em '~/.dataforge/credenciais.json', com modo 600: num
arquivo do projeto ele acabaria commitado, que e a forma
mais comum de vazar credencial de registro que existe.

O 'login' CONFERE o token antes de gravar — sem isso o erro
so apareceria no primeiro 'publish', longe da causa.`, lang: 'text' },
  { code: `dataforge login                                      # pede o token e confere
dataforge login df_pat_…                             # sem perguntar`, lang: 'bash' },
  {"p": "Veja: `publish`, `whoami`, `logout`."},
  {"h3": "logout"},
  {"p": "Esquece o token guardado. Ver [a página](/docs/pacotes/publicar)."},
  { code: `dataforge logout`, lang: 'bash' },
  {"p": "Veja: `login`."},
  {"h3": "whoami"},
  {"p": "Diz de quem e o token guardado, e o que ele alcanca. Ver [a página](/docs/pacotes/publicar)."},
  { code: `dataforge whoami`, lang: 'bash' },
  {"p": "Veja: `login`."},
  {"h2": "Analise"},
  {"h3": "stats"},
  {"p": "O tamanho e a forma do codigo. Ver [a página](/docs/cli/analise)."},
  { code: `dataforge stats [alvo]`, lang: 'bash' },
  { code: `Nao e 'linhas de codigo' como metrica de produtividade — e o
inventario: quantas acoes, quantos blueprints, o arquivo mais
longo, a acao mais longa.

Serve para achar o que cresceu demais sem ninguem notar. Uma
acao acima de 50 linhas costuma fazer mais de uma coisa.`, lang: 'text' },
  { code: `dataforge stats                                      # o projeto inteiro
dataforge stats src/                                 # so uma pasta`, lang: 'bash' },
  {"p": "Veja: `lint`, `check`."},
  {"h3": "profile"},
  {"p": "Onde o tempo foi gasto, acao por acao. Ver [a página](/docs/cli/profile)."},
  { code: `dataforge profile <arquivo>`, lang: 'bash' },
  { code: `Um 'bench' diz que esta lento; um 'profile' diz ONDE.
Mede cada acao: quantas chamadas, tempo acumulado e por
chamada, ordenado pelo que mais custa.

Meca antes de otimizar. A acao que voce acha que e o gargalo
quase nunca e.`, lang: 'text' },
  { code: `dataforge profile src/main.df`, lang: 'bash' },
  {"p": "Veja: `bench`, `run`."},
  {"h3": "fix"},
  {"p": "Formata e aponta o que precisa de voce. Ver [a página](/docs/cli/profile)."},
  { code: `dataforge fix [alvo]`, lang: 'bash' },
  { code: `Roda o formatador e, em seguida, o linter — arrumando o que da
para arrumar sozinho e listando o resto.

O que exige julgamento nao e 'consertado' automaticamente:
uma ferramenta que muda o codigo precisa ser previsivel.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--dry-run`", "mostra o que faria, sem escrever"]]}},
  { code: `dataforge fix                                        # o projeto inteiro
dataforge fix --dry-run                              # so o relatorio`, lang: 'bash' },
  {"p": "Veja: `fmt`, `lint`."},
  {"h2": "Ambiente"},
  {"h3": "devops"},
  {"p": "Gera os artefatos que levam o projeto ao ar. Ver [a página](/docs/devops)."},
  { code: `dataforge devops <init|docker|ci|k8s|doctor|…>`, lang: 'bash' },
  { code: `Dockerfile, compose, pipeline de CI, manifestos do
Kubernetes, chart do Helm, nginx, Prometheus, SBOM.

O que ele gera nao e esboco: e o que se poria em
producao — usuario sem privilegio, limite de recurso,
sonda de saude e segredo fora do repositorio.

Os artefatos saem conforme o que o projeto ADOTA: quem
nao usa banco nao ganha um Postgres no compose.

Arquivo que ja existe e PULADO, nao sobrescrito.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--forcar`", "sobrescreve (o anterior vai para .anterior)"], ["`--seco`", "mostra o que faria, sem escrever"], ["`--registro=<host>`", "o registro das imagens"], ["`--dominio=<host>`", "o dominio, no ingress e no nginx"], ["`--em=<pasta>`", "o projeto (padrao: a pasta atual)"]]}},
  { code: `dataforge devops init                                # tudo o que faz sentido
dataforge devops docker                              # Dockerfile e compose
dataforge devops k8s --dominio=app.exemplo.br
dataforge devops doctor                              # o que falta para subir
dataforge devops secrets                             # o que nao pode ir ao repo`, lang: 'bash' },
  {"p": "Também: `ops`. Veja: `vitrine`, `new`, `pack`."},
  {"h3": "telegram"},
  {"p": "Cria, roda e publica um bot de Telegram. Ver [a página](/docs/telegram)."},
  { code: `dataforge telegram <new|run|doctor|webhook|off>`, lang: 'bash' },
  { code: `O token vem de $TELEGRAM_TOKEN — nunca do código. 'doctor' pergunta ao próprio Telegram por que o bot está calado: token, webhook brigando com o polling, privacidade de grupo ligada.`, lang: 'text' },
  { code: `dataforge telegram new meubot                        # cria o projeto
dataforge telegram doctor                            # por que ele não responde
dataforge telegram run                               # sobe em long polling
dataforge telegram webhook https://x.dev             # registra o webhook`, lang: 'bash' },
  {"p": "Também: `bot`. Veja: `vitrine`, `devops`, `new`."},
  {"h3": "iot"},
  {"p": "Arduino e ESP32: a placa, do terminal."},
  { code: `dataforge iot <portas|doctor|monitorar|sketch|carregar|piscar>`, lang: 'bash' },
  { code: `Uma placa que nao responde tambem nao da erro: a porta abre e nada chega. 'doctor' confere as causas na ordem em que elas acontecem — cabo so de energia, driver ausente, StandardFirmata nao gravado, velocidade errada. 'carregar' chama o arduino-cli: compilar C++ para AVR e gravar pelo bootloader e o que ele faz, e bem.`, lang: 'text' },
  { code: `dataforge iot portas                                 # as portas que existem agora
dataforge iot doctor                                 # por que a placa nao responde
dataforge iot piscar                                 # o LED 13, por Firmata
dataforge iot sketch pisca --em=/tmp/p               # escreve o .ino
dataforge iot monitorar --velocidade=9600            # o monitor serial`, lang: 'bash' },
  {"p": "Também: `arduino`. Veja: `telegram`, `vitrine`, `devops`."},
  {"h3": "desktop"},
  {"p": "Aplicacao de mesa nativa, com zero dependencia."},
  { code: `dataforge desktop <novo|rodar|empacotar|doctor>`, lang: 'bash' },
  { code: `O Tk vem na biblioteca padrao do Python, e e a unica forma
de desenhar uma janela nativa nos tres sistemas sem trazer
nada de fora. A arvore e separada do desenho, como na
Vitrine: por isso uma tela se testa SEM display nenhum.

'empacotar' chama o PyInstaller — empacotar um
interpretador Python e um problema resolvido.`, lang: 'text' },
  { code: `dataforge desktop novo caixa                         # um esqueleto que ja roda
dataforge desktop rodar src/main.df                  # abre a janela
dataforge desktop empacotar src/main.df --nome=Caixa # .app, .exe ou binario
dataforge desktop doctor                             # o que falta para empacotar`, lang: 'bash' },
  {"p": "Também: `janela`. Veja: `mobile`, `vitrine`, `devops`."},
  {"h3": "mobile"},
  {"p": "Android: o que funciona, e o que nao existe."},
  { code: `dataforge mobile <pwa|doctor>`, lang: 'bash' },
  { code: `Nao ha APK — empacotar o interpretador num aplicativo
Android exigiria python-for-android ou Chaquopy, e as duas
trazem uma cadeia de dependencias que a linguagem nao tem.

O que funciona e o PWA: uma aplicacao Vitrine servida por
HTTPS que o Android instala na tela inicial, abre em tela
cheia e roda sem navegador visivel.`, lang: 'text' },
  { code: `dataforge mobile pwa --nome='Meu App'                # manifesto, icone e service worker
dataforge mobile doctor                              # o que existe e o que NAO existe`, lang: 'bash' },
  {"p": "Também: `android`. Veja: `desktop`, `vitrine`."},
  {"h3": "vitrine"},
  {"p": "Sobe um painel feito com Arcane.Vitrine. Ver [a página](/docs/vitrine)."},
  { code: `dataforge vitrine <run|dev|doctor|new>`, lang: 'bash' },
  { code: `Um programa de cima para baixo vira uma pagina web. 'dev'
recarrega ao salvar; 'doctor' diz por que ela nao sobe.

Nao ha 'build': nao existe bundler nem transpilacao — o
que roda e o proprio .df.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--porta=<n>`", "a porta (padrao 8501)"], ["`--host=<ip>`", "o endereco (padrao 127.0.0.1)"]]}},
  { code: `dataforge vitrine dev                                # sobe recarregando ao salvar
dataforge vitrine doctor                             # o que falta para subir
dataforge vitrine new meupainel                      # cria o projeto`, lang: 'bash' },
  {"p": "Veja: `new`, `run`."},
  {"h3": "editor"},
  {"p": "Instala a coloracao de sintaxe no VS Code. Ver [a página](/docs/cli/editor)."},
  { code: `dataforge editor [status|remove]`, lang: 'bash' },
  { code: `Copia a extensao para o VS Code, Insiders, Cursor, VSCodium e
Windsurf — todos os que encontrar. Depois disso, todo arquivo
.df abre com as palavras reservadas coloridas, 23 snippets e a
indentacao de 4 espacos que a linguagem exige.

O instalador ja faz isso; use este comando para reinstalar
depois de atualizar o DataForge ou de instalar um editor novo.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`status`", "mostra onde esta instalada"], ["`remove`", "desinstala de todos os editores"]]}},
  { code: `dataforge editor                                     # instala em todos
dataforge editor status                              # so confere`, lang: 'bash' },
  {"p": "Veja: `version`, `lsp`."},
  {"h3": "debug"},
  {"p": "Roda parando onde voce mandar. Ver [a página](/docs/cli/debug)."},
  { code: `dataforge debug <arquivo.df>`, lang: 'bash' },
  { code: `Para, mostra o que esta valendo e deixa andar de uma
instrucao por vez. Dentro dele: 'p' passo, 'n' proximo,
'f' sai da acao, 'c' continua, 'vars' lista o escopo,
'pilha' mostra quem chamou quem, e qualquer expressao e
avaliada no quadro onde voce parou.

Sem '--parar', ele para na primeira instrucao.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--parar=N,M`", "paradas ja nas linhas N e M"], ["`--vigiar=EXPR`", "para quando o valor de EXPR mudar (repetivel)"], ["`--vigiar-leitura=NOME`", "para quando NOME for LIDO — 'quem esta consultando isto?'"]]}},
  { code: `dataforge debug conta.df                             # para no comeco
dataforge debug conta.df --parar=42                  # so na linha 42
dataforge debug conta.df --vigiar=saldo              # para quando 'saldo' mudar
dataforge debug conta.df --vigiar-leitura=saldo      # para quando 'saldo' for lido`, lang: 'bash' },
  {"p": "Veja: `run`, `check`."},
  {"h3": "dap"},
  {"p": "Adaptador de depuracao para o editor. Ver [a página](/docs/cli/debug)."},
  { code: `dataforge dap`, lang: 'bash' },
  { code: `Fala o Debug Adapter Protocol por stdin/stdout. E o que poe
os breakpoints na margem do editor, a pilha de chamadas no
painel, as variaveis em arvore e o console de avaliacao —
com 'entrar', 'passar por cima' e 'sair da acao'.

Voce nao o roda a mao: a extensao do VS Code o inicia
sozinha ao apertar F5. Este comando existe para outros
editores que perguntam qual adaptador iniciar.

Para depurar no terminal — por ssh, sem interface
grafica — use 'dataforge debug'.`, lang: 'text' },
  { code: `dataforge dap                                        # o que o editor executa`, lang: 'bash' },
  {"p": "Veja: `debug`, `lsp`."},
  {"h3": "lsp"},
  {"p": "Servidor de linguagem para o editor. Ver [a página](/docs/cli/debug)."},
  { code: `dataforge lsp`, lang: 'bash' },
  { code: `Fala o Language Server Protocol por stdin/stdout. E o que da
ao editor autocompletar sensivel a contexto, erro sublinhado
enquanto se digita, ir-para-definicao, renomear com seguranca,
o esquema do arquivo e ajuda de assinatura.

Voce nao o roda a mao: a extensao do VS Code o inicia
sozinha. Este comando existe para outros editores — Neovim,
Helix, Emacs — que perguntam qual comando iniciar.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--log=ARQUIVO`", "grava o que acontece, para depurar"]]}},
  { code: `dataforge lsp                                        # o que o editor executa
dataforge lsp --log=/tmp/lsp.log                     # com registro`, lang: 'bash' },
  {"p": "Veja: `editor`, `check`."},
  {"h2": "Diagnostico"},
  {"h3": "explain"},
  {"p": "Explica um codigo de erro. Ver [a página](/docs/cli/explain)."},
  { code: `dataforge explain <codigo>`, lang: 'bash' },
  { code: `Todo erro do DataForge tem um codigo estavel, como DF0601.
Este comando diz o que ele significa e como resolver.`, lang: 'text' },
  { code: `dataforge explain DF0601
dataforge explain 0401                               # o prefixo e opcional
dataforge explain KeyError                           # o nome da classe tambem`, lang: 'bash' },
  {"p": "Veja: `check`, `erros`."},
  {"h3": "crucible"},
  {"p": "Roda as suites do Crucible, o framework de testes. Ver [a página](/docs/cli/crucible)."},
  { code: `dataforge crucible [alvo]`, lang: 'bash' },
  { code: `Descobre os arquivos, carrega as suites e roda tudo junto.
Sem alvo, procura em tests/, testes/ e *_crucible.df.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--verbose, -v`", "mostra tambem o que passou"], ["`--filtro=<t>`", "so os trials cujo nome contem <t>"], ["`--tag=<a,b>`", "so os marcados com estas tags"], ["`--sem-tag=<a>`", "pula os marcados com esta tag"], ["`--aleatorio`", "embaralha a ordem; ordem oculta aparece"], ["`--semente=<n>`", "repete um embaralhamento especifico"], ["`--repetir=<n>`", "roda cada trial n vezes"], ["`--prazo=<ms>`", "falha o que passar deste tempo"], ["`--fail-fast`", "para na primeira falha"], ["`--formato=<f>`", "texto \\| junit \\| json \\| tap"], ["`--out=<arq>`", "escreve o relatorio num arquivo"], ["`--matchers`", "lista tudo o que se pode cobrar"]]}},
  { code: `dataforge crucible                                   # roda tudo
dataforge crucible --tag=rapido                      # so os rapidos
dataforge crucible --formato=junit --out=r.xml       # para o CI`, lang: 'bash' },
  {"p": "Também: `cr`. Veja: `test`, `bench`."},
  {"h3": "big-o"},
  {"p": "Calcula a complexidade de cada acao, sem rodar o codigo. Ver [a página](/docs/cli/analise)."},
  { code: `dataforge big-o [alvo]`, lang: 'bash' },
  { code: `Le a arvore e conta estrutura: lacos aninhados, recursao,
e o custo das funcoes embutidas que aparecem. Diz a classe
E o porque — 'O(n^2)' sozinho nao ajuda a melhorar nada.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--medir`", "roda e compara com a classe MEDIDA"], ["`--verbose, -v`", "mostra o porque e o que fazer"], ["`--escala`", "a tabela do que cada classe custa"], ["`--json`", "saida estruturada, para o editor"], ["`--strict`", "sai com erro se algo passar de O(n log n)"]]}},
  { code: `dataforge big-o src/ -v
dataforge big-o --escala                             # a tabela de referencia`, lang: 'bash' },
  {"p": "Também: `bigo`, `complexidade`. Veja: `profile`, `bench`."},
  {"h3": "oop"},
  {"p": "Metricas de orientacao a objeto e os cheiros de SOLID. Ver [a página](/docs/cli/analise)."},
  { code: `dataforge oop [alvo]`, lang: 'bash' },
  { code: `Mede cada blueprint sem rodar: WMC, DIT, NOC, CBO, RFC, LCOM,
fan-in, fan-out, instabilidade e indice de manutenibilidade.

Cada limite ultrapassado vira um cheiro com o principio que
ele fere e o que fazer: god blueprint (SRP), contrato gordo
(ISP), switch de tipo (OCP), sobrescrita que recusa (LSP),
dependencia concreta (DIP), heranca funda, baixa coesao,
modelo anemico, inveja de recurso e dependencia circular.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--diagrama`", "o diagrama de classes em Mermaid"], ["`--hierarquia`", "a arvore de heranca"], ["`--json`", "saida estruturada"], ["`--strict`", "sai com erro se houver cheiro"]]}},
  { code: `dataforge oop src/                                   # metricas e cheiros
dataforge oop src/ --diagrama > classes.mmd          # o diagrama para o README`, lang: 'bash' },
  {"p": "Também: `metricas-oop`. Veja: `big-o`, `stats`, `check`."},
  {"h3": "custo"},
  {"p": "Mostra o que cada 'adopt' traz junto. Ver [a página](/docs/cli/analise)."},
  { code: `dataforge custo [alvo]`, lang: 'bash' },
  { code: `Uma linha de import nao parece cara. Um modulo de 200
simbolos entra inteiro no processo.`, lang: 'text' },
  { code: `dataforge custo src/`, lang: 'bash' },
  {"p": "Também: `cost`. Veja: `big-o`."},
  {"h3": "gramatica"},
  {"p": "A gramatica da linguagem, com exemplos conferidos."},
  { code: `dataforge gramatica [grupo|producao]`, lang: 'bash' },
  { code: `Cada producao traz o EBNF, um exemplo e a nota do que mais
engana. Os exemplos passam pelo lexer e pelo parser de verdade
a cada execucao da suite — a gramatica nao tem como descrever
uma sintaxe que o parser ja nao aceita.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--ebnf`", "so o EBNF (de um grupo, ou da gramatica inteira)"], ["`--precedencia`", "a tabela, da mais fraca para a mais forte"], ["`--json`", "a mesma coisa como dado"]]}},
  { code: `dataforge gramatica                                  # os grupos
dataforge gramatica pipeline                         # uma producao
dataforge gramatica expressoes --ebnf                # o EBNF de um grupo
dataforge gramatica --precedencia                    # quem liga mais forte`, lang: 'bash' },
  {"p": "Também: `grammar`. Veja: `palavras`, `tokens`, `ast`."},
  {"h3": "palavras"},
  {"p": "Lista as palavras da linguagem, com um exemplo de cada. Ver [a página](/docs/referencia/palavras-reservadas)."},
  { code: `dataforge palavras [termo]`, lang: 'bash' },
  { code: `Sao 113: as 81 reservadas mais as contextuais. Cada uma traz
o que faz e um exemplo que RODA — eles saem de
'exemplos_palavras.py', e ha teste executando todos.

Com termo, procura no nome e na descricao.`, lang: 'text' },
  { code: `dataforge palavras                                   # todas
dataforge palavras cycle                             # so o que fala de laco`, lang: 'bash' },
  {"p": "Também: `keywords`. Veja: `erros`, `explain`."},
  {"h3": "erros"},
  {"p": "Lista o catalogo de erros da linguagem. Ver [a página](/docs/referencia/erros)."},
  { code: `dataforge erros [termo]`, lang: 'bash' },
  { code: `Sao 219 codigos em 19 familias. Sem termo, lista tudo
agrupado; com termo, procura no titulo e na explicacao.`, lang: 'text' },
  { code: `dataforge erros                                      # o catalogo inteiro
dataforge erros banco                                # so o que fala de banco`, lang: 'bash' },
  {"p": "Também: `errors`. Veja: `explain`."},
  {"h3": "doc"},
  {"p": "Gera documentacao Markdown a partir dos comentarios. Ver [a página](/docs/cli/doc)."},
  { code: `dataforge doc [alvo]`, lang: 'bash' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--out=<arquivo>`", "escreve num arquivo"]]}},
  { code: `dataforge doc src/ --out=doc/API.md`, lang: 'bash' },
  {"h3": "deps"},
  {"p": "Mostra o grafo de imports do codigo. Ver [a página](/docs/cli/analise)."},
  { code: `dataforge deps [alvo]`, lang: 'bash' },
  { code: `Quem adota quem, e avisa sobre ciclos.`, lang: 'text' },
  {"p": "Veja: `tree`."},
  {"h3": "tokens"},
  {"p": "Mostra o fluxo de tokens (lexer). Ver [a página](/docs/cli/internos)."},
  { code: `dataforge tokens <arquivo>`, lang: 'bash' },
  {"p": "Veja: `ast`."},
  {"h3": "ast"},
  {"p": "Mostra a arvore sintatica (parser). Ver [a página](/docs/cli/internos)."},
  { code: `dataforge ast <arquivo>`, lang: 'bash' },
  {"p": "Veja: `tokens`, `ir`."},
  {"h3": "abi"},
  {"p": "Compara duas versoes e diz se a nova QUEBRA a anterior. Ver [a página](/docs/cli/abi)."},
  { code: `dataforge abi <antes.df> <depois.df>`, lang: 'bash' },
  { code: `A superficie de um modulo e o contrato dele: o que ele
exporta, com que aridade e com que tipos. Muda-la quebra
quem depende — em silencio, no dia da atualizacao.

Sai com 1 quando ha quebra, para reprovar no CI. O veredito
e o bump de semver que a mudanca EXIGE:

  maior     alguma coisa quebrou
  menor     so acrescimos compativeis
  correcao  a superficie nao mudou`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--json`", "o resultado como dado, para o CI ler"], ["`--estrito`", "trata como quebra o que a superficie nao decide sozinha (campo novo num record)"]]}},
  { code: `dataforge abi v1/lib.df v2/lib.df                    # o que mudou
dataforge abi a.df b.df --json                       # como dado`, lang: 'bash' },
  {"p": "Veja: `alvo`, `check`."},
  {"h3": "alvo"},
  {"p": "Este programa roda no navegador? no WASI? numa funcao?. Ver [a página](/docs/cli/abi)."},
  { code: `dataforge alvo <arquivo> [--alvo=<nome>]`, lang: 'bash' },
  { code: `Le os 'adopt' e cruza com o que cada ambiente suporta.

  servidor   maquina com sistema operacional completo
  cli        programa de linha de comando
  navegador  CPython em WebAssembly, dentro de uma aba
  wasi       WebAssembly fora do navegador
  funcao     serverless: efemero, e com o disco so de leitura
  embarcado  microcontrolador

A leitura e ESTATICA: um 'roda' quer dizer 'nao achei
impedimento por esta via', e nao 'vai funcionar'.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--alvo=<nome>`", "confere um alvo, e sai com 1 se nao roda"], ["`--json`", "o resultado como dado"]]}},
  { code: `dataforge alvo app.df                                # a tabela de todos
dataforge alvo app.df --alvo=navegador               # um so`, lang: 'bash' },
  {"p": "Veja: `abi`, `check`."},
  {"h3": "percurso"},
  {"p": "Onde o tempo vai: as fases em ordem, medidas. Ver [a página](/docs/cli/internos)."},
  { code: `dataforge percurso <arquivo>`, lang: 'bash' },
  { code: `O 'ir' mostra cada fase; o 'percurso' mostra TODAS em
ordem, com o que cada uma produziu e quanto levou — que e
a pergunta quando um arquivo demora a abrir no editor.

Ele NAO executa o programa: executar e o que o programa
faz, e um arquivo de verdade abre soquete e escreve em
disco. A ultima fase e nomeada e marcada como nao
percorrida, para que a ausencia tenha lugar.

Cada fase e medida UMA vez, com os imports aquecidos:
serve para comparar as fases entre si, e nao maquinas.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--json`", "o resultado como dado"], ["`--desenho`", "o caminho real desenhado"], ["`--sem-tipos`", "pula a analise estatica, a fase mais cara num projeto com muitos 'adopt'"]]}},
  { code: `dataforge percurso app.df                            # a tabela de fases
dataforge percurso app.df --desenho                  # o caminho desenhado, com as ausencias`, lang: 'bash' },
  {"p": "Veja: `ir`, `ecossistema`."},
  {"h3": "ecossistema"},
  {"p": "O inventario da implementacao, conferido contra o disco. Ver [a página](/docs/ecossistema/componentes)."},
  { code: `dataforge ecossistema`, lang: 'bash' },
  { code: `O desenho do ecossistema com uma marca por componente:

  [+]  existe, com esse papel
  [~]  equivale: outra peca responde a mesma pergunta
  [-]  nao existe, e o porque esta escrito

Ele CONFERE as duas direcoes: todo caminho citado existe
no disco, e todo modulo do nucleo aparece em algum
componente. Sem a segunda, um modulo novo nasce fora do
mapa e o inventario fica incompleto em silencio.

Sai com 1 quando o mapa e o disco discordam.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--json`", "o inventario como dado"], ["`--ausencias`", "so o que nao existe e o que esta no lugar"]]}},
  { code: `dataforge ecossistema                                # o inventario inteiro
dataforge ecossistema --ausencias                    # so o que nao existe, com o motivo`, lang: 'bash' },
  {"p": "Veja: `principios`, `percurso`."},
  {"h3": "principios"},
  {"p": "Os dez principios de design, com a prova de cada um. Ver [a página](/docs/ecossistema/principios)."},
  { code: `dataforge principios`, lang: 'bash' },
  { code: `Cada principio carrega a frase do documento, o que ela
significa AQUI, o veredito e uma prova que RODA — duas
delas chamam o analisador e uma abre um interpretador.

O veredito nao e dez de dez de proposito: ha parciais e
ha um que nao se aplica, com o motivo.

E as TENSOES: onde dois principios se contradizem, qual
venceu, o custo aceito e o arquivo onde isso mora. Uma
lista de principios diz o que se quer; a tensao diz o que
se escolheu quando nao era possivel querer as duas coisas.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--json`", "o resultado como dado"], ["`--tensoes`", "so as tensoes"]]}},
  { code: `dataforge principios                                 # os dez, medidos
dataforge principios --tensoes                       # so onde dois se contradizem`, lang: 'bash' },
  {"p": "Veja: `ecossistema`, `percurso`."},
  {"h3": "ir"},
  {"p": "Mostra o caminho inteiro: HIR, MIR, LIR e as analises. Ver [a página](/docs/cli/internos)."},
  { code: `dataforge ir <arquivo> [--fase=…]`, lang: 'bash' },
  { code: `As representacoes do meio, que 'tokens' e 'ast' nao mostram.

  hir       a arvore depois do acucar, e quanto dele o arquivo usa
  mir       o grafo de fluxo: bloco basico, aresta, laco, tratador
  analises  alcance, constantes, escapatoria e nome nao definido
  ssa       uma definicao por nome, com os nos phi das juncoes
  otimizado o que os passes conseguem tirar deste arquivo
  lir       o que o compilador de fechamentos compilou, e o que recuou

Nao ha fase de codigo de maquina: o backend e compilador.py, e
o 'lir' e onde isso fica visivel.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--fase=<nome>`", "tokens, ast, hir, mir, analises, ssa, otimizado, lir ou tudo"], ["`--acao=<nome>`", "so o corpo desta acao, no 'mir'"], ["`--json`", "a mesma coisa como dado"]]}},
  { code: `dataforge ir app.df                                  # o caminho inteiro
dataforge ir app.df --fase=mir                       # so o grafo de fluxo
dataforge ir app.df --fase=lir                       # o que compilou`, lang: 'bash' },
  {"p": "Veja: `ast`, `tokens`, `check`."},
  {"h3": "completar"},
  {"p": "Gera o autocompletar do terminal. Ver [a página](/docs/cli/completar)."},
  { code: `dataforge completar <bash|zsh|fish>`, lang: 'bash' },
  { code: `O script sai do proprio catalogo de comandos: um comando novo
aparece no Tab no dia em que entra aqui. As opcoes sao por
comando, e depois de 'run', 'check' ou 'fmt' o Tab completa
arquivo. O script nao chama o dataforge a cada tecla.`, lang: 'text' },
  { code: `dataforge completar bash > ~/.local/share/bash-completion/completions/dataforge # bash
dataforge completar zsh > "\${fpath[1]}/_dataforge"   # zsh
dataforge completar fish > ~/.config/fish/completions/dataforge.fish # fish`, lang: 'bash' },
  {"p": "Também: `completion`. Veja: `help`, `editor`."},
  {"h3": "clean"},
  {"p": "Limpa caches e artefatos de build. Ver [a página](/docs/cli/cache)."},
  { code: `dataforge clean`, lang: 'bash' },
  { code: `Remove dist/, __pycache__ e o cache de pacotes baixados.`, lang: 'text' },
  {"table": {"head": ["Opção", "Efeito"], "rows": [["`--all`", "inclui forge_modules/ e o cache global"]]}},
  {"h3": "version"},
  {"p": "Mostra a versao. Ver [a página](/docs/cli/scripts)."},
  { code: `dataforge version`, lang: 'bash' },
  {"p": "Também: `--version`, `-V`."},
  {"h3": "help"},
  {"p": "Mostra esta ajuda, ou a de um comando. Ver [a página](/docs/cli/scripts)."},
  { code: `dataforge help [comando]`, lang: 'bash' },
  { code: `dataforge help                                       # visao geral
dataforge help add                                   # so o 'add'`, lang: 'bash' },
  {"p": "Também: `--help`, `-h`."},
];

const headings = [{ id: 'projeto', text: "Projeto", level: 2 as const }, { id: 'init', text: "init", level: 3 as const }, { id: 'api', text: "api", level: 3 as const }, { id: 'converter', text: "converter", level: 3 as const }, { id: 'new', text: "new", level: 3 as const }, { id: 'info', text: "info", level: 3 as const }, { id: 'executar', text: "Executar", level: 2 as const }, { id: 'run', text: "run", level: 3 as const }, { id: 'eval', text: "eval", level: 3 as const }, { id: 'watch', text: "watch", level: 3 as const }, { id: 'repl', text: "repl", level: 3 as const }, { id: 'qualidade', text: "Qualidade", level: 2 as const }, { id: 'check', text: "check", level: 3 as const }, { id: 'test', text: "test", level: 3 as const }, { id: 'fmt', text: "fmt", level: 3 as const }, { id: 'lint', text: "lint", level: 3 as const }, { id: 'seguranca', text: "seguranca", level: 3 as const }, { id: 'bench', text: "bench", level: 3 as const }, { id: 'pacotes', text: "Pacotes", level: 2 as const }, { id: 'add', text: "add", level: 3 as const }, { id: 'remove', text: "remove", level: 3 as const }, { id: 'install', text: "install", level: 3 as const }, { id: 'update', text: "update", level: 3 as const }, { id: 'list', text: "list", level: 3 as const }, { id: 'tree', text: "tree", level: 3 as const }, { id: 'why', text: "why", level: 3 as const }, { id: 'outdated', text: "outdated", level: 3 as const }, { id: 'search', text: "search", level: 3 as const }, { id: 'pack', text: "pack", level: 3 as const }, { id: 'publish', text: "publish", level: 3 as const }, { id: 'versions', text: "versions", level: 3 as const }, { id: 'use', text: "use", level: 3 as const }, { id: 'upgrade', text: "upgrade", level: 3 as const }, { id: 'workspace', text: "workspace", level: 3 as const }, { id: 'login', text: "login", level: 3 as const }, { id: 'logout', text: "logout", level: 3 as const }, { id: 'whoami', text: "whoami", level: 3 as const }, { id: 'analise', text: "Analise", level: 2 as const }, { id: 'stats', text: "stats", level: 3 as const }, { id: 'profile', text: "profile", level: 3 as const }, { id: 'fix', text: "fix", level: 3 as const }, { id: 'ambiente', text: "Ambiente", level: 2 as const }, { id: 'devops', text: "devops", level: 3 as const }, { id: 'telegram', text: "telegram", level: 3 as const }, { id: 'iot', text: "iot", level: 3 as const }, { id: 'desktop', text: "desktop", level: 3 as const }, { id: 'mobile', text: "mobile", level: 3 as const }, { id: 'vitrine', text: "vitrine", level: 3 as const }, { id: 'editor', text: "editor", level: 3 as const }, { id: 'debug', text: "debug", level: 3 as const }, { id: 'dap', text: "dap", level: 3 as const }, { id: 'lsp', text: "lsp", level: 3 as const }, { id: 'diagnostico', text: "Diagnostico", level: 2 as const }, { id: 'explain', text: "explain", level: 3 as const }, { id: 'crucible', text: "crucible", level: 3 as const }, { id: 'big-o', text: "big-o", level: 3 as const }, { id: 'oop', text: "oop", level: 3 as const }, { id: 'custo', text: "custo", level: 3 as const }, { id: 'gramatica', text: "gramatica", level: 3 as const }, { id: 'palavras', text: "palavras", level: 3 as const }, { id: 'erros', text: "erros", level: 3 as const }, { id: 'doc', text: "doc", level: 3 as const }, { id: 'deps', text: "deps", level: 3 as const }, { id: 'tokens', text: "tokens", level: 3 as const }, { id: 'ast', text: "ast", level: 3 as const }, { id: 'abi', text: "abi", level: 3 as const }, { id: 'alvo', text: "alvo", level: 3 as const }, { id: 'percurso', text: "percurso", level: 3 as const }, { id: 'ecossistema', text: "ecossistema", level: 3 as const }, { id: 'principios', text: "principios", level: 3 as const }, { id: 'ir', text: "ir", level: 3 as const }, { id: 'completar', text: "completar", level: 3 as const }, { id: 'clean', text: "clean", level: 3 as const }, { id: 'version', text: "version", level: 3 as const }, { id: 'help', text: "help", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Referência da CLI"}
      description={"Todo comando, com uso, opções, exemplos e apelidos — gerada do catálogo."}
      href={"/docs/cli/referencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
