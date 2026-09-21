// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Princípios",
  description: "CIA, autenticação, autorização, responsabilização, não-repúdio, privilégio mínimo, defesa em profundidade, zero trust, seguro por desenho e por padrão.",
};

const blocos: Bloco[] = [
  {"p": "Os princípios existem porque controles isolados envelhecem e as perguntas não. Quando um requisito novo aparece, é a eles que se volta para decidir."},
  {"h2": "Confidencialidade, integridade, disponibilidade"},
  {"p": "A **tríade CIA** é o enquadramento mais antigo e o mais útil: todo controle serve a pelo menos um dos três, e um controle que não serve a nenhum é cerimônia."},
  {"table": {"head": ["", "Falha típica", "Na prática, aqui"], "rows": [["**Confidencialidade**", "vazamento, log com dado pessoal, chave no repositório", "cifrar em repouso, `Seg.segredo`, `dataforge seguranca`"], ["**Integridade**", "dado alterado sem marca, log forjado", "AEAD, `Seg.auditoria`, `Seg.escapar_log`"], ["**Disponibilidade**", "negação de serviço, exaustão de memória", "`Seg.limitador`, `Seg.json_seguro`, limite de corpo"]]}},
  {"callout": {"tipo": "dica", "titulo": "Os três brigam entre si", "texto": "Cifrar tudo prejudica disponibilidade (a chave vira ponto único de falha). Replicar para disponibilidade aumenta a superfície de confidencialidade. Bloquear a conta após três erros protege contra força bruta e **cria** uma negação de serviço contra o usuário legítimo — quem ataca passa a errar de propósito para trancar a conta alheia. Por isso [atraso progressivo](/docs/seguranca/ataques) é preferível a bloqueio duro. Segurança é sempre uma escolha entre os três, e escolher sem nomear o que se perdeu é como a maioria dos sistemas fica frágil."}},
  {"h2": "Autenticação, autorização, responsabilização, não-repúdio"},
  {"p": "Quatro perguntas diferentes, confundidas o tempo todo. Um sistema que autentica muito bem e não autoriza direito entrega o banco inteiro a um usuário legítimo."},
  { code: `adopt Arcane.Crypto as Crypto
adopt Arcane.Seguranca as Seg
adopt Arcane.OS as OS

// 1. AUTENTICACAO — quem e voce?
guardada := Crypto.hash_password("uma senha bem forte 2026")
assert Crypto.verify_password("uma senha bem forte 2026", guardada)

// 2. AUTORIZACAO — voce pode fazer isto?
steady PERMISSOES := {
    "leitor": ["ler"],
    "editor": ["ler", "escrever"],
    "admin":  ["ler", "escrever", "apagar"]
}

action pode(papel, acao):
    yield acao in (PERMISSOES[papel] ?? [])

assert pode("editor", "escrever")
assert pode("editor", "apagar") is no

// 3. RESPONSABILIZACAO — quem fez, e quando?
livro := Seg.auditoria($"{OS.temp_dir()}/df-princ-{randint(100000, 999999)}.log")
livro.registrar("apagou_pedido", {"pedido": 42}, quem := "ana")
assert livro.conferir()["ok"]

// 4. NAO-REPUDIO — da para provar que foi voce?
// Com chave simetrica isto prova a origem ENTRE AS DUAS PARTES,
// e nao perante um terceiro: quem confere tambem consegue forjar.
chave := Seg.chave_de_assinatura()
recibo := Seg.assinar({"pedido": 42, "por": "ana"}, chave,
    proposito := "recibo")
assert Seg.ler_assinado(recibo, chave, proposito := "recibo")["valor"]["por"] is "ana"

out "os quatro, e o quarto com a ressalva escrita"`, lang: 'df' },
  {"h2": "Privilégio mínimo"},
  {"p": "Cada parte recebe exatamente a autoridade de que precisa, e por exatamente o tempo em que precisa. É o princípio que mais reduz o **estrago** de uma falha — ele não impede a invasão, ele limita o que ela alcança."},
  {"table": {"head": ["Onde aplicar", "Como"], "rows": [["no módulo", "`Arcane.Capacidade` recusa o `adopt` do que não está na lista"], ["no banco", "a conta da aplicação não é a dona do esquema; `service_role` fica fora do bundle"], ["no token", "propósito e prazo — um token de confirmar e-mail não troca senha"], ["no contêiner", "`USER forge` no Dockerfile, e é o que `dataforge devops` gera"], ["no arquivo", "`Seg.caminho_seguro(base, pedido)` — a pasta base é a autoridade"]]}},
  { code: `adopt Arcane.Capacidade as Cap

// A autoridade AMBIENTE e o que se recorta: o 'adopt' de um modulo
// fora da lista e recusado pelo NOME da capacidade que falta.
permitido := Cap.limites()
out $"o que este arquivo alcanca: {len(permitido)} capacidade(s)"

// E o que ela NAO faz, dito no proprio modulo: ela nao tira o que
// ja foi ENTREGUE. Numa linguagem de capacidade, poder e o que se
// PASSA, nao o que esta no ar — e e por isso que bloquear o 'adopt'
// e a fronteira certa, e nao uma meia-medida.`, lang: 'df' },
  {"h2": "Defesa em profundidade"},
  {"p": "Nenhum controle é confiável sozinho. A pergunta que define o desenho é: **quando esta camada falhar, o que segura?**"},
  {"table": {"head": ["Camada", "Exemplo", "O que ela ainda deixa passar"], "rows": [["1. Validar na entrada", "`Seg.numero_seguro(pagina, 1, 1000)`", "um valor válido e malicioso"], ["2. Consulta parametrizada", "`db.query(sql, [valor])`", "nada de SQL — mas o dado vai para a tela"], ["3. Codificar na saída", "`Seg.escapar_html`", "nada de XSS — mas o navegador pode carregar de fora"], ["4. Cabeçalhos", "CSP, `X-Content-Type-Options`", "um bug de lógica de autorização"], ["5. Autorização por recurso", "o dono do pedido é quem o lê", "uma credencial roubada"], ["6. Auditoria", "`Seg.auditoria`", "nada — mas agora dá para investigar"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Escapar não substitui parametrizar", "texto": "`Seg.escapar_sql_like` cuida do `%` e do `_` de um `LIKE`, e **não é defesa contra injeção**: o valor continua tendo de ir por parâmetro. A função existe para que uma busca por `\"50%\"` não vire uma busca por *\"50 seguido de qualquer coisa\"* — que é um bug de resultado, não de segurança."}},
  {"h2": "Zero trust"},
  {"p": "O modelo antigo era um perímetro: dentro da rede, confia-se. **Zero trust** parte de que não há dentro — toda requisição é autenticada, autorizada e registrada, venha de onde vier."},
  {"table": {"head": ["Regra", "O que ela quebra do modelo antigo"], "rows": [["nunca confie na rede de origem", "“é interno” deixa de ser argumento"], ["autentique **cada** requisição", "a sessão longa e implícita dá lugar a token curto"], ["autorize por recurso, e não por papel só", "ser `admin` não basta: é `admin` **daquele** tenant"], ["presuma violação", "o log e a auditoria não são opcionais"]]}},
  {"callout": {"tipo": "dica", "titulo": "Onde isso aparece na linguagem", "texto": "`Seg.url_segura` é zero trust aplicado a uma URL: ela **resolve o nome** antes de responder, porque `localtest.me` resolve para `127.0.0.1` e quem ataca controla o DNS do domínio dele. A pergunta não é *como o endereço se parece*, é *para onde ele aponta* — a mesma troca que o zero trust faz com a rede."}},
  {"h2": "Seguro por desenho, e seguro por padrão"},
  {"p": "São coisas diferentes, e a segunda é a que mais rende. **Por desenho** é a arquitetura escolhida para tornar a falha impossível; **por padrão** é o estado inicial ser o mais restritivo — o que protege quem nunca leu a documentação."},
  {"table": {"head": ["Decisão", "Por desenho ou por padrão", "O que ela evita"], "rows": [["`record` é imutável, ponto", "desenho", "um valor compartilhado mudar sob os pés de quem o leu"], ["`limpar_html` usa lista de **permitidos**", "desenho", "a lista de proibidos que esqueceu `<svg onload>`"], ["`Seg.segredo` imprime `***`", "padrão", "o vault inteiro impresso para depurar"], ["a grade da Vitrine já vem paginada", "padrão", "uma listagem sem teto travar o painel"], ["`POST` não é repetido sem chave de idempotência", "padrão", "a cobrança em dobro de uma retentativa"], ["`Kiln` responde 404 de verdade, não 200", "padrão", "um monitor achando que está tudo bem"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O padrão inseguro mais caro da linguagem, nomeado", "texto": "A linguagem **não sincroniza sozinha**. Duas threads escrevendo na mesma variável perdem atualizações — medido: **40.425 de 80.000**, em silêncio. Isso vale para toda rota do Kiln, onde a concorrência é invisível para quem escreve. O `check` avisa (`escrita-concorrente`), e o aviso é o controle: não há como a linguagem decidir por você onde pôr o mutex sem proibir o uso correto. Veja [Concorrência](/docs/tecnicas/concorrencia)."}},
];

const headings = [{ id: 'confidencialidade-integridade-disponibilidade', text: "Confidencialidade, integridade, disponibilidade", level: 2 as const }, { id: 'autenticacao-autorizacao-responsabilizacao-nao-repudio', text: "Autenticação, autorização, responsabilização, não-repúdio", level: 2 as const }, { id: 'privilegio-minimo', text: "Privilégio mínimo", level: 2 as const }, { id: 'defesa-em-profundidade', text: "Defesa em profundidade", level: 2 as const }, { id: 'zero-trust', text: "Zero trust", level: 2 as const }, { id: 'seguro-por-desenho-e-seguro-por-padrao', text: "Seguro por desenho, e seguro por padrão", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Princípios"}
      description={"CIA, autenticação, autorização, responsabilização, não-repúdio, privilégio mínimo, defesa em profundidade, zero trust, seguro por desenho e por padrão."}
      href={"/docs/seguranca/principios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
