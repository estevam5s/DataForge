// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A consulta",
  description: "A linguagem que o cliente escreve: busca, mudança, assinatura, apelidos, trechos, variáveis, diretivas e introspecção.",
};

const blocos: Bloco[] = [
  {"p": "A consulta é um **texto** — ela atravessa a rede. A escrita é indentada, como a linguagem, e o `:` no fim marca que aquele campo tem seleção dentro."},
  {"h2": "As três operações"},
  {"table": {"head": ["Operação", "Para quê"], "rows": [["`busca`", "ler — sem efeito colateral"], ["`mudanca`", "escrever — o efeito aparece no nome"], ["`assinatura`", "acompanhar — o servidor empurra cada novo valor"]]}},
  {"p": "A separação não é burocracia. Quem lê a consulta sabe, **sem abrir o resolvedor**, se aquilo muda alguma coisa — e é o que permite a um intermediário guardar em cache uma `busca` e nunca uma `mudanca`."},
  { code: `busca:
    usuario(id: 1):
        nome

mudanca:
    criarUsuario(dados: {nome: "Ana", email: "ana@forja.co"}):
        id

assinatura:
    pedidoCriado:
        numero
        total`, lang: 'lavra' },
  {"h2": "Campos e argumentos"},
  { code: `busca:
    pedidos(limite: 10, ordem: Recente, ativo: yes):
        numero
        itens:
            quantidade
            produto:
                nome`, lang: 'lavra' },
  {"p": "Um campo **sem** seleção é uma folha (`numero`); um **com** seleção termina em `:`. É a mesma regra do bloco na linguagem, e o erro de esquecer os dois pontos diz isso."},
  {"p": "Os valores aceitos são os da linguagem: texto entre aspas, número, `yes`/`no`/`void`, `[lista]`, `{vault}`, `$variavel` e o nome de um membro de enum."},
  {"h2": "Apelidos"},
  { code: `busca:
    ana: usuario(id: 1):
        nome
    bia: usuario(id: 2):
        nome`, lang: 'lavra' },
  { code: `{ana: {nome: Ana}, bia: {nome: Bia}}`, lang: 'text' },
  {"p": "Sem apelido, os dois `usuario` colidiriam na resposta. É também como se pede o mesmo campo com argumentos diferentes na mesma consulta."},
  {"h2": "Trechos"},
  {"p": "Um **trecho** é um pedaço de seleção com nome. Ele existe para não repetir a mesma lista de campos em cinco lugares — e para que mudá-la seja uma edição só."},
  { code: `trecho Basico em Usuario:
    id
    nome
    email

busca:
    ana: usuario(id: 1):
        ...Basico
    bia: usuario(id: 2):
        ...Basico
        criado_em`, lang: 'lavra' },
  {"p": "O `em Usuario` diz a que tipo ele se aplica, e é o que permite **conferi-lo antes de rodar**: um trecho de `Usuario` usado num `Produto` é recusado pela validação."},
  {"callout": {"tipo": "nota", "titulo": "O mesmo campo duas vezes vira um", "texto": "`...Basico` mais `nome` escrito à mão pedem `nome` duas vezes. O Lavra junta os dois numa seleção só. Sem juntar, a segunda apagaria a primeira no vault — e aí a **ordem** da consulta mudaria o resultado."}},
  {"h2": "Trecho condicional"},
  {"p": "Para união e contrato: pedir o que só existe num dos tipos."},
  { code: `busca:
    acervo:
        titulo
        ... em Video:
            minutos
        ... em Podcast:
            episodio`, lang: 'lavra' },
  {"h2": "Variáveis"},
  {"p": "A consulta é uma só; o valor muda. É o que permite guardá-la como constante no cliente em vez de montá-la com concatenação — que é de onde vem injeção."},
  { code: `busca Painel($id: Integer!, $limite: Integer := 3):
    usuario(id: $id):
        nome
        pedidos(limite: $limite):
            numero`, lang: 'lavra' },
  { code: `r := Lavra.executar(esq, consulta, variaveis := {"id": 7})`, lang: 'df' },
  {"table": {"head": ["Declaração", "O que acontece se não vier"], "rows": [["`$id: Integer!`", "a consulta é recusada"], ["`$id: Integer`", "chega como `void`"], ["`$id: Integer := 3`", "chega como `3`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A validação confere o tipo da variável", "texto": "Passar `$nome: String` para um argumento `Integer!` é recusado **antes** de executar, com as duas declarações na mensagem. E uma variável declarada e nunca usada também é apontada — ela costuma ser o resto de uma edição pela metade."}},
  {"h2": "Diretivas"},
  { code: `busca Talvez($detalhado: Boolean!):
    usuario(id: 1):
        nome
        email @incluir(se: $detalhado)
        telefone @pular(se: $detalhado)`, lang: 'lavra' },
  {"p": "`@incluir(se:)` põe o campo quando a condição é verdadeira; `@pular(se:)` tira. Servem para uma consulta só atender a duas telas — a compacta e a completa — sem duas versões dela para divergirem."},
  {"p": "Diretivas próprias entram no esquema:"},
  { code: `action so_admin(args, ctx):
    yield ctx["papel"] is "admin"

Lavra.diretiva(esq, "admin", so_admin)`, lang: 'df' },
  { code: `busca:
    usuario(id: 1):
        nome
        cpf @admin`, lang: 'lavra' },
  {"p": "É o gancho para `@admin`, `@experimento(nome: …)` e afins — sem espalhar `given` por dentro de cada resolvedor."},
  {"h2": "Introspecção"},
  {"p": "O esquema se descreve, e é ele mesmo quem responde:"},
  { code: `busca:
    __tipo(nome: "Pedido")`, lang: 'lavra' },
  { code: `busca:
    __esquema`, lang: 'lavra' },
  {"p": "Sem introspecção, um cliente precisa de documentação ao lado para saber o que pedir — e essa documentação envelhece em silêncio. Com ela, o editor completa o campo e a página de referência é **gerada** do que está no ar."},
  {"p": "A resposta vem do **mesmo objeto** que executa. Não há um segundo lugar descrevendo o esquema para divergir do primeiro."},
  {"callout": {"tipo": "atencao", "titulo": "Desligue em produção", "texto": "`Lavra.introspeccao(esq, no)` tira `__esquema` e `__tipo`. Um esquema exposto é um mapa do que existe para quem for procurar, e quem precisa dele é o time — que pode lê-lo do repositório."}},
  {"h2": "Os erros de consulta dizem a linha"},
  { code: `erro: 'Usuario' não tem o campo 'nomee'
  linha 3
  dica: você quis dizer 'nome'?`, lang: 'text' },
  {"p": "E **todos de uma vez**: um validador que para no primeiro erro faz corrigir uma linha por tentativa. Com dez numa resposta, corrigem-se as dez."},
];

const headings = [{ id: 'as-tres-operacoes', text: "As três operações", level: 2 as const }, { id: 'campos-e-argumentos', text: "Campos e argumentos", level: 2 as const }, { id: 'apelidos', text: "Apelidos", level: 2 as const }, { id: 'trechos', text: "Trechos", level: 2 as const }, { id: 'trecho-condicional', text: "Trecho condicional", level: 2 as const }, { id: 'variaveis', text: "Variáveis", level: 2 as const }, { id: 'diretivas', text: "Diretivas", level: 2 as const }, { id: 'introspeccao', text: "Introspecção", level: 2 as const }, { id: 'os-erros-de-consulta-dizem-a-linha', text: "Os erros de consulta dizem a linha", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A consulta"}
      description={"A linguagem que o cliente escreve: busca, mudança, assinatura, apelidos, trechos, variáveis, diretivas e introspecção."}
      href={"/docs/lavra/consulta"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
