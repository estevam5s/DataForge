// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "OWASP Top 10 na linguagem",
  description: "As dez categorias de 2021, e o que a linguagem, a biblioteca e as ferramentas fazem com cada uma.",
};

const blocos: Bloco[] = [
  {"p": "O OWASP Top 10 é a lista das categorias de falha que mais aparecem em aplicações web. Ela não é um checklist — é um mapa de onde procurar. Para cada categoria, o que existe aqui para ajudar, e o que continua sendo decisão de quem escreve."},
  {"table": {"head": ["Categoria (2021)", "O que existe aqui", "O que continua sendo seu"], "rows": [["**A01** Controle de acesso quebrado", "`Arcane.Politica` — negar por padrão, negar vence permitir, a decisão diz quem decidiu", "conferir o **dono** do objeto em cada rota (ver [API](/docs/seguranca/api))"], ["**A02** Falhas criptográficas", "scrypt em `hash_password`, ChaCha20-Poly1305, `Arcane.Chaves` com rotação", "não inventar esquema; TLS no proxy"], ["**A03** Injeção", "`?` no SQL, escape por destino, templates que escapam, `escapar_shell`", "não montar SQL com `$\"…\"`"], ["**A04** Design inseguro", "`Arcane.Dominio` com invariantes cobradas", "modelar ameaças antes — [STRIDE](/docs/seguranca/ameacas)"], ["**A05** Configuração insegura", "`Kiln.secure_headers()`, `dataforge devops doctor`", "ligar HSTS quando o TLS existir"], ["**A06** Componentes vulneráveis", "lockfile com sha256, SBOM, `dataforge outdated`", "atualizar — [Cadeia](/docs/seguranca/cadeia)"], ["**A07** Falhas de autenticação", "`tentativas` (bloqueio progressivo), TOTP, `forca_da_senha`, `vazada`", "a mesma resposta para usuário e senha errados"], ["**A08** Integridade de software e dados", "`Arcane.Integridade`, tarball reprodutível, webhook assinado", "assinar o que se publica"], ["**A09** Falhas de log e monitoramento", "`auditoria` encadeada, `escapar_log`, `Arcane.Deteccao`", "alguém olhar os alertas"], ["**A10** SSRF", "`url_segura` resolve o nome antes de responder", "usar o IP que ela devolve"]]}},
  { code: `adopt Arcane.Seguranca as S

// A03 — o nome que vira SQL, o texto que vira shell, a celula que vira formula
assert S.escapar_csv("=HYPERLINK(\\"x\\")").startswith("'")
assert "\\n" not in S.escapar_log("ok\\nFALSO login admin")

// A07 — quanto vale esta senha?
assert S.forca_da_senha("123456")["nota"] smaller S.forca_da_senha("cavalo-bateria-grampo-azul")["nota"]

// A10 — o endereco interno e recusado ANTES da requisicao, e levanta:
// devolver "nao" deixaria quem esqueceu de conferir seguir adiante.
monitor:
    S.url_segura("http://127.0.0.1/admin")
    assert no
handle Error as e:
    out e.message
out "quatro categorias, conferidas"`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "A varredura acha o que está escrito", "texto": "`dataforge seguranca` aplica regras sintáticas — SQL concatenado, shell com interpolação, MD5 para assinatura — e acha segredo pelo formato. Ela não prova que a aplicação é segura: acha o que está **escrito** de um jeito perigoso, que é a classe de falha mais barata de corrigir."}},
  {"p": "Continue em [Segurança de API](/docs/seguranca/api) e [Web](/docs/seguranca/web)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"OWASP Top 10 na linguagem"}
      description={"As dez categorias de 2021, e o que a linguagem, a biblioteca e as ferramentas fazem com cada uma."}
      href={"/docs/seguranca/owasp"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
