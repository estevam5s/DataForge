import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Erros comuns",
  description: "As armadilhas que mais custam tempo, e como sair delas.",
};

const blocos: Bloco[] = [
  {"h2": "`yield` retorna, não gera"},
  {"p": "`yield` encerra a ação imediatamente. Para produzir uma sequência, use `stream action` com `emit`:"},
  { code: `action f():
    yield 1        # devolve 1 e ENCERRA

stream action g():
    emit 1         # produz 1 e CONTINUA
    emit 2` },
  {"h2": "`//` virou comentário sem querer"},
  { code: `x := a // b        # isto é COMENTÁRIO — x fica sem valor
x := a ~/ b        # isto é divisão inteira` },
  {"p": "Regra: `//` só é divisão quando seguido de dígito, `(`, ou identificador que abre chamada/índice/membro. **Use `~/`.**"},
  {"h2": "`SyncError: Tab character detected`"},
  {"p": "DataForge exige **espaços**, nunca tabs. No VS Code: paleta de comandos → \"Convert Indentation to Spaces\"."},
  {"h2": "`SyncError: Indentation mismatch`"},
  {"p": "Um bloco tem recuo inconsistente — 3 espaços onde os outros usam 4, por exemplo. Use sempre 4 por nível, ou rode `dataforge fmt`."},
  {"h2": "Palavra reservada como nome"},
  { code: `no := 1        # ERRO: 'no' é o literal falso
nao := 1       # certo` },
  {"p": "As que mais pegam em português: `no`, `in`, `is`, `to`, `from`, `as`, `step`, `point`, `default`, `frame`, `stream`, `emit`, `forge`. A [lista completa](/referencia/palavras-reservadas) tem 81."},
  {"h2": "Esqueci o `self` num método"},
  { code: `blueprint Conta(saldo):
    action depositar(valor):
        saldo := saldo + valor          # ERRADO: mexe no escopo externo
        self.saldo := self.saldo + valor # certo` },
  {"h2": "`monitor` sem `handle` não engole o erro"},
  {"p": "Isso é intencional. Um `monitor:` seguido só de `ensure:` garante a limpeza mas **deixa o erro subir**. Se você quer silenciar, escreva o `handle` explicitamente."},
  {"h2": "Padrão de sequência não casa com vault"},
  { code: `match {"k": 1}:
    point [a]:          # NÃO casa — vault não é sequência
        yield "lista"
    point {"k": x}:     # casa
        yield "vault"` },
  {"h2": "A ordem dos `point` importa"},
  { code: `match n:
    point x:            # captura tudo
        yield "pegou tudo"
    point 5:            # INALCANÇÁVEL
        yield "nunca chega aqui"` },
  {"p": "Ordene do específico ao geral. Uma captura no topo engole todos os casos abaixo — e nenhum erro aparece, só o comportamento errado."},
  {"h2": "String simples não cruza linhas"},
  { code: `sql := """SELECT nome, preco
FROM produtos
WHERE preco > ?"""` },
  {"p": "Para SQL ou texto multilinha, use as aspas triplas."},
  {"h2": "Generator infinito com `to_cluster()`"},
  { code: `naturais().to_cluster()     # TRAVA — sequência infinita
naturais().take(10)         # certo` },
  {"h2": "Duas threads escrevendo na mesma variável"},
  {"p": "Perde atualizações silenciosamente. DataForge 4.0 não tem mutex — use [`channel`](/tecnicas/concorrencia), onde cada thread reporta o próprio resultado."},
  {"h2": "`cast` antes de validar"},
  { code: `# errado: dispara se não for número
idade := cast entrada as Integer

# certo
given not entrada.isdigit():
    yield {"erro": "idade nao numerica"}
idade := cast entrada as Integer` },
];

const headings = [{ id: 'yield-retorna-nao-gera', text: "`yield` retorna, não gera", level: 2 as const }, { id: 'virou-comentario-sem-querer', text: "`//` virou comentário sem querer", level: 2 as const }, { id: 'syncerror-tab-character-detected', text: "`SyncError: Tab character detected`", level: 2 as const }, { id: 'syncerror-indentation-mismatch', text: "`SyncError: Indentation mismatch`", level: 2 as const }, { id: 'palavra-reservada-como-nome', text: "Palavra reservada como nome", level: 2 as const }, { id: 'esqueci-o-self-num-metodo', text: "Esqueci o `self` num método", level: 2 as const }, { id: 'monitor-sem-handle-nao-engole-o-erro', text: "`monitor` sem `handle` não engole o erro", level: 2 as const }, { id: 'padrao-de-sequencia-nao-casa-com-vault', text: "Padrão de sequência não casa com vault", level: 2 as const }, { id: 'a-ordem-dos-point-importa', text: "A ordem dos `point` importa", level: 2 as const }, { id: 'string-simples-nao-cruza-linhas', text: "String simples não cruza linhas", level: 2 as const }, { id: 'generator-infinito-com-tocluster', text: "Generator infinito com `to_cluster()`", level: 2 as const }, { id: 'duas-threads-escrevendo-na-mesma-variavel', text: "Duas threads escrevendo na mesma variável", level: 2 as const }, { id: 'cast-antes-de-validar', text: "`cast` antes de validar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Erros comuns"}
      description={"As armadilhas que mais custam tempo, e como sair delas."}
      href={"/faq/erros-comuns"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
