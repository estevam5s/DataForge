// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Estrutura de uma biblioteca",
  description: "O esqueleto que o init cria, o que cada campo do forge.toml significa, e onde pôr cada coisa.",
};

const blocos: Bloco[] = [
  { code: `dataforge init minha-lib
cd minha-lib
`, lang: 'bash' },
  { code: `minha-lib/
  forge.toml               o manifesto            (versionado)
  src/main.df              a entrada              (versionado)
  tests/principal_test.df  os testes              (versionado)
  forge.lock               o que foi instalado    (versionado)
  forge_modules/           as dependências        (NÃO versionado)
  dist/                    os tarballs gerados    (NÃO versionado)
`, lang: 'text' },
  {"h2": "O manifesto, campo a campo"},
  { code: `[package]
name = "validador"
version = "1.0.0"
description = "Validação de dados: e-mail, CPF, CNPJ, CEP, telefone e senha."
authors = ["Seu Nome"]
license = "MIT"
entry = "src/main.df"
dataforge = ">=1.0"
keywords = ["validacao", "formulario", "cpf", "brasil"]

[dependencies]
texto = "^1.0"

[lint]
ignore = ["magic-number"]

[scripts]
test = "test tests/"
`, lang: 'toml', title: `forge.toml` },
  {"table": {"head": ["Campo", "Para quê"], "rows": [["`name`", "o nome do `adopt`. Minúsculas, sem espaço — e **não se muda depois**"], ["`version`", "semver. Ver [versão](/docs/bibliotecas/versao)"], ["`description`", "a linha que aparece no `dataforge search`"], ["`entry`", "o arquivo que `adopt minha-lib` carrega"], ["`dataforge`", "de qual versão da linguagem ela precisa"], ["`keywords`", "como alguém acha a sua biblioteca sem saber o nome"], ["`[dependencies]`", "o que ela pede, com faixa semver"], ["`[lint]`", "as regras que **este** projeto silencia, com o porquê em comentário"], ["`[scripts]`", "atalhos: `dataforge test` vira o que estiver aqui"]]}},
  {"h2": "Uma entrada, e o resto interno"},
  {"p": "O `entry` é a porta. Tudo o que não passa por ela é detalhe de implementação, e é assim que se consegue mudar o interior sem quebrar ninguém:"},
  { code: `src/
  main.df          a porta — só 'adopt' e 'relay'
  cpf.df           a regra do CPF
  cnpj.df          a do CNPJ
  comum.df         o que os dois usam
`, lang: 'text' },
  { code: `adopt ./cpf as Cpf
adopt ./cnpj as Cnpj

action cpf(texto):
    yield Cpf.validar(texto)

action cnpj(texto):
    yield Cnpj.validar(texto)

relay cpf, cnpj
`, lang: 'df', title: `src/main.df` },
  {"p": "Quem usa escreve `V.cpf(\"...\")`. Que exista um `comum.df`, e o que tem dentro, não é problema de ninguém — e **pode mudar numa versão de correção**."},
  {"h2": "Nada de efeito no topo"},
  {"p": "O corpo de um módulo roda no `adopt` de quem importa. Numa biblioteca, isso significa: na hora em que a aplicação da outra pessoa inicia."},
  { code: `// NÃO: isto abre conexão quando alguém te importa
conexao := Banco.abrir("dados.db")

action buscar(id):
    yield Banco.query(conexao, "SELECT …", [id])
`, lang: 'df' },
  { code: `// SIM: quem usa decide quando, e com qual banco
action buscar(conexao, id):
    yield Banco.query(conexao, "SELECT …", [id])

relay buscar
`, lang: 'df' },
  {"p": "O sintoma do primeiro caso é caro e indireto: o teste de quem te usa fica lento, ou abre arquivo, ou falha em CI sem disco — e a causa está numa biblioteca que ele nem chamou ainda."},
  {"h2": "O README é parte do pacote"},
  {"p": "Três coisas que quem chega procura, nesta ordem: **o que isto faz** (uma frase), **como instalo** (uma linha), **um exemplo que roda** (cinco linhas). O resto pode esperar."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/bibliotecas/contrato", "title": "O contrato", "desc": "o que o relay promete"}, {"href": "/docs/cli/forge-toml", "title": "forge.toml", "desc": "a referência completa do manifesto"}]},
];

const headings = [{ id: 'o-manifesto-campo-a-campo', text: "O manifesto, campo a campo", level: 2 as const }, { id: 'uma-entrada-e-o-resto-interno', text: "Uma entrada, e o resto interno", level: 2 as const }, { id: 'nada-de-efeito-no-topo', text: "Nada de efeito no topo", level: 2 as const }, { id: 'o-readme-e-parte-do-pacote', text: "O README é parte do pacote", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Estrutura de uma biblioteca"}
      description={"O esqueleto que o init cria, o que cada campo do forge.toml significa, e onde pôr cada coisa."}
      href={"/docs/bibliotecas/estrutura"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
