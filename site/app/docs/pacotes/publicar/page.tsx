import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Publicar um pacote",
  description: "Do forge.toml ao registro: estrutura, empacotamento e versionamento.",
};

const blocos: Bloco[] = [
  {"h2": "A estrutura"},
  { code: `meu-pacote/
├── forge.toml
├── README.md
├── src/
│   └── main.df        o ponto de entrada
└── tests/
    └── meu_pacote_test.df`, lang: 'bash' },
  {"h2": "O manifesto"},
  { code: `[package]
name = "meu-pacote"
version = "1.0.0"
description = "Uma frase dizendo o que resolve."
authors = ["Seu Nome"]
license = "MIT"
entry = "src/main.df"
dataforge = ">=4.0"
keywords = ["cli", "texto"]

[dependencies]

[scripts]
test = "test tests/"`, lang: 'toml' },
  {"p": "O nome usa minúsculas, dígitos, `-` e `_`, começando por letra. `dataforge pack` recusa o resto — nome de pacote vira caminho de arquivo e URL."},
  {"h2": "O que sai do pacote"},
  {"p": "Só o que o `relay` exporta atravessa o `adopt`:"},
  { code: `action publica():
    yield interna() * 2

action interna():
    yield 21

relay publica          // 'interna' fica dentro do módulo`, lang: 'df' },
  {"p": "Sem nenhum `relay`, o módulo exporta tudo o que definiu no topo. Num pacote, declare `relay` explicitamente: é o que separa a API do detalhe de implementação."},
  {"h2": "Empacotar"},
  { code: `dataforge pack`, lang: 'bash' },
  { code: `✓ meu-pacote 1.0.0
  arquivo  dist/meu-pacote-1.0.0.tar.gz
  tamanho  3.4 KB
  sha256   1cf0908cfde283ef411139600d49f0cfee823d1d67120cab30f1918598f70ef5`, lang: 'bash' },
  {"p": "Ficam de fora `forge_modules/`, `.git/`, `__pycache__/`, `dist/` e `.venv/`. O tarball é reprodutível: mesma fonte, mesmo sha256 — é isso que torna a verificação de integridade possível."},
  {"h2": "Publicar"},
  { code: `dataforge publish --registry=/caminho/do/registro`, lang: 'bash' },
  {"p": "O registro é um índice estático: uma pasta com `index.json` e `pacotes/`. Publicar acrescenta seu tarball e atualiza o índice — daí você abre um PR."},
  {"p": "Republicar a mesma versão é recusado. Suba a `version` no `forge.toml` primeiro: um lockfile que aponta para um conteúdo que mudou é pior que um erro."},
  {"h2": "Versionar"},
  {"table": {"head": ["Mudança", "Sobe o quê", "Exemplo"], "rows": [["Corrigiu um bug", "correção", "1.0.0 → 1.0.1"], ["Acrescentou algo", "menor", "1.0.1 → 1.1.0"], ["Quebrou compatibilidade", "maior", "1.1.0 → 2.0.0"]]}},
  {"p": "Quem depende de você escreveu `^1.0.0`. Enquanto você não subir o `maior`, essa pessoa recebe suas versões automaticamente — e conta com que nada quebre."},
  {"h2": "Testes"},
  {"p": "Um pacote sem teste não tem como provar que a próxima versão não quebrou nada:"},
  { code: `adopt Arcane.Test as T
adopt meu_pacote as M

action test_faz_o_que_promete():
    T.assert_eq(M.publica(), 42)`, lang: 'df' },
  { code: `dataforge test tests/`, lang: 'bash' },
  {"h2": "Mandar para o registro da comunidade"},
  {"p": "O registro do site aceita pacotes de qualquer pessoa, por **dois caminhos**. Os dois chegam na mesma fila de revisão."},
  {"table": {"head": ["Caminho", "Quando usar"], "rows": [
    ["`dataforge publish --remoto`", "o normal — é onde você já está quando termina o pacote"],
    ["[o formulário do painel](/painel/bibliotecas)", "a primeira vez, ou quando o tarball já está publicado e só falta registrar"],
  ]}},

  {"h3": "Pelo terminal"},
  {"p": "Uma vez por máquina, você entra com um token criado em [/painel/tokens](/painel/tokens):"},
  { lang: 'bash', code: `dataforge login
# cole o token — ele é conferido antes de ser guardado

dataforge whoami
#   token     notebook
#   pacotes   3
#   vem de    ~/.dataforge/credenciais.json` },
  {"p": "E a cada versão:"},
  { lang: 'bash', code: `dataforge pack
dataforge publish --remoto \
  --tarball=https://github.com/voce/minha-lib/releases/download/v1.0.0/minha-lib-{versao}.tar.gz` },
  { lang: 'text', code: `publicando minha-lib 1.0.0
  tarball  https://github.com/voce/minha-lib/releases/download/v1.0.0/minha-lib-1.0.0.tar.gz
  sha256   324396cab760ebf2210b7be3bc64d6288edc852f88f91349df8203654ace306a

✓ minha-lib 1.0.0 enviado` },
  {"p": "`{versao}` é trocado pelo número do `forge.toml` — assim o comando não muda a cada release. Se preferir, ponha `tarball` no manifesto e o `--tarball` deixa de ser necessário."},

  {"h3": "O token"},
  {"p": "Ele aparece **uma vez só**, na criação. O banco guarda apenas o `sha256` dele: um vazamento não entrega a capacidade de publicar em nome de ninguém — é a mesma razão de nenhum sistema sério guardar senha em texto."},
  {"table": {"head": ["", ""], "rows": [
    ["onde fica", "`~/.dataforge/credenciais.json`, com permissão 600"],
    ["na CI", "a variável `DATAFORGE_TOKEN` — ela vence o arquivo e não deixa rastro em disco"],
    ["revogar", "em [/painel/tokens](/painel/tokens); qualquer máquina que o use para na hora"],
    ["expirar", "não expira sozinho. Um token que morre no meio de um deploy ensina a guardar o de vida mais longa que existir"],
  ]}},
  {"callout": {"tipo": "atencao", "titulo": "Um token publica em seu nome", "texto": "Ele não lê seus dados nem entra no painel — só publica. Mesmo assim: um por máquina, com nome que diga qual é (`notebook`, `CI do projeto X`). Uma lista de tokens idênticos torna impossível revogar o certo."}},

  {"h3": "Pelo painel"},
  { lang: 'bash', code: `cd minha-lib
dataforge pack                              # gera o .tar.gz
shasum -a 256 minha-lib-1.0.0.tar.gz        # o hash que o painel pede` },
  {"p": "Hospede o `.tar.gz` onde quiser — um release do GitHub serve — e cole no painel o link `https://`, o sha256, o nome e uma descrição."},
  {"callout": {"tipo": "nota", "titulo": "O registro guarda o endereço, não o arquivo", "texto": "Hospedar binário exige um serviço com cota, expiração e política de abuso; um release do GitHub já faz isso melhor. E o **hash** é o que torna a origem irrelevante: se o conteúdo mudar, o `dataforge add` recusa."}},
  {"table": {"head": ["Campo", "Regra", "Por quê"], "rows": [
    ["nome", "minúsculas, dígitos, `-` e `_`", "ele vira `dataforge add <nome>`, e um nome com `/` ou `..` viraria caminho ao ser extraído"],
    ["versão", "semver (`1.0.0`)", "é por estes três números que o resolvedor decide o que `^1.2` aceita"],
    ["tarball", "só `https://`", "um link `http` num instalador é um ataque de rede esperando acontecer"],
    ["sha256", "64 hexadecimais", "é ele que faz o `add` recusar um tarball trocado no caminho"],
  ]}},
  {"h3": "O nome é de quem publicou primeiro"},
  {"p": "Depois do primeiro envio, só o autor manda versão nova daquele nome. Sem essa regra, quem chegasse depois sequestraria o nome de um pacote que outros já instalaram — e o `dataforge add` passaria a baixar outra coisa com o mesmo nome. É o ataque que mais aparece em registro de pacotes."},
  {"h3": "Todo envio passa por revisão"},
  {"p": "O pacote entra como **pendente** e alguém o revisa antes de entrar no registro. Não é burocracia: o `dataforge add` baixa e **executa** o que está lá, e aprovar sozinho tornaria o registro um canal de distribuição de código."},
  {"p": "Quem revisa confere que o hash bate e que o conteúdo é `.df` e `forge.toml` — nada fora da pasta do pacote. Uma versão nova volta para a fila pelo mesmo motivo: aprovar o *nome* de uma vez tornaria a revisão inútil a partir do segundo envio."},
  {"callout": {"tipo": "nota", "titulo": "Recusa vem com motivo", "texto": "Um pacote recusado traz o porquê, e ele aparece no seu painel. Recusar em silêncio faz a pessoa reenviar a mesma coisa."}},
  {"h2": "Um registro próprio"},
  {"p": "Para uso interno numa empresa, aponte o cliente para outro índice:"},
  { code: `export DATAFORGE_REGISTRY=https://pacotes.suaempresa.com
dataforge search .`, lang: 'bash' },
  {"p": "Basta servir estaticamente uma pasta com `index.json` e `pacotes/`. Não há servidor a manter."},
];

