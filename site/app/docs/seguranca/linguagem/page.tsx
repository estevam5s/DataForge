// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que a linguagem garante",
  description: "Segurança de tipos, de memória, limites de índice, ausência segura, dados imutáveis e padrões seguros — com a medida, e com o que fica de fora.",
};

const blocos: Bloco[] = [
  {"p": "Boa parte da segurança de um sistema é decidida antes de qualquer biblioteca: pelo que a **linguagem** torna impossível. Esta página é o inventário honesto disso — o que é garantido, o que é verificado, e o que continua por conta de quem escreve."},
  {"h2": "Segurança de memória"},
  {"p": "A classe de falha mais cara da história do software — estouro de buffer, uso após liberação, ponteiro pendurado — **não existe aqui**, e não por mérito da linguagem: o interpretador roda sobre o CPython, que gerencia a memória. Não há aritmética de ponteiro no caminho comum, não há `free`, e todo acesso a coleção é conferido."},
  {"table": {"head": ["Classe de falha", "Estado", "Porque"], "rows": [["estouro de buffer", "**impossível** no caminho comum", "coleções crescem; índice é conferido"], ["uso após liberação", "**impossível**", "não há liberação manual"], ["ponteiro pendurado", "**impossível**", "a contagem de referências segura o objeto"], ["dupla liberação", "**impossível**", "idem"], ["corrida de dados", "**possível**", "threads compartilham memória e nada é automático"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Há duas portas para fora dessa garantia, e as duas são explícitas", "texto": "`Arcane.C` (FFI) chama biblioteca nativa: dali para frente a segurança de memória é a do C, e um ponteiro errado derruba o processo. E `Arcane.Estrutura` trabalha sobre blocos de bytes — ali há ponteiro, aritmética e `liberar()`. As duas **conferem os limites** e recusam o nulo (`BufferOverflowError`, `NullPointerError`, `DanglingPointerError`), mas quem as usa saiu do jardim murado de propósito. Segurança de memória por gestão automática é o padrão; sair dela é uma escolha escrita no código."}},
  { code: `adopt Arcane.Estrutura as Est

bloco := Est.bloco(16)

// O limite e conferido — e o erro tem NOME, e nao um valor de lixo.
monitor:
    Cabecalho := Est.definir("Cabecalho", [["a", "u64"], ["b", "u64"],
        ["c", "u64"]], ordem := "rede")
    Cabecalho.ler(bloco)
    assert no
handle BufferOverflowError as e:
    out "recusado: o registro nao cabe no bloco"

// E o ponteiro nulo tambem:
p := Est.nulo()
monitor:
    p.ler()
    assert no
handle NullPointerError as e:
    out "recusado: ponteiro nulo"`, lang: 'df' },
  {"h2": "Segurança de tipos"},
  {"p": "A linguagem é **dinamicamente tipada com verificação estática opcional**. A distinção importa: o tipo não é apagado em execução — ele é conferido —, e o `check` prova antes de rodar o que consegue provar."},
  {"table": {"head": ["Confere", "Quando", "Código"], "rows": [["tipo declarado de variável e parâmetro", "execução **e** `check`", "`x: Integer := \"a\"`"], ["aridade da chamada, inclusive entre arquivos", "`check`", "`P.criar(1, 2, 3)`"], ["campo que não existe num record ou instância", "`check`, com sugestão", "`p.clientte`"], ["índice fora do alcance num literal fixo", "`check`", "`indice-fora-do-alcance`"], ["chave ausente num vault literal", "`check`, com sugestão", "`chave-ausente`"], ["limite de um genérico `<T extends X>`", "ambos", "`generic-bound`"], ["refinamento de um `type … where`", "toda fronteira", "`tipo-refinado`"]]}},
  { code: `// O refinamento vale em TODA fronteira — declaracao, parametro,
// retorno e campo. Um tipo que so valesse na criacao seria uma
// sugestao, e nao um tipo.
type Positivo := Integer where valor bigger 0

action dividir(total: Integer, partes: Positivo) -> Integer:
    yield total ~/ partes

assert dividir(10, 2) is 5

monitor:
    dividir(10, 0)
    assert no
handle Error as e:
    out "recusado na fronteira: 0 nao e Positivo"

// E o tipo OPACO e o que impede confundir dois textos. A regra
// vale na CRIACAO, entao um valor invalido nunca existe:
opaque type Cpf := String where len(valor) is 11

cpf := Cpf("12345678909")
assert cpf isnt void

monitor:
    Cpf("123")
    assert no
handle Error as e:
    out "recusado: um Cpf tem 11 digitos"

out "o tipo opaco separa dois textos que parecem iguais"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O que o analisador NÃO prova", "texto": "Ele é **otimista de propósito**: quando não consegue provar que algo está errado, fica calado. Um falso alarme ensina a ignorar mensagens, e um analisador ignorado não protege nada. Então ele cala sobre valor que vem de fora, sobre objeto sem anotação, sobre o que atravessa um decorador, e dentro de `monitor`/`retry` os erros viram aviso. **Isso não é segurança de tipos à moda de Rust** — é verificação parcial, e a diferença precisa estar clara para quem desenha o sistema."}},
  {"h2": "Ausência segura"},
  {"p": "`void` é um valor, não um ponteiro nulo — e ler um campo de `void` levanta `NullReferenceError`, com linha e coluna, em vez de corromper qualquer coisa. Os dois operadores que evitam o `given` defensivo são os mesmos do resto do mundo."},
  { code: `v := {"nome": "Ana"}

// '??' da o padrao quando o valor e void.
assert (v["idade"] ?? 0) is 0

// '?.' para a cadeia em vez de levantar.
endereco := void
assert endereco?.cidade is void

// E a distincao que o analisador conhece: depois de conferir,
// o tipo deixa de incluir void.
given v["nome"] isnt void:
    assert len(v["nome"]) is 3

out "ausencia tratada, e nao adivinhada"`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "A armadilha que o `??` esconde numa rota", "texto": "`query[\"x\"]` **sem** `??` dá 500 numa rota do Kiln: a query, o corpo e os cabeçalhos vêm de fora, a chave pode não vir, e indexar um vault sem a chave é erro. `params` é a exceção — se a rota casou, o parâmetro existe. É a diferença entre dado que você controla e dado que chegou pela rede, e ela aparece no código como um `??`."}},
  {"h2": "Dados imutáveis"},
  {"p": "Imutabilidade é um controle de segurança, e não só de estilo: um valor que não muda não pode ser alterado por outra parte do programa depois de conferido — o padrão *TOCTOU* (conferir e usar) simplesmente não acontece."},
  {"table": {"head": ["Forma", "O que ela garante"], "rows": [["`steady`", "o nome não é reatribuído"], ["`record`", "campos imutáveis, igualdade estrutural, `with` devolve cópia"], ["`freeze(xs)`", "um cluster que não muda"], ["`Objetos.congelar(obj)`", "a instância recusa escrita"], ["`Dom.valor(...)`", "objeto de valor com a regra cobrada na criação"]]}},
  { code: `record Permissao:
    papel: String
    acao: String

p := Permissao("editor", "escrever")

// Conferido uma vez, vale para sempre: nada muda o objeto depois.
monitor:
    p.papel := "admin"
    assert no
handle Error as e:
    out "recusado: record e imutavel"

// 'with' devolve um NOVO — o original continua o que era.
elevada := p with {"papel": "admin"}
assert p.papel is "editor"
assert elevada.papel is "admin"`, lang: 'df' },
  {"h2": "Padrões seguros — a lista"},
  {"table": {"head": ["Padrão", "A alternativa insegura que ele evita"], "rows": [["a indentação só aceita espaço", "o mesmo arquivo com significados diferentes"], ["`//` é comentário; divisão inteira é `~/`", "ambiguidade em código lido às pressas"], ["`record` é imutável por padrão", "compartilhar estado sem perceber"], ["campo com padrão mutável é **copiado** no `spawn`", "todas as instâncias dividirem a mesma lista"], ["`monitor` sem `handle` **não** engole o erro", "a falha sumir silenciosamente"], ["`defer` **não** engole erro", "um arquivo não fechado terminar com código 0"], ["`parallel` levanta o erro da tarefa que falhou", "um CI verde com metade do trabalho perdida"], ["`Crypto.hash_password` usa scrypt", "SHA-256 puro numa senha"], ["o `check` avisa sobre escrita concorrente", "perder atualizações em silêncio"]]}},
  {"h2": "Limites e recursos"},
  {"p": "A disponibilidade tem controles próprios na linguagem, e eles existem porque o caso comum é acidente e não ataque."},
  {"table": {"head": ["Limite", "O que ele impede"], "rows": [["teto de mil quadros de chamada", "recursão infinita comer a pilha (e `yield f(…)` vira salto)"], ["`Seg.json_seguro`", "aninhamento fundo estourar a pilha do leitor"], ["`Kiln.limite_de_corpo`", "um corpo gigante consumir a memória"], ["teto na fila do `Arcane.Laco`", "fonte mais rápida que o consumo morrer por memória"], ["`Arcane.Inicio.limite_da_pilha`", "o teto real da thread, e não o presumido"]]}},
];

const headings = [{ id: 'seguranca-de-memoria', text: "Segurança de memória", level: 2 as const }, { id: 'seguranca-de-tipos', text: "Segurança de tipos", level: 2 as const }, { id: 'ausencia-segura', text: "Ausência segura", level: 2 as const }, { id: 'dados-imutaveis', text: "Dados imutáveis", level: 2 as const }, { id: 'padroes-seguros-a-lista', text: "Padrões seguros — a lista", level: 2 as const }, { id: 'limites-e-recursos', text: "Limites e recursos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O que a linguagem garante"}
      description={"Segurança de tipos, de memória, limites de índice, ausência segura, dados imutáveis e padrões seguros — com a medida, e com o que fica de fora."}
      href={"/docs/seguranca/linguagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
