import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Análise estática",
  description: "O que o dataforge check encontra antes de executar, e por que ele é otimista.",
};

const blocos: Bloco[] = [
  {"h2": "Três etapas sem executar"},
  { code: `dataforge check meu_programa.df
dataforge check src/ --strict      # avisos também falham
dataforge check x.df --syntax-only # só a sintaxe`, lang: 'bash' },
  {"list": ["**Léxica** — o arquivo é um DataForge válido?", "**Sintática** — a estrutura faz sentido?", "**Semântica** — os nomes existem? as chamadas batem? os tipos combinam?"]},
  {"h2": "O que ele encontra"},
  {"table": {"head": ["Categoria", "Exemplo", "Mensagem"], "rows": [["nome indefinido", "`sommar(1, 2)`", "*Did you mean `somar`?*"], ["aridade", "`somar(1)`", "*is missing argument(s): b*"], ["tipo de argumento", "`somar(\"x\", 2)`", "*expects Integer but got String*"], ["tipo de variável", "`x: Integer := \"texto\"`", "*Declared as Integer but the value is String*"], ["tipo inexistente", "`x: Intger := 1`", "*Did you mean `Integer`?*"], ["constante reatribuída", "`LIMITE := 200`", "*Cannot reassign the steady constant*"], ["operador incompatível", "`1 + [2]`", "*Cannot add Integer and Cluster*"], ["campo de record", "`p.emial`", "*Record has no field. Fields: nome, idade*"], ["membro de enum", "`Status.Cancelado`", "*Members: Ativo, Inativo*"], ["código inalcançável", "linha após `yield`", "*Unreachable code* (aviso)"], ["retorno ausente", "`-> Integer` sem `yield`", "*can end without a yield* (aviso)"], ["`halt` fora de laço", "", "*halt outside of a loop*"]]}},
  {"h2": "Um exemplo"},
  { code: `app.df:5:1: erro: Cannot reassign the steady constant 'LIMITE'
    sugestão: Use another name, or drop 'steady' from the declaration
app.df:9:11: erro: Parameter 'a' of 'somar' expects Integer but got String
    sugestão: Pass a Integer
app.df:10:5: erro: Undefined action 'sommar'
    sugestão: Did you mean 'somar'?

✗ 3 erro(s), 0 aviso(s)`, lang: 'text' },
  {"p": "Cada diagnóstico traz **linha, coluna e sugestão**. As sugestões de nome usam distância de edição — `sommar` → `somar` é encontrado automaticamente."},
  {"h2": "Por que é otimista"},
  {"p": "O analisador fica calado quando não consegue **provar** que algo está errado. Isso é deliberado: DataForge é dinamicamente tipado, e um falso alarme atrapalha mais que um alerta perdido — porque ensina a ignorar as mensagens."},
  {"p": "Calibragem atual: **zero erros** em 259 arquivos conhecidamente bons (os 217 exercícios mais os 43 exemplos)."},
  {"h3": "O que ele não encontra"},
  { code: `divisor := 0
out 10 / divisor      # o valor só é conhecido em tempo de execução` },
  {"p": "Isso passa no `check` e falha ao rodar. Erros que dependem de dados não são detectáveis estaticamente."},
  {"h2": "Erros dentro de monitor"},
  {"p": "Código dentro de um `monitor:` existe justamente para conter falhas — provocar uma de propósito é legítimo. Por isso o analisador **rebaixa erros a avisos** ali dentro:"},
  { code: `monitor:
    x := 1 / 0        # aviso, não erro
handle e:
    out e.message` },
  {"h2": "Em integração contínua"},
  { code: `dataforge fmt . --check && dataforge check . && dataforge test`, lang: 'bash' },
  {"p": "Cada comando sai com código diferente de zero em caso de falha. Com `--strict`, os avisos também derrubam o build."},
];

const headings = [{ id: 'tres-etapas-sem-executar', text: "Três etapas sem executar", level: 2 as const }, { id: 'o-que-ele-encontra', text: "O que ele encontra", level: 2 as const }, { id: 'um-exemplo', text: "Um exemplo", level: 2 as const }, { id: 'por-que-e-otimista', text: "Por que é otimista", level: 2 as const }, { id: 'o-que-ele-nao-encontra', text: "O que ele não encontra", level: 3 as const }, { id: 'erros-dentro-de-monitor', text: "Erros dentro de monitor", level: 2 as const }, { id: 'em-integracao-continua', text: "Em integração contínua", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Análise estática"}
      description={"O que o dataforge check encontra antes de executar, e por que ele é otimista."}
      href={"/docs/tecnicas/analise-estatica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