const headings = [{ id: 'a-estrutura', text: "A estrutura", level: 2 as const }, { id: 'o-manifesto', text: "O manifesto", level: 2 as const }, { id: 'o-que-sai-do-pacote', text: "O que sai do pacote", level: 2 as const }, { id: 'empacotar', text: "Empacotar", level: 2 as const }, { id: 'publicar', text: "Publicar", level: 2 as const }, { id: 'versionar', text: "Versionar", level: 2 as const }, { id: 'testes', text: "Testes", level: 2 as const }, { id: 'mandar-para-o-registro-da-comunidade', text: "Mandar para o registro da comunidade", level: 2 as const }, { id: 'pelo-terminal', text: "Pelo terminal", level: 3 as const }, { id: 'o-token', text: "O token", level: 3 as const }, { id: 'pelo-painel', text: "Pelo painel", level: 3 as const }, { id: 'o-nome-e-de-quem-publicou-primeiro', text: "O nome é de quem publicou primeiro", level: 3 as const }, { id: 'todo-envio-passa-por-revisao', text: "Todo envio passa por revisão", level: 3 as const }, { id: 'um-registro-proprio', text: "Um registro próprio", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Publicar um pacote"}
      description={"Do forge.toml ao registro: estrutura, empacotamento e versionamento."}
      href={"/docs/pacotes/publicar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
