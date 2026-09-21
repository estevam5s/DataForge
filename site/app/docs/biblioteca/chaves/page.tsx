// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/chaves.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Chaves",
  description: "Ciclo de vida de chave criptográfica: propósito cobrado, prazo, rotação que mantém as antigas decifrando o passado, identificador no dado cifrado, cifragem em envelope (DEK/KEK), recifragem, derivação por contexto (HKDF) e exportação do cofre cifrada pela senha mestra.",
};

const blocos: Bloco[] = [
  {"p": "`Arcane.Crypto` gera bytes aleatórios e cifra com eles. O que ele não tem é o **ciclo de vida**: de onde a chave veio, até quando vale, para que serve, e o que fazer com o dado cifrado pela versão anterior."},
  {"p": "Sem isso, o que acontece na prática é sempre o mesmo: uma chave nasce numa variável de ambiente, é usada para tudo, e **nunca é trocada** — porque trocá-la tornaria ilegível tudo que já foi cifrado."},
  { code: `adopt Arcane.Chaves as Ch

cofre := Ch.cofre()
k := cofre.gerar("sessao", proposito := "assinar", prazo := 86400.0)

assert len(Ch.usar(k, "assinar")) is 32

// O proposito e COBRADO: uma chave por finalidade impede que um
// comprometimento vire todos os comprometimentos.
monitor:
    Ch.usar(k, "cifrar")
handle CryptoKeyError as e:
    out "recusado: esta chave e de 'assinar'"

// E o material nao aparece em texto — o vazamento mais comum e
// alguem imprimir o objeto para depurar.
out k          // <chave SvJsJypGwyqR (assinar)>`, title: `propósito e prazo` },
  {"h2": "Rotação: a antiga continua lendo"},
  {"p": "Esta é a decisão que torna a rotação possível na prática. Se trocar a chave tornasse ilegível o que já foi cifrado, ninguém trocaria — e é exatamente o que acontece na maioria dos sistemas."},
  { code: `adopt Arcane.Chaves as Ch

cofre := Ch.cofre()
cofre.gerar("mestra", proposito := "cifrar")

envelope := cofre.envelopar("um terabyte de dados", "mestra")

// Rotaciona: a nova passa a ser a ativa, e a antiga fica aposentada.
nova := cofre.rotacionar("mestra", "cifrar")

// O dado antigo continua legivel — o envelope carrega o 'kid'.
out Ch.e_chave(nova)
assert cofre.desenvelopar(envelope) isnt void

// E recifrar troca a chave sem tocar nos dados.
novo := cofre.recifrar(envelope, "mestra")
assert novo["kid"] is nova.kid`, title: `rotacionar` },
  {"callout": {"tipo": "dica", "titulo": "Envelope: por que a DEK existe", "texto": "Cifrar um terabyte com a chave mestra significa que rotacioná-la é **reescrever o terabyte**. Com envelope, cada objeto tem a sua chave de dados (DEK), e o que a chave mestra (KEK) cifra é só a DEK — 32 bytes. Rotacionar a mestra passa a ser recifrar as DEKs. É o que KMS, Vault e as três nuvens fazem, e o motivo é este."}},
  {"h2": "O momento único de atualizar"},
  { code: `adopt Arcane.Chaves as Ch

cofre := Ch.cofre()
cofre.gerar("curta", proposito := "cifrar", prazo := 3600.0)
cofre.gerar("longa", proposito := "cifrar", prazo := 99999999.0)

// Uma chave que vence sem ninguem saber derruba o sistema numa
// madrugada. O aviso e o que transforma isso em tarefa.
perto := cofre.precisa_rotacionar(aviso := 7200.0)
cycle c in perto:
    out $"   rotacionar '{c['rotulo']}' ({c['kid']})"`, title: `avisar antes` },
  {"h2": "O que ele NÃO é"},
  {"table": {"head": ["Não é", "Porque"], "rows": [
      ["um **HSM** ou **KMS**", "o material vive na memória deste processo, e quem lê a memória lê a chave. Um HSM existe justamente para que a chave nunca saia dele — e isso é hardware, não biblioteca"],
      ["persistente sozinho", "`exportar()` devolve o cofre cifrado pela senha mestra, e gravar é decisão de quem chama. Um cofre que escolhesse onde gravar escolheria errado em metade dos casos"],
      ["assimétrico", "RSA e curva elíptica em Python puro são lentas e são exatamente onde um erro de implementação vira falha silenciosa. Para assinatura com prova perante terceiro, um serviço"]
    ]}},
  {"callout": {"tipo": "atencao", "titulo": "Um decifrar que devolve nada é pior que um que levanta", "texto": "`cifra.abrir` devolve `void` quando a etiqueta do AEAD não fecha — defensável numa primitiva, onde quem chama decide. Aqui isso é convertido em **erro**: um `desenvelopar` que devolvesse `void` faria o programa acima gravar nada onde havia um dado, ou tratar a ausência como conteúdo vazio. A falha de integridade é o assunto todo do AEAD, e ela tem de ser barulhenta."}},
  {"p": "As primitivas: [Arcane.Crypto](/docs/biblioteca/crypto). Guia: [Autenticação](/docs/seguranca/autenticacao)."},
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`ESTADOS`", "`[\"ativa\", \"aposentada\", \"revogada\"]`"], ["`PROPOSITOS`", "`[\"assinar\", \"cifrar\", \"derivar\", \"autenticar\"]`"]]}},
  {"h2": "Funções (4)"},
  {"table": {"head": ["Assinatura"], "rows": [["`cofre(opcoes=None)`"], ["`derivar_de(chave, contexto, tamanho=32)`"], ["`e_chave(v)`"], ["`usar(chave, proposito)`"]]}},
];

const headings = [{ id: 'rotacao-a-antiga-continua-lendo', text: "Rotação: a antiga continua lendo", level: 2 as const }, { id: 'o-momento-unico-de-atualizar', text: "O momento único de atualizar", level: 2 as const }, { id: 'o-que-ele-nao-e', text: "O que ele NÃO é", level: 2 as const }, { id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-4', text: "Funções (4)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Chaves"}
      description={"Ciclo de vida de chave criptográfica: propósito cobrado, prazo, rotação que mantém as antigas decifrando o passado, identificador no dado cifrado, cifragem em envelope (DEK/KEK), recifragem, derivação por contexto (HKDF) e exportação do cofre cifrada pela senha mestra."}
      href={"/docs/biblioteca/chaves"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
