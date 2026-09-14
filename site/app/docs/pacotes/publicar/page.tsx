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
  {"p": "O registro do site aceita pacotes de qualquer pessoa. O envio é pelo [painel](/painel/bibliotecas), com a conta que você já usa — e o que se manda é o **endereço** do tarball e o hash dele, não o arquivo."},
  { code: `cd minha-lib
dataforge pack                              # gera o .tar.gz
shasum -a 256 minha-lib-1.0.0.tar.gz        # o hash que o painel pede`, lang: 'bash' },
  {"p": "Hospede o `.tar.gz` onde quiser — um release do GitHub serve — e cole no painel o link `https://`, o sha256, o nome e uma descrição."},
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

const headings = [{ id: 'a-estrutura', text: "A estrutura", level: 2 as const }, { id: 'o-manifesto', text: "O manifesto", level: 2 as const }, { id: 'o-que-sai-do-pacote', text: "O que sai do pacote", level: 2 as const }, { id: 'empacotar', text: "Empacotar", level: 2 as const }, { id: 'publicar', text: "Publicar", level: 2 as const }, { id: 'versionar', text: "Versionar", level: 2 as const }, { id: 'testes', text: "Testes", level: 2 as const }, { id: 'mandar-para-o-registro-da-comunidade', text: "Mandar para o registro da comunidade", level: 2 as const }, { id: 'o-nome-e-de-quem-publicou-primeiro', text: "O nome é de quem publicou primeiro", level: 3 as const }, { id: 'todo-envio-passa-por-revisao', text: "Todo envio passa por revisão", level: 3 as const }, { id: 'um-registro-proprio', text: "Um registro próprio", level: 2 as const }];

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
