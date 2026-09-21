// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Operação e conformidade",
  description: "DevSecOps, cadeia de suprimentos, contêiner, nuvem, testes de segurança, privacidade e LGPD — o que a linguagem gera, o que ela verifica e o que é infraestrutura.",
};

const blocos: Bloco[] = [
  {"p": "As frentes desta página têm uma coisa em comum: **elas não são código da aplicação**. São o que roda em volta dele — a esteira, a imagem, o cluster, o processo. A linguagem participa de duas formas: gerando artefato e verificando o que dá para verificar."},
  {"h2": "DevSecOps: as cinco que reprovam"},
  { code: `// A esteira, e o que cada linha cobra
//
//   dataforge check . --strict        nome, aridade, tipo — entre arquivos
//   dataforge lint .                  estilo e higiene
//   dataforge seguranca . --strict    segredo e dez regras (SAST)
//   dataforge test tests/ --minimo=80 suite, com piso de cobertura
//   dataforge devops doctor           o que falta para levar ao ar
//
// E o gancho local, que pega antes de o segredo sair da maquina:
//
//   # .git/hooks/pre-commit
//   dataforge seguranca . --strict || exit 1`, lang: 'df' },
  {"table": {"head": ["Sigla", "O que é", "Aqui"], "rows": [["**SAST**", "análise estática do seu código", "`dataforge seguranca` + `check` + `lint`"], ["**SCA**", "análise das dependências", "`forge.lock` com sha256; `dataforge outdated`"], ["**SBOM**", "inventário do que compõe o artefato", "`dataforge devops sbom`"], ["**Secret scanning**", "segredo no repositório", "`dataforge seguranca`, em qualquer tipo de arquivo"], ["**DAST**", "teste contra a aplicação rodando", "**não existe** — é uma ferramenta externa (ZAP, Burp)"], ["**Fuzzing**", "entrada aleatória em massa", "**não existe** como ferramenta; `Crucible` tem teste por propriedade"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O gancho local não substitui a esteira", "texto": "Um `pre-commit` pode ser pulado com `--no-verify`, e é pulado. Ele existe para dar a resposta **rápida** a quem está escrevendo; quem **reprova** é o CI, que não tem como ser pulado. Os dois rodam o mesmo comando de propósito: se divergirem, o local passa a aprovar o que o remoto recusa, e a confiança no primeiro acaba."}},
  {"h2": "Cadeia de suprimentos"},
  {"p": "O código que você não escreveu roda com a mesma autoridade do que você escreveu. É hoje um dos vetores mais explorados, e a defesa é chata: saber exatamente o que entrou."},
  {"table": {"head": ["Controle", "Como aqui"], "rows": [["**zero dependência no runtime**", "`dataforge/` usa só a stdlib do Python — a superfície de terceiros é **zero**"], ["lockfile **lido**", "`install` instala o que o lock fixa; `update` é que reescreve"], ["integridade conferida", "o sha256 do lock é comparado com o que chegou"], ["tarball reprodutível", "`mtime=0`, uid/gid zerados — sem isso o sha256 mudaria a cada empacotamento e a verificação não significaria nada"], ["extração recusa `../` e link simbólico", "um pacote não escreve fora da própria pasta"], ["conflito de versão é **erro**", "duas cópias em versões diferentes geram bug irreproduzível"], ["**assinatura do pacote**", "**não existe** — o que há é integridade por hash no lock"]]}},
  {"h2": "Contêiner e nuvem"},
  {"p": "`dataforge devops` **gera** e sai da frente. Um `deploy` que falasse com Docker e Kubernetes por dentro esconderia o que a imagem é, e no dia em que alguém precisa mudar uma camada não haveria onde mexer."},
  {"table": {"head": ["No artefato gerado", "Sem ele"], "rows": [["`USER forge`", "um escape de contêiner vira root no host"], ["`.env` no `.dockerignore`", "o segredo fica na camada, e `docker history` o mostra"], ["o manifesto copiado antes do código", "um commit numa linha reinstala tudo"], ["`resources` + as duas sondas no Deployment", "um pod come o nó; o Service manda tráfego antes da hora"], ["`depends_on: service_healthy`", "a app falha na primeira consulta, de forma intermitente"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`--host=0.0.0.0` é obrigatório dentro de um contêiner", "texto": "O padrão é `127.0.0.1`, que de dentro significa **o próprio contêiner**. O sintoma engana: o log diz “no ar” e o `curl` de fora não recebe nada. Vale para a Vitrine e para o `ignite` do Kiln (`at \"0.0.0.0\"`)."}},
  {"p": "Segurança de **nuvem** e de **Kubernetes** — IAM, políticas de rede, admission control, varredura de imagem — é configuração da plataforma, e não há nada a implementar numa linguagem. O que a linguagem faz é gerar manifestos que já nascem com o mínimo certo."},
  {"h2": "Testes de segurança"},
  { code: `adopt Arcane.Seguranca as Seg

// Um teste de seguranca e um teste que cobra a RECUSA. O caminho
// feliz ja tem dono; o que ninguem escreve e o outro.
action test_caminho_de_arquivo_nao_sai_da_pasta():
    monitor:
        Seg.caminho_seguro("/tmp/uploads", "../../etc/passwd")
        assert no
    handle UnsafeInputError as e:
        assert yes

action test_o_token_de_um_proposito_nao_serve_a_outro():
    chave := Seg.chave_de_assinatura()
    t := Seg.assinar({"id": 1}, chave, proposito := "confirmar-email")
    monitor:
        Seg.ler_assinado(t, chave, proposito := "trocar-senha")
        assert no
    handle SignatureError as e:
        assert yes

test_caminho_de_arquivo_nao_sai_da_pasta()
test_o_token_de_um_proposito_nao_serve_a_outro()
out "dois testes que cobram a recusa"`, lang: 'df' },
  {"h2": "Privacidade, LGPD e GDPR"},
  {"p": "Segurança pergunta *quem pode acessar*. Privacidade pergunta *se esse dado deveria existir*. Um sistema pode ser impecável na primeira e ilegal na segunda."},
  {"table": {"head": ["Obrigação", "O que ela exige", "A peça"], "rows": [["**minimização**", "não coletar o que não se usa", "nenhuma ferramenta substitui a decisão de desenho"], ["**finalidade**", "usar só para o que foi declarado", "—"], ["**mascaramento**", "log e relatório sem dado pessoal", "`Seg.mascarar_pii` — CPF, CNPJ, cartão com Luhn, e-mail, telefone"], ["**retenção**", "apagar quando o prazo vence", "`Crypto.apagar_seguro`; a política é sua"], ["**acesso e portabilidade**", "entregar o que se tem sobre a pessoa", "sua consulta"], ["**eliminação**", "apagar a pedido", "e nas cópias de segurança também — é aí que quase todo mundo falha"], ["**registro de tratamento**", "provar o que foi feito", "[`Seg.auditoria`](/docs/biblioteca/seguranca)"], ["**notificação de incidente**", "comunicar em prazo", "processo, e não código"]]}},
  {"callout": {"tipo": "dica", "titulo": "Criptografia ajuda a apagar", "texto": "Apagar de verdade um dado espalhado por réplicas e cópias de segurança é difícil. **Destruição de chave** é a saída prática: se cada titular tem a própria chave de dados, revogá-la torna os registros dele ilegíveis em toda cópia, de uma vez. `Chaves.cofre` com uma DEK por titular é o desenho, e `revogar` é o gesto."}},
  {"p": "Continue em [As ferramentas](/docs/seguranca/ferramentas) e [Detecção](/docs/seguranca/deteccao)."},
];

const headings = [{ id: 'devsecops-as-cinco-que-reprovam', text: "DevSecOps: as cinco que reprovam", level: 2 as const }, { id: 'cadeia-de-suprimentos', text: "Cadeia de suprimentos", level: 2 as const }, { id: 'conteiner-e-nuvem', text: "Contêiner e nuvem", level: 2 as const }, { id: 'testes-de-seguranca', text: "Testes de segurança", level: 2 as const }, { id: 'privacidade-lgpd-e-gdpr', text: "Privacidade, LGPD e GDPR", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Operação e conformidade"}
      description={"DevSecOps, cadeia de suprimentos, contêiner, nuvem, testes de segurança, privacidade e LGPD — o que a linguagem gera, o que ela verifica e o que é infraestrutura."}
      href={"/docs/seguranca/operacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
