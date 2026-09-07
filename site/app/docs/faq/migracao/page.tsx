import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Migração 3.x → 4.0",
  description: "O que mudou, o que quebrou e como atualizar.",
};

const blocos: Bloco[] = [
  {"h2": "O que quebra"},
  {"h3": "`//` agora é comentário por padrão"},
  {"p": "Esta é a **única** mudança que pode alterar o comportamento de código existente:"},
  { code: `x := a // b        # 3.x: divisão inteira · 4.0: COMENTÁRIO
x := 7 // 2        # 3.x e 4.0: divisão (dígito depois)
x := total // len(xs)  # 3.x e 4.0: divisão (chamada depois)` },
  {"p": "A correção é mecânica: troque por `~/` onde você quer divisão. O `dataforge fmt` já reimprime nessa grafia."},
  {"h3": "Três palavras deixaram de ser reservadas"},
  {"p": "`cluster`, `vault` e `range` viraram funções chamáveis. Isso **libera** nomes, não quebra nada."},
  {"h3": "Três palavras novas foram reservadas"},
  {"p": "`record`, `enum` e `when`. Se você usava alguma como nome de variável, precisa renomear."},
  { code: `dataforge check src/     # aponta todos os casos`, lang: 'bash' },
  {"h2": "O que foi corrigido"},
  {"p": "Comportamentos que estavam errados no 3.x e agora funcionam. Se seu código dependia do bug, ele muda:"},
  {"table": {"head": ["O que", "Antes", "Agora"], "rows": [["`yield` dentro de `monitor`", "era engolido pelo `handle`", "retorna da ação"], ["`monitor` sem `handle`", "engolia o erro", "deixa o erro subir"], ["`2 ** 3 ** 2`", "`64`", "`512` — associa à direita"], ["`-2 ** 2`", "`4`", "`-4`"], ["`f(1)` com 2 params", "ligava o resto a `void`", "erro de aridade"], ["`adopt X.Inexistente`", "devolvia vault vazio", "`ImportError_`"], ["`str(obj)`", "ignorava `toString`", "usa `toString`"], ["`defer` com erro", "não rodava", "roda em todo caminho"], ["transações SQLite", "`rollback` não desfazia", "funciona"]]}},
  {"h2": "O que é novo"},
  {"list": ["[Records](/docs/fundamentos/records) e [enums](/docs/fundamentos/enums)", "[Pattern matching estrutural](/docs/fundamentos/pattern-matching) com guardas", "[Interpolação](/docs/fundamentos/interpolacao) `$\"{x}\"`", "Ternário, `??`, `?.`, `in`/`not in`", "[Desestruturação](/docs/fundamentos/desestruturacao), [spread](/docs/fundamentos/spread), [compreensões](/docs/fundamentos/compreensoes)", "[Generators](/docs/fundamentos/generators) com `stream action` e `emit`", "[Análise estática](/docs/tecnicas/analise-estatica) e stack traces", "Imports seletivos e `relay` funcional", "Sete módulos novos na [biblioteca](/docs/biblioteca)", "Seis ferramentas: `check`, `test`, `fmt`, `lint`, `doc`, `init`"]},
  {"h2": "O roteiro de migração"},
  { code: `# 1. rodar a análise estática — ela aponta quase tudo
dataforge check src/

# 2. formatar — normaliza ~/ e o resto
dataforge fmt src/

# 3. rodar os testes
dataforge test

# 4. rodar o linter, para o que sobrou
dataforge lint src/`, lang: 'bash' },
  {"p": "Na prática, a maioria dos projetos precisa apenas do passo 1 e de trocar alguns `//` por `~/`."},
  {"h2": "Aproveitando o novo"},
  {"p": "Nada obriga a reescrever. Mas alguns padrões ficam bem mais curtos:"},
  { code: `# antes
out "Ola, " + nome + "! Voce tem " + str(idade) + " anos."
# agora
out $"Ola, {nome}! Voce tem {idade} anos."

# antes
given config isnt void and config["porta"] isnt void:
    porta := config["porta"]
otherwise:
    porta := 8080
# agora
porta := config?.porta ?? 8080

# antes
resultado := []
cycle n in nums:
    given n % 2 is 0:
        resultado.append(n * n)
# agora
resultado := [n * n cycle n in nums given n % 2 is 0]` },
];

const headings = [{ id: 'o-que-quebra', text: "O que quebra", level: 2 as const }, { id: 'o-que-foi-corrigido', text: "O que foi corrigido", level: 2 as const }, { id: 'o-que-e-novo', text: "O que é novo", level: 2 as const }, { id: 'o-roteiro-de-migracao', text: "O roteiro de migração", level: 2 as const }, { id: 'aproveitando-o-novo', text: "Aproveitando o novo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Migração 3.x → 4.0"}
      description={"O que mudou, o que quebrou e como atualizar."}
      href={"/docs/faq/migracao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
