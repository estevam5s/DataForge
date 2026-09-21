// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Autorização e capacidades",
  description: "RBAC, autorização por recurso, a fronteira de autoridade do Arcane.Capacidade, segurança de dependências e os limites do sandbox.",
};

const blocos: Bloco[] = [
  {"p": "Autenticação diz **quem** é. Autorização diz **o que pode**. A segunda é onde mora a maioria das falhas exploradas na prática, e é a menos testada — porque exige pensar no usuário legítimo agindo fora do seu papel."},
  {"h2": "A falha mais comum: autorização por objeto"},
  {"p": "Conferir o **papel** e esquecer o **dono** é a vulnerabilidade mais frequente em aplicações web. O usuário está autenticado, tem o papel certo, e lê o pedido de outra pessoa trocando o número na URL."},
  { code: `// ERRADO: confere o papel, e nao o dono.
action ver_pedido_errado(usuario, id):
    given usuario["papel"] isnt "cliente":
        trigger "sem permissao"
    yield buscar(id)          // qualquer id, de qualquer um

// CERTO: a consulta carrega o dono. A autorizacao vira uma
// condicao do WHERE, e nao um 'given' que alguem pode esquecer.
action ver_pedido(usuario, id):
    pedido := buscar_do_dono(id, usuario["id"])
    given pedido is void:
        // 404, e nao 403: dizer "existe, mas nao e seu" ja entrega
        // que aquele id existe.
        trigger "nao encontrado"
    yield pedido

action buscar(id):
    yield {"id": id, "dono": 99}

action buscar_do_dono(id, dono):
    p := buscar(id)
    yield p given p["dono"] is dono otherwise void

monitor:
    ver_pedido({"id": 7, "papel": "cliente"}, 1234)
    assert no
handle Error as e:
    out "o pedido de outro dono nao e alcancavel"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "403 ou 404?", "texto": "Responder **403 Forbidden** a um recurso que existe e não é seu confirma que ele existe — e isso já é informação. Para recursos cujo identificador é sequencial ou adivinhável, **404** é a resposta certa: quem não pode ver não descobre nem que existe. Use 403 quando a existência do recurso já é pública e o que falta é permissão."}},
  {"h2": "RBAC"},
  {"p": "Papéis são a forma mais usada, e funcionam bem quando as permissões são **do sistema**. Quando dependem do dado (*este* pedido, *este* tenant), papel sozinho não basta — a checagem tem de descer ao recurso."},
  { code: `steady PERMISSOES := {
    "leitor": ["pedido:ler"],
    "editor": ["pedido:ler", "pedido:escrever"],
    "admin":  ["pedido:ler", "pedido:escrever", "pedido:apagar",
               "usuario:gerir"]
}

action pode(papel, permissao):
    yield permissao in (PERMISSOES[papel] ?? [])

// O padrao e NEGAR: um papel desconhecido nao ganha nada. A lista
// vazia do '??' e o que garante isso — sem ela, indexar um vault
// sem a chave levantaria, e um 'monitor' mal colocado viraria um
// 'permitido'.
assert pode("admin", "usuario:gerir")
assert pode("leitor", "pedido:apagar") is no
assert pode("papel-que-nao-existe", "pedido:ler") is no

// E a separacao de funcoes: quem aprova nao e quem solicita.
action aprovar(solicitante, aprovador, valor):
    given solicitante is aprovador:
        trigger "quem solicita nao aprova"
    given pode(aprovador["papel"], "pedido:escrever") is no:
        trigger "sem permissao"
    yield {"aprovado": yes, "valor": valor}

monitor:
    ana := {"id": 1, "papel": "editor"}
    aprovar(ana, ana, 10000)
    assert no
handle Error as e:
    out $"recusado: {e.message}"`, lang: 'df' },
  {"h2": "Capacidades: a outra escola"},
  {"p": "No modelo de **capacidade**, poder não é consultado numa tabela — é **passado**. Quem tem a referência ao recurso pode usá-lo, e quem não tem não consegue nem nomeá-lo. Isso elimina por construção a confusão do *deputado confuso*, em que um componente privilegiado é enganado a agir em nome de outro."},
  { code: `adopt Arcane.Capacidade as Cap

// 'limites()' devolve a lista em EXECUCAO. Um modulo que
// prometesse contencao sem dizer o que alcanca seria usado onde
// nao pode, e a descoberta viria por incidente.
out $"capacidades deste arquivo: {len(Cap.limites())}"

// A fronteira e o 'adopt': um modulo fora da lista e recusado pelo
// NOME da capacidade que falta — e nao com "erro de import".`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O que a capacidade NÃO é — e está no próprio módulo", "texto": "Ela bloqueia a **autoridade ambiente** (o `adopt`), e **não tira o que já foi entregue**. Isso não é limitação de implementação: é o modelo. Numa linguagem de capacidade, poder é o que se **passa**, não o que está no ar — e por isso bloquear o `adopt` é a fronteira certa. Mas a consequência precisa estar clara: **não é um sandbox**. Código que já recebeu um objeto de arquivo continua usando-o. Contenção real é processo separado, contêiner ou VM."}},
  {"h2": "Sandbox — o veredito"},
  {"table": {"head": ["Nível", "Existe aqui?", "O que ele realmente contém"], "rows": [["`Arcane.Capacidade`", "**sim**", "o `adopt`; não contém código já autorizado"], ["Restrição por processo", "**parcial** — `P.map_processos`", "isola memória; não isola disco nem rede"], ["Contêiner", "**gerado**, não executado", "`dataforge devops` escreve o Dockerfile com `USER forge`"], ["VM / microVM", "**não existe**", "é infraestrutura"], ["Executar código não confiável", "**não faça**", "não há mecanismo que torne isso seguro aqui"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Não execute código de terceiros no seu processo", "texto": "Não há, nesta linguagem, um modo de execução que torne seguro rodar um `.df` que você não escreveu. Se o requisito for esse — um *playground*, uma automação enviada por usuário —, a contenção tem de vir de fora: contêiner descartável, sem rede, com limite de CPU e memória, e com prazo. Qualquer coisa aquém disso é uma aposta."}},
  {"h2": "Segurança de dependências"},
  {"p": "A cadeia de suprimentos é hoje um dos vetores mais explorados: o código que você não escreveu roda com a mesma autoridade do que você escreveu."},
  {"table": {"head": ["Controle", "Como aqui"], "rows": [["**zero dependência no runtime**", "`dataforge/` usa só a stdlib do Python — a superfície de terceiros é **zero**"], ["lockfile **lido**", "`forge.lock` fixa a versão e o sha256, e `install` o honra"], ["integridade conferida", "o sha256 do lock é comparado com o que chegou — é o ataque do tarball trocado"], ["conflito de versão é **erro**", "duas cópias em versões diferentes geram bug irreproduzível"], ["extração recusa `../` e link simbólico", "um pacote não escreve fora da própria pasta"], ["tarball reprodutível", "`mtime=0`, uid/gid zerados — sem isso o sha256 mudaria a cada empacotamento e a verificação não significaria nada"], ["SBOM", "`dataforge devops sbom`"]]}},
  {"callout": {"tipo": "dica", "titulo": "Um lockfile que ninguém lê não trava nada", "texto": "O `forge.lock` era versionado, carregava o sha256 de cada pacote — e **nenhum caminho de instalação o consultava**. Duas pessoas clonando o mesmo projeto em dias diferentes recebiam árvores diferentes, e a “verificação de integridade” conferia um download contra ele mesmo. Hoje `install` instala o que o lock fixa, `update` reescreve, e `add` move só o que está sendo adicionado. Vale conferir isso em qualquer gerenciador que você use."}},
];

const headings = [{ id: 'a-falha-mais-comum-autorizacao-por-objeto', text: "A falha mais comum: autorização por objeto", level: 2 as const }, { id: 'rbac', text: "RBAC", level: 2 as const }, { id: 'capacidades-a-outra-escola', text: "Capacidades: a outra escola", level: 2 as const }, { id: 'sandbox-o-veredito', text: "Sandbox — o veredito", level: 2 as const }, { id: 'seguranca-de-dependencias', text: "Segurança de dependências", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Autorização e capacidades"}
      description={"RBAC, autorização por recurso, a fronteira de autoridade do Arcane.Capacidade, segurança de dependências e os limites do sandbox."}
      href={"/docs/seguranca/autorizacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
