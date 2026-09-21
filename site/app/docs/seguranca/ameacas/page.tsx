// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ameaças e risco",
  description: "Modelagem de ameaças com STRIDE, superfície de ataque, fronteiras de confiança e de segurança, gestão de risco e políticas.",
};

const blocos: Bloco[] = [
  {"p": "Modelar ameaças é responder quatro perguntas, nesta ordem: **o que estamos construindo**, **o que pode dar errado**, **o que vamos fazer**, e **fizemos um bom trabalho?** Pular a primeira é o erro mais comum — sem o desenho do sistema, a lista de ameaças vira uma lista de medos."},
  {"h2": "STRIDE"},
  {"p": "Seis categorias que cobrem praticamente tudo o que se faz contra um sistema. O valor delas é serem **exaustivas o bastante** para a reunião terminar."},
  {"table": {"head": ["", "A ameaça", "A propriedade que ela viola", "A resposta aqui"], "rows": [["**S**poofing", "fingir ser outro", "autenticação", "`hash_password` com scrypt, TOTP, token assinado"], ["**T**ampering", "alterar dado em trânsito ou em repouso", "integridade", "AEAD, HMAC, `Seg.auditoria`"], ["**R**epudiation", "negar ter feito", "não-repúdio", "trilha encadeada — e a ressalva sobre chave simétrica"], ["**I**nformation disclosure", "ver o que não devia", "confidencialidade", "`Seg.segredo`, `redigir`, `mascarar_pii`"], ["**D**enial of service", "impedir o uso legítimo", "disponibilidade", "`limitador`, `json_seguro`, limite de corpo"], ["**E**levation of privilege", "virar admin sem ser", "autorização", "RBAC por recurso, `Arcane.Capacidade`"]]}},
  {"h2": "Superfície de ataque"},
  {"p": "É a soma de todos os pontos por onde um dado de fora entra no sistema. Reduzi-la é a única medida que melhora **todas** as outras ao mesmo tempo — o que não existe não pode ser atacado."},
  {"table": {"head": ["Ponto de entrada", "O que costuma escapar", "A peça"], "rows": [["parâmetro de rota e query", "faixa não conferida, tipo assumido", "`Seg.numero_seguro`"], ["corpo do pedido", "JSON fundo demais, corpo gigante", "`Seg.json_seguro`, `Kiln.limite_de_corpo`"], ["cabeçalho", "`Host` e `X-Forwarded-For` tratados como verdade", "conferir contra uma lista"], ["upload", "nome com `..`, extensão, tamanho", "`Kiln.salvar_upload`, `Seg.nome_de_arquivo_seguro`"], ["URL fornecida pelo usuário", "SSRF para a rede interna", "`Seg.url_segura`"], ["redirecionamento", "`?proximo=` para fora do site", "`Seg.redirecionamento_seguro`"], ["arquivo de configuração", "segredo commitado", "`dataforge seguranca`"], ["dependência", "pacote trocado numa versão publicada", "`forge.lock` com sha256"]]}},
  { code: `adopt Arcane.Seguranca as Seg

// A superficie de uma rota, em quatro linhas. Cada uma fecha um
// ponto que um pedido de fora alcanca.
action listar(query):
    pagina := Seg.numero_seguro(query["pagina"] ?? "1", 1, 10000)
    por_pagina := Seg.numero_seguro(query["tamanho"] ?? "20", 1, 100)
    busca := Seg.sem_controle(query["q"] ?? "")
    yield {"pagina": pagina, "tamanho": por_pagina, "busca": busca}

assert listar({"pagina": "3"})["pagina"] is 3
assert listar({})["tamanho"] is 20

// '?tamanho=999999999' derruba a listagem, e passa por qualquer
// conversao que nao confira a faixa.
monitor:
    listar({"tamanho": "999999999"})
    assert no
handle UnsafeInputError as e:
    out "recusado antes de chegar ao banco"`, lang: 'df' },
  {"h2": "Fronteira de confiança, fronteira de segurança"},
  {"p": "São conceitos diferentes e a confusão entre eles custa caro. Uma **fronteira de confiança** é onde o nível de confiança muda — o dado atravessa e passa a ser suspeito. Uma **fronteira de segurança** é onde existe um mecanismo que **obriga** a separação."},
  {"table": {"head": ["Fronteira", "Tipo", "O que ela garante"], "rows": [["navegador → servidor", "confiança **e** segurança", "processos e máquinas diferentes"], ["processo → processo", "ambas", "o sistema operacional isola a memória"], ["`Arcane.Capacidade`", "**só de confiança**", "recusa o `adopt`; não tira o que já foi entregue"], ["thread → thread", "**nenhuma**", "memória compartilhada; nada isola"], ["validação de entrada", "**só de confiança**", "depende de quem escreveu chamar a função"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Tratar uma de confiança como de segurança é a falha clássica", "texto": "`Arcane.Capacidade` bloqueia a **autoridade ambiente** — o `adopt` de um módulo fora da lista — e o próprio módulo diz isso em execução, por `limites()`. Ele **não é um sandbox**: código malicioso que já recebeu um objeto de arquivo continua usando-o. Um módulo chamado *Sandbox* que prometesse contenção seria usado onde não pode, e a descoberta viria por incidente. Contenção de verdade é processo separado, contêiner ou VM."}},
  {"h2": "Gestão de risco"},
  {"p": "Risco é **probabilidade × impacto**, e o ponto de fazer a conta é ordenar — não há orçamento para tratar tudo. As quatro respostas possíveis são sempre as mesmas."},
  {"table": {"head": ["Resposta", "Quando", "Exemplo"], "rows": [["**Mitigar**", "o controle custa menos que o dano esperado", "limite de taxa no login"], ["**Transferir**", "outro faz melhor e responde por isso", "TLS no Caddy; pagamentos num PSP"], ["**Evitar**", "a funcionalidade não paga o risco", "não guardar o número do cartão"], ["**Aceitar**", "residual pequeno, e **registrado**", "o `.deb` não é assinado; está escrito"]]}},
  {"callout": {"tipo": "dica", "titulo": "Aceitar é uma decisão, não um silêncio", "texto": "A diferença entre risco aceito e risco esquecido é **um registro com data e nome**. Este repositório faz isso no código: `Arcane.Ecossistema.o_que_nao_existe()` lista os cinco componentes ausentes com o motivo, e `Arcane.Principios` traz os dez princípios com veredito — cinco cumpridos, quatro parciais, um que não se aplica. Um relatório que aprovasse os dez seria a prova de que ninguém o leu."}},
  {"h2": "Políticas"},
  {"p": "Uma política que ninguém consegue verificar é um documento. As que funcionam viram **verificação automática** — e o lugar delas é a esteira de CI."},
  { code: `// Uma politica executavel: a esteira reprova o que a
// politica proibe, e ninguem precisa lembrar de conferir.

// 1. Nenhum segredo entra no repositorio.
//    $ dataforge seguranca . --strict

// 2. O analisador nao deixa passar erro.
//    $ dataforge check . --strict

// 3. Estilo e higiene.
//    $ dataforge lint .

// 4. A suite inteira, com piso de cobertura.
//    $ dataforge test tests/ --cobertura --minimo=80

// 5. A superficie nao quebrou sem o bump correspondente.
//    $ dataforge abi antes.df depois.df`, lang: 'df' },
  {"table": {"head": ["Política", "O comando que a cobra"], "rows": [["segredo nunca entra no repositório", "`dataforge seguranca . --strict`"], ["nenhum erro do analisador", "`dataforge check . --strict`"], ["cobertura mínima", "`dataforge test --cobertura --minimo=80`"], ["a versão sobe quando a superfície quebra", "`dataforge abi`"], ["as dependências são as do lockfile", "`dataforge install`"]]}},
];

const headings = [{ id: 'stride', text: "STRIDE", level: 2 as const }, { id: 'superficie-de-ataque', text: "Superfície de ataque", level: 2 as const }, { id: 'fronteira-de-confianca-fronteira-de-seguranca', text: "Fronteira de confiança, fronteira de segurança", level: 2 as const }, { id: 'gestao-de-risco', text: "Gestão de risco", level: 2 as const }, { id: 'politicas', text: "Políticas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ameaças e risco"}
      description={"Modelagem de ameaças com STRIDE, superfície de ataque, fronteiras de confiança e de segurança, gestão de risco e políticas."}
      href={"/docs/seguranca/ameacas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
