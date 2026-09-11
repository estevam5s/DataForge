// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/versoes.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Segurança",
  description: "O que a linguagem garante por construção, e o que continua sendo sua responsabilidade.",
};

const blocos: Bloco[] = [
  {"p": "Segurança não se acrescenta depois. Esta página lista o que o DataForge **garante por construção** — coisas que você não consegue errar mesmo querendo — e o que ele não pode garantir por você."},
  {"h2": "Injeção de SQL"},
  {"p": "**Garantido.** O construtor de consultas não tem como pôr um valor no texto da consulta: valores viram parâmetros, sempre."},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Forge.executar(db, "create table u (id integer primary key, nome text)")

malicioso := "'; drop table u; --"
Forge.de(db, "u").inserir({"nome": malicioso})

// a tabela continua lá — o valor foi tratado como dado
assert "u" in Forge.tabelas(db)`, lang: 'df' },
  {"p": "A lista de operadores também é **fechada**: `.onde(\"x\", operador, v)` só aceita os operadores conhecidos. Um operador vindo de variável seria outro caminho de injeção."},
  {"callout": {"tipo": "atencao", "titulo": "`onde_cru` é a saída de emergência", "texto": "Ela existe para o que o construtor não cobre — funções do banco, operadores geográficos. O SQL vai como escrito; **os valores continuam parâmetros**. Nunca concatene entrada do usuário no texto que você passa a ela."}},
  {"h2": "XSS nos templates"},
  {"p": "**Garantido por padrão.** O Kiln escapa toda interpolação de template:"},
  { code: `// render "pagina.html" with {"nome": entrada_do_usuario}
//
// No template:  <p>{{ nome }}</p>
// Se 'nome' for '<script>alert(1)</script>', sai escapado — o
// navegador mostra o texto, não executa.`, lang: 'df' },
  {"p": "Escapar é o **padrão**, não uma opção a lembrar. Ver [Kiln: páginas](/docs/kiln/paginas)."},
  {"h2": "Travessia de caminho em pacotes"},
  {"p": "**Garantido.** A extração de um pacote recusa qualquer entrada com `../` ou link simbólico — um pacote não pode escrever fora da própria pasta."},
  {"p": "O tarball também é **reprodutível** (`mtime` zerado, uid/gid zerados): sem isso o sha256 mudaria a cada empacotamento, e a verificação de integridade não significaria nada."},
  {"h2": "Integridade dos pacotes"},
  {"p": "**Garantido.** Todo pacote instalado tem o sha256 registrado no `forge.lock`. Se o conteúdo mudar entre o registro e você, a instalação falha com `IntegrityError` (DF0507)."},
  { code: `dataforge install --limpar-cache   # se suspeitar do cache local`, lang: 'bash' },
  {"h2": "Conflito de versão"},
  {"p": "**É erro, não aviso.** Se dois pacotes pedem faixas incompatíveis do mesmo terceiro, o resolvedor falha dizendo quem pediu o quê. Instalar duas cópias em versões diferentes gera bug irreproduzível."},
  {"h2": "TLS"},
  {"p": "**Verificado por padrão.** `Http.get` e as conexões de banco verificam o certificado. Desligar exige dizer isso explicitamente — e a documentação não ensina como, de propósito."},
  {"callout": {"tipo": "perigo", "titulo": "Não desligue a verificação de TLS", "texto": "Um certificado inválido significa que você não sabe com quem está falando. Corrija o certificado do servidor; desligar a verificação transforma um erro visível num problema silencioso."}},
  {"h2": "Senhas no editor"},
  {"p": "**A extensão do VS Code** guarda senhas de banco no cofre do sistema (`SecretStorage`), não no `settings.json` — que muita gente versiona sem perceber. A URL salva leva um marcador no lugar da senha."},
  {"h2": "O que continua sendo sua responsabilidade"},
  {"h3": "Segredos"},
  {"p": "A linguagem não tem como saber que um texto é uma senha. As regras valem aqui como em qualquer lugar:"},
  { code: `adopt Forge

// certo: vem do ambiente
db := Forge.conectar(ambiente("DATABASE_URL") ?? ":memory:")

// errado: vai para o repositório junto com o código
// db := Forge.conectar("postgres://usuario:senha123@prod/app")`, lang: 'df' },
  {"list": ["Nunca escreva credencial no código — use `ambiente(\"NOME\")`.", "`.env` e `forge.local.toml` no `.gitignore`.", "Se um segredo vazou para o histórico do git, **rotacione**: apagar o commit não basta, ele já foi clonado."]},
  {"h3": "Validar o que vem de fora"},
  {"p": "O corpo, a query e os cabeçalhos de uma requisição vêm do cliente. Trate-os como hostis:"},
  { code: `adopt Forge

db := Forge.conectar(":memory:")
Usuario := Forge.modelo("Usuario", {
    "id": {"tipo": "Serial"},
    "email": {"tipo": "Texto", "obrigatorio": yes, "validacoes": ["email"]},
    "idade": {"tipo": "Inteiro", "validacoes": [["minimo", 0], ["maximo", 130]]}
}, {"conexao": db})
Forge.migrar_tudo(db)

monitor:
    Usuario.criar({"email": "não-é-email", "idade": -5})
handle ValidationError as e:
    assert len(e.campos) is 2`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`query[\"x\"]` sem `??` dá 500", "texto": "A chave pode não vir, e indexar um vault sem a chave é erro. `params` é a exceção — se a rota casou, o parâmetro existe."}},
  {"h3": "Autorização"},
  {"p": "Autenticação diz **quem** é; autorização diz **o que pode**. A segunda é regra de negócio, e nenhuma biblioteca a escreve por você:"},
  { code: `// route DELETE "/pedidos/:id":
//     given req.sessao["usuario"] is void:
//         respond 401, {"erro": "não autenticado"}
//
//     pedido := buscar(params.id)
//     given pedido["usuario_id"] isnt req.sessao["usuario"]:
//         respond 403, {"erro": "não é seu"}
//
//     remover(params.id)
//     respond 204, ""`, lang: 'df' },
  {"p": "O erro clássico é conferir só a autenticação — e qualquer usuário logado apagar o pedido de qualquer outro."},
  {"h3": "Limite de requisições"},
  {"p": "O Kiln tem `rate_limit`, mas quem decide o limite é você. Sem ele, uma rota de login é um convite a força bruta."},
  {"h3": "Produção"},
  {"list": ["**Ponha um nginx ou Caddy na frente do Kiln.** Ele roda sobre o `http.server` do Python, que não foi feito para exposição direta.", "**Rode como usuário sem privilégio.** O `Dockerfile` do projeto já faz isso.", "**`dataforge check --strict` no CI.** O analisador acha erro de nome e de aridade antes do usuário achar."]},
  {"h2": "Relatar uma vulnerabilidade"},
  {"p": "Se você encontrou algo que permite executar código, ler arquivo fora do escopo, ou contornar as garantias desta página:"},
  {"list": ["**Não abra issue pública.** Ela é indexada em minutos.", "Escreva para o e-mail do mantenedor no [repositório](https://github.com/estevam5s/DataForge), com o que você fez e o que aconteceu.", "Um exemplo mínimo que reproduz vale mais que uma descrição longa."]},
  {"callout": {"tipo": "nota", "titulo": "O que não é vulnerabilidade", "texto": "`trigger` derruba o programa, `run` executa o arquivo que você mandou, e um `.df` malicioso faz o que qualquer script faz. A linguagem executa código — não há sandbox, e ela não promete um."}},
  {"h2": "Os erros que ajudam"},
  {"table": {"head": ["Código", "Sobre"], "rows": [["`DF0507`", "pacote corrompido — o sha256 não bate"], ["`DF0508`", "pacote com caminho inseguro (`../` ou link simbólico)"], ["`DF1203`", "credenciais recusadas"], ["`DF1304`", "falha de TLS"], ["`DF1308`", "sessão inválida ou expirada"], ["`DF1311`", "origem não permitida (CORS)"], ["`DF1312`", "limite de requisições"], ["`DF1505`", "dado fora do esquema"]]}},
  {"p": "`dataforge explain DF0508` explica cada um."},
];

const headings = [{ id: 'injecao-de-sql', text: "Injeção de SQL", level: 2 as const }, { id: 'xss-nos-templates', text: "XSS nos templates", level: 2 as const }, { id: 'travessia-de-caminho-em-pacotes', text: "Travessia de caminho em pacotes", level: 2 as const }, { id: 'integridade-dos-pacotes', text: "Integridade dos pacotes", level: 2 as const }, { id: 'conflito-de-versao', text: "Conflito de versão", level: 2 as const }, { id: 'tls', text: "TLS", level: 2 as const }, { id: 'senhas-no-editor', text: "Senhas no editor", level: 2 as const }, { id: 'o-que-continua-sendo-sua-responsabilidade', text: "O que continua sendo sua responsabilidade", level: 2 as const }, { id: 'segredos', text: "Segredos", level: 3 as const }, { id: 'validar-o-que-vem-de-fora', text: "Validar o que vem de fora", level: 3 as const }, { id: 'autorizacao', text: "Autorização", level: 3 as const }, { id: 'limite-de-requisicoes', text: "Limite de requisições", level: 3 as const }, { id: 'producao', text: "Produção", level: 3 as const }, { id: 'relatar-uma-vulnerabilidade', text: "Relatar uma vulnerabilidade", level: 2 as const }, { id: 'os-erros-que-ajudam', text: "Os erros que ajudam", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Segurança"}
      description={"O que a linguagem garante por construção, e o que continua sendo sua responsabilidade."}
      href={"/docs/seguranca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
