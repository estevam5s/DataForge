// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_informacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Entrada e saída",
  description: "Validação de entrada, codificação de saída e serialização segura — as três que respondem pela maioria das falhas exploradas.",
};

const blocos: Bloco[] = [
  {"p": "A maior parte das falhas exploradas na prática cabe em uma frase: **dado de fora tratado como código**. As três defesas são independentes e nenhuma substitui as outras."},
  {"h2": "Validar na entrada"},
  {"p": "Validação responde *este valor é aceitável?* — e a resposta certa a um valor inaceitável é **recusar**, não consertar. Consertar cria o segundo problema: duas versões do mesmo dado, e a conferência feita sobre a errada."},
  {"table": {"head": ["Conferir", "A função", "O que passa despercebido sem ela"], "rows": [["número e faixa", "`Seg.numero_seguro`", "`?pagina=-1`, `?tamanho=999999999`"], ["JSON", "`Seg.json_seguro`", "dez mil níveis de aninhamento"], ["URL de fora", "`Seg.url_segura`", "SSRF para `169.254.169.254`"], ["caminho de arquivo", "`Seg.caminho_seguro`", "`../../etc/passwd`, e o link simbólico"], ["nome de arquivo", "`Seg.nome_de_arquivo_seguro`", "`CON.txt`, e a marca que inverte a leitura"], ["destino de redirecionamento", "`Seg.redirecionamento_seguro`", "`//banco-falso.exemplo`"], ["texto", "`Seg.sem_controle`", "caracteres invisíveis de direção de escrita"], ["esquema de formulário", "`Kiln.validar`, `Lavra.validar`", "campo ausente tratado como vazio"]]}},
  { code: `adopt Arcane.Seguranca as Seg

// Travessia: o 'realpath' antes de comparar e o que fecha o buraco.
// Sem ele, um link simbolico dentro da pasta aponta para fora e a
// comparacao de texto aprova.
monitor:
    Seg.caminho_seguro("/tmp/uploads", "../../etc/passwd")
    assert no
handle UnsafeInputError as e:
    out "travessia recusada"

// E o byte nulo, que e a forma classica de truncar o nome DEPOIS
// da conferencia de extensao.
monitor:
    Seg.caminho_seguro("/tmp/uploads", "foto.png\\u0000.php")
    assert no
handle Error as e:
    out "byte nulo recusado"

// Nome de arquivo: '..' some, e o nome reservado do Windows ganha
// prefixo — criar 'CON.txt' falha la e funciona aqui.
assert Seg.nome_de_arquivo_seguro("../../etc/passwd") is "passwd"
assert Seg.nome_de_arquivo_seguro("CON.txt") is "_CON.txt"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Lista de permitidos, sempre", "texto": "Uma lista de proibidos é uma aposta de que se pensou em tudo, e a história do XSS é a lista dos que não pensaram: `<svg onload>`, `<math>`, `javascript:` com tabulação no meio, entidade HTML dentro do atributo. A lista de permitidos erra para o lado de **perder uma tag legítima** — que é um bug visível, relatado no mesmo dia. É por isso que `Seg.limpar_html` recebe as tags que passam, e não as que não passam."}},
  {"h2": "Codificar na saída"},
  {"p": "Codificação responde *para onde este texto vai?* — e a resposta muda a função. O que protege uma página HTML não protege uma linha de shell, e o que protege shell estraga um CSV."},
  {"table": {"head": ["Destino", "Função", "O que ela fecha"], "rows": [["corpo HTML", "`escapar_html`", "XSS refletido e armazenado"], ["atributo HTML", "`escapar_atributo`", "atributo sem aspas, onde o espaço é o fim do valor"], ["dentro de `<script>`", "`escapar_js`", "`</script>` no meio de uma string fechando a tag"], ["URL", "`escapar_url`", "parâmetro que vira outro parâmetro"], ["linha de shell", "`escapar_shell`", "injeção de comando"], ["`LIKE` do SQL", "`escapar_sql_like`", "`%` do usuário virando curinga *(não é defesa contra injeção)*"], ["célula de planilha", "`escapar_csv`", "injeção de fórmula"], ["cabeçalho HTTP", "`escapar_cabecalho`", "injeção de cabeçalho por CRLF"], ["linha de log", "`escapar_log`", "log forjado"], ["expressão regular", "`escapar_regex`", "padrão do usuário virando metacaractere"]]}},
  { code: `adopt Arcane.Seguranca as Seg

// 1. O caso que mais engana: o texto do usuario vai DENTRO de um
//    <script>. Escapar aspas nao resolve — '</script>' fecha a tag
//    antes de o JavaScript ser lido, e o resto da pagina vira codigo.
perigoso := "</script><script>roubar()</script>"
assert "</script>" not in Seg.escapar_js(perigoso)

// 2. A injecao que quase ninguem escapa: o Excel EXECUTA a celula
//    que comeca com '=', '+', '-' ou '@'.
assert Seg.escapar_csv("=HYPERLINK(\\"http://mau\\")")[0:1] is "'"
assert Seg.escapar_csv("Ana Souza") is "Ana Souza"

// 3. O log forjado: um '\\n' num campo acrescenta uma LINHA inteira,
//    e a investigacao seguinte le um evento que nunca aconteceu.
forjado := "ana\\n2026-01-01 INFO admin apagou tudo"
assert "\\n" not in Seg.escapar_log(forjado)

// 4. E o cabecalho, onde o CRLF injeta outro cabecalho.
assert Seg.escapar_cabecalho("/painel\\r\\nSet-Cookie: admin=1") is "/painelSet-Cookie: admin=1"

out "quatro destinos, quatro funcoes"`, lang: 'df' },
  {"h2": "Serializar e desserializar"},
  {"p": "Desserialização insegura é a falha que mais surpreende, porque a operação parece passiva. Em linguagens onde o formato carrega **tipos** — `pickle` do Python, a serialização nativa do Java —, ler um arquivo é executar código."},
  {"callout": {"tipo": "dica", "titulo": "Aqui essa classe não existe, e o motivo é o formato", "texto": "`Arcane.Serialization` e `Objetos.de_json` trabalham com **JSON**, que carrega dados e não tipos. Não há construtor a invocar na leitura, então não há execução a sequestrar. A ponte para o Python (`adopt Python.pickle`) reabre a porta — e ali a responsabilidade volta a ser de quem escreveu."}},
  {"p": "O que **continua** sendo sua responsabilidade é a **forma** do que chegou: JSON válido não quer dizer JSON esperado."},
  { code: `adopt Arcane.Seguranca as Seg
adopt Arcane.Objetos as Obj

record Pedido:
    id: Integer
    total: Integer

// 1. Teto de tamanho, profundidade e numero de chaves ANTES de ler.
//    Um '[[[[[...]]]]]' de dez mil niveis estoura a pilha de quem le,
//    e o leitor padrao aceita: e negacao de servico com 50 KB.
cru := Seg.json_seguro("{\\"id\\": 7, \\"total\\": 199}")

// 2. O dado NUNCA escolhe o tipo. A lista de tipos e argumento,
//    e as invariantes sao conferidas na chegada.
pedido := Obj.de_vault(cru, [Pedido])
assert pedido.id is 7

// 3. E o inverso, para gravar.
assert Obj.para_vault(pedido)["total"] is 199

out "o formato nao executa, e a forma e conferida"`, lang: 'df' },
  {"table": {"head": ["Regra", "Porque"], "rows": [["o dado nunca escolhe a classe", "`Objetos.de_vault` exige a lista de tipos como argumento"], ["`setup` não roda na desserialização", "construtor é código; a chegada não o invoca"], ["as invariantes são conferidas na chegada", "um objeto inválido nunca existe"], ["tamanho e profundidade antes de interpretar", "a defesa tem de vir antes do trabalho"]]}},
];

const headings = [{ id: 'validar-na-entrada', text: "Validar na entrada", level: 2 as const }, { id: 'codificar-na-saida', text: "Codificar na saída", level: 2 as const }, { id: 'serializar-e-desserializar', text: "Serializar e desserializar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Entrada e saída"}
      description={"Validação de entrada, codificação de saída e serialização segura — as três que respondem pela maioria das falhas exploradas."}
      href={"/docs/seguranca/entrada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
