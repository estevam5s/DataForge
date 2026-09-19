# 265 — a superfície como contrato, e o alvo como restrição

Numa linguagem compilada, quebrar a **ABI** é trocar o layout de uma
struct ou a convenção de chamada. O sintoma é cruel: o programa
**carrega** e corrompe memória, longe da causa e sem nada denunciar.

Aqui não há layout binário a quebrar. E existe **exatamente o mesmo
problema**, com outro nome.

| Na linguagem compilada | Aqui |
|---|---|
| símbolo removido do `.so` | símbolo tirado do `relay` |
| assinatura trocada | aridade, nome ou tipo de parâmetro trocado |
| layout de struct mudado | campo acrescentado a um `record` |
| `soname` bump | versão **maior** no `forge.toml` |

**O sintoma também é o mesmo**: não é um erro de compilação de quem
publicou. O módulo novo compila, os testes dele passam, o pacote sobe. O
erro acontece na máquina de **quem consome**, depois — e a pessoa que vai
depurar não é a que causou.

## O que é contrato

A superfície respeita o `relay`. Um módulo que **declara** o que exporta
está dizendo que o resto é interno — e o que é interno não é contrato,
então mexer nele não quebra ninguém.

## As regras que quebram

| Regra | Por quê |
|---|---|
| `simbolo-removido` | quem o adotava para de compilar |
| `especie-trocada` | uma ação virou record: toda forma de uso muda |
| `aridade-incompativel` | uma chamada que era válida deixou de ser |
| `parametro-renomeado` | **a chamada com nome existe aqui** |
| `tipo-de-parametro` | quem passava o tipo antigo passa a ser recusado |
| `retorno-trocado` | o retorno **atravessa** a fronteira do `adopt` |
| `campo-removido` | todo acesso ao campo vira erro |

`parametro-renomeado` é a regra que uma ferramenta feita para C **não
precisaria ter**. Em C o argumento é posicional e o nome não sai do
cabeçalho; aqui `somar(a := 1, b := 2)` existe, então trocar `a` por `x`
quebra — e quebra em silêncio, porque o `check` de quem consome acusa um
nome que a pessoa nunca escreveu errado.

## O terceiro balde

Acrescentar um campo a um `record` quebra `Ponto(3, 4)` **se o campo não
tiver padrão**. Se tiver, é compatível. A superfície lê a declaração sem
executá-la e **não sabe qual dos dois é**.

Acusar quebra reprovaria um release correto; calar deixaria passar um que
quebra. O honesto é um **terceiro balde** — em destaque no relatório, e
que `--estrito` transforma em quebra para quem prefere o alarme.

Pelo mesmo motivo, **uma superfície que não compila não julga**:
`veredito` devolve `desconhecido` com o motivo. Um falso alarme aqui
reprova um release que está certo — e a segunda vez que isso acontece, a
conferência inteira é desligada.

## O mapa de símbolos

Num projeto de duzentos arquivos, *"de onde vem este nome?"* é a pergunta
que mais custa a responder à mão. Um ligador escreve isso num arquivo de
mapa; aqui ele sai do mesmo caminho que o `check` usa.

A linha que paga o mapa é `desconhecido`: um nome que nenhum `adopt`,
nenhuma declaração local e nenhum embutido provê é, quase sempre, um erro
de digitação, um `adopt` apagado, ou um nome que vem de um arquivo
vizinho que este não importa.

## Parte 19 — onde este programa roda

*Roda no navegador? numa função serverless? num WASI?* A resposta
dependia de alguém conhecer de cor o que cada ambiente suporta.

Seis alvos: `servidor`, `cli`, `navegador`, `wasi`, `funcao`,
`embarcado`. E cada ausência vem com **o motivo**, não só com um `não`:
threads no navegador dependem de `SharedArrayBuffer` e isolamento de
origem; soquete cru não existe numa aba; o WASI não tem `fork`.

**O vocabulário é o mesmo** de `Arcane.Capacidade`. Lá as capacidades são
cobradas em execução; aqui são lidas antes de rodar. É a mesma pergunta
feita de dois lados — e usar dois vocabulários faria as duas respostas
divergirem no primeiro módulo novo.

## O limite, dito em voz alta

**A leitura é estática, e sai dos `adopt` de um arquivo.**

- um módulo alcançado **indiretamente** não aparece;
- `adopt Python.x` conta como `python` e para aí;
- um `roda` quer dizer **"não achei impedimento por esta via"**, e não
  "vai funcionar".

## WebAssembly, com precisão

**Compilar para WASM** é produzir um `.wasm` com as funções da sua
linguagem — e isso **não existe** aqui. **Rodar em WASM** é rodar o
interpretador dentro de um runtime WASM — e isso **funciona**, pelo
Pyodide, que compila o CPython para WebAssembly.

Quem chama a segunda de "DataForge compila para WASM" está descrevendo
outra coisa, e a diferença aparece no tamanho do artefato: o
interpretador inteiro vai junto, alguns megabytes antes da primeira
linha.

Emitir um `.wasm` parcial "só para dizer que emite" seria uma caixa que
se marca: ele não rodaria nenhum programa do repositório. A parte 8 já
mostrou o que acontece quando se mede em vez de supor — a otimização que
"devia" render, rendeu **1,01×**.
