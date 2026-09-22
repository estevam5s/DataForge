// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Segurança na web",
  description: "Cabeçalhos, CSP, CORS, CSRF, cookie, limite de taxa e de corpo — o que o Kiln liga e o que é decisão sua.",
};

const blocos: Bloco[] = [
  {"p": "O navegador tem defesas poderosas — e **nenhuma** vem ligada. Elas dependem de cabeçalhos que o servidor manda. O Kiln traz cada uma como middleware, e a lista abaixo é o mínimo de um site público."},
  { code: `adopt Kiln

server site on 0:
    middleware Kiln.rate_limit(60, 60)        // 60 pedidos por minuto, por IP
    middleware Kiln.body_limit(1048576)       // 1 MB de corpo, no maximo
    after Kiln.secure_headers()               // nosniff, frame, CSP, referrer
    route GET "/":
        respond json {"ok": yes}

r := Kiln.test(site, "GET", "/")
assert r["headers"]["X-Frame-Options"] is "DENY"
assert r["headers"]["X-Content-Type-Options"] is "nosniff"
assert "default-src 'self'" in r["headers"]["Content-Security-Policy"]
out "os cabecalhos sairam"`, lang: 'df' },
  {"table": {"head": ["Defesa", "No Kiln", "Contra"], "rows": [["`X-Frame-Options` / `frame-ancestors`", "`secure_headers(frame := …)`", "clickjacking: sua página num `<iframe>` de outro"], ["`Content-Security-Policy`", "`secure_headers(csp := …)`", "o XSS que escapou do escape — o script injetado não roda"], ["`X-Content-Type-Options: nosniff`", "ligado", "um `.txt` com HTML executado como página"], ["`Strict-Transport-Security`", "`secure_headers(hsts := yes)`", "o primeiro acesso por http interceptado"], ["CORS com origem **nomeada**", "`Kiln.cors([\"https://app.exemplo.com\"])`", "outro site lendo a resposta com o cookie do usuário"], ["CSRF", "`Kiln.csrf(segredo)` + `csrf_token`", "o formulário de outro site postando no seu"], ["cookie `HttpOnly`, `SameSite`, `Secure`", "`Kiln.cookie(…)` — `HttpOnly` e `Lax` por padrão", "o script que lê a sessão; o POST de outra origem"], ["limite de taxa e de corpo", "`rate_limit`, `body_limit`", "força bruta; o corpo de 2 GB que derruba o processo"]]}},
  {"callout": {"tipo": "atencao", "titulo": "HSTS desligado por padrão — de propósito", "texto": "Ele diz ao navegador *“só me acesse por https pelos próximos meses”*, e o navegador **obedece** mesmo que o https ainda não exista. Mandado cedo demais, tira o site do ar para quem já o visitou, sem como voltar atrás a tempo. Ligue quando o certificado estiver de pé."}},
  {"callout": {"tipo": "atencao", "titulo": "`cors(\"*\")` com credenciais", "texto": "Origem `*` é para API pública e sem cookie. Com sessão, a origem precisa ser nomeada — senão qualquer site que o usuário abrir lê as respostas como se fosse ele."}},
  {"p": "O `rate_limit` conta **por processo**: com três réplicas, o limite real é o triplo. Ver [Kiln em produção](/docs/kiln/producao)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Segurança na web"}
      description={"Cabeçalhos, CSP, CORS, CSRF, cookie, limite de taxa e de corpo — o que o Kiln liga e o que é decisão sua."}
      href={"/docs/seguranca/web"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
