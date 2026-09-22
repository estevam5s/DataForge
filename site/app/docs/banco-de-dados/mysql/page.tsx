// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/banco_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "MySQL e MariaDB",
  description: "Um driver para os dois, a autenticação que quase todo driver caseiro não faz, e as diferenças que importam.",
};

const blocos: Bloco[] = [
  {"p": "O mesmo driver serve os dois: o protocolo é o mesmo, e o que muda é o método de autenticação padrão e alguns nomes de variável."},
  { code: `adopt Arcane.Forge as Forge

db := Forge.esperar("mysql://forge:segredo@localhost:3306/loja",
    prazo := 40.0)

out Forge.versao(db)
Forge.fechar(db)`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "O `caching_sha2_password` é onde os drivers caseiros param", "texto": "O MySQL 8 mudou o padrão de `mysql_native_password` para `caching_sha2_password`. Ele tem dois caminhos: o **rápido**, que usa o cache do servidor, e o **completo**, que exige trocar uma chave RSA. Quase todo driver escrito à mão implementa só o rápido — e falha na primeira conexão de uma senha que o servidor ainda não cacheou, que é justamente a primeira conexão depois de subir o contêiner. Este faz os dois."}},
  {"h2": "As diferenças que importam"},
  {"table": {"head": ["", "MySQL / MariaDB", "PostgreSQL"], "rows": [["parâmetro", "`?`", "`$1`"], ["auto incremento", "`auto_increment`", "`serial`"], ["texto sem limite", "`text`", "`text`"], ["texto com limite", "`varchar(n)` — e `n` é **obrigatório** num índice", "`text` indexa direto"], ["booleano", "`tinyint(1)`", "`boolean`"], ["`insert … on duplicate`", "existe", "é `on conflict`"], ["comparação de texto", "**insensível** a maiúsculas por padrão", "sensível"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A comparação insensível é uma armadilha silenciosa", "texto": "No MySQL, `where email = 'Ana@x.com'` encontra `ana@x.com` — e o mesmo código no Postgres não encontra. Um sistema migrado de um para o outro passa a rejeitar logins que funcionavam, sem nenhum erro no meio. Normalize na **aplicação** (`lower()` antes de gravar e antes de buscar) e o comportamento deixa de depender do motor."}},
  {"h2": "Codificação"},
  {"p": "Use `utf8mb4`, sempre. O `utf8` do MySQL guarda **três** bytes por caractere e não cabe emoji nem vários ideogramas — e o sintoma é um texto truncado na gravação, sem erro."},
  { code: `docker run -d --name loja-my \\
  -e MYSQL_ROOT_PASSWORD=segredo \\
  -e MYSQL_DATABASE=loja \\
  -e MYSQL_USER=forge -e MYSQL_PASSWORD=segredo \\
  -p 3306:3306 mysql:8 \\
  --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci`, lang: 'bash' },
  {"p": "Continue em [Cada motor](/docs/banco-de-dados/motores)."},
];

const headings = [{ id: 'as-diferencas-que-importam', text: "As diferenças que importam", level: 2 as const }, { id: 'codificacao', text: "Codificação", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"MySQL e MariaDB"}
      description={"Um driver para os dois, a autenticação que quase todo driver caseiro não faz, e as diferenças que importam."}
      href={"/docs/banco-de-dados/mysql"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
