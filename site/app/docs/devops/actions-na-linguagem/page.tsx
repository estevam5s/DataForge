// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um passo de workflow em DataForge",
  description: "Saídas, variáveis, resumo, anotações, máscara e grupos — com Arcane.GitHub, e sem injeção.",
};

const blocos: Bloco[] = [
  {"p": "Um passo de workflow conversa com o executor por **arquivos** (`GITHUB_OUTPUT`, `GITHUB_ENV`, `GITHUB_STEP_SUMMARY`) e por **linhas mágicas** na saída. Escrever isso à mão erra calado de dois jeitos: uma saída com quebra de linha vira duas (ou injeta uma variável), e uma mensagem com `%` é cortada. `Arcane.GitHub` escreve do jeito que o toolkit oficial escreve."},
  { code: `- name: relatorio
  id: relatorio
  run: dataforge run ci/relatorio.df
- name: usar
  run: echo "\${{ steps.relatorio.outputs.cobertura }}"`, lang: 'yaml' },
  {"h2": "Saída e resumo"},
  { code: `adopt Arcane.GitHub as GH
adopt Arcane.OS as OS
adopt Arcane.IO as IO

// O executor aponta estas variaveis para arquivos. Aqui, para
// temporarios — e exatamente o que acontece dentro do job.
pasta := $"{OS.temp_dir()}/df-gh-{randint(100000, 999999)}"
IO.mkdir(pasta)
OS.set_env("GITHUB_OUTPUT", $"{pasta}/output")
OS.set_env("GITHUB_STEP_SUMMARY", $"{pasta}/resumo.md")

resultados := [
    {"suite": "pedidos", "passou": 42, "falhou": 0},
    {"suite": "estoque", "passou": 17, "falhou": 1}
]

// Uma saida multilinha: sem o delimitador aleatorio, a segunda linha
// viraria outra saida — ou outra variavel.
GH.saida("resumo", "pedidos: 42\\nestoque: 17")
GH.saida("falhas", str(sum(resultados >> morph r: r["falhou"])))
GH.resumo("## Testes\\n\\n" + GH.tabela_markdown(resultados))

saidas := IO.read($"{pasta}/output")
assert "falhas<<ghadelimiter_" in saidas
assert "| estoque | 17 | 1 |" in IO.read($"{pasta}/resumo.md")

OS.unset_env("GITHUB_OUTPUT")
OS.unset_env("GITHUB_STEP_SUMMARY")
IO.remove_tree(pasta)
out "saidas escritas como o executor espera"`, lang: 'df' },
  {"h2": "Anotações, máscara e grupos"},
  { code: `adopt Arcane.GitHub as GH

// A anotacao aparece na linha do arquivo, no PR.
a := GH.anotacao("aviso", "cobertura caiu para 71%\\nminimo: 80%", "src/regras.df", 12,
    titulo := "cobertura")
out a
assert a is "::warning file=src/regras.df,line=12,title=cobertura::cobertura caiu para 71%25%0Aminimo: 80%25"

// Nivel desconhecido e recusado: o executor ignoraria a linha calado.
monitor:
    GH.anotacao("fatal", "x")
    assert no
handle Error as e:
    out e.message

// Fora do Actions, o contexto vem vazio — e nao levanta.
c := GH.contexto()
out $"em actions: {c['em_actions']}"`, lang: 'df' },
  {"table": {"head": ["Função", "O que ela resolve"], "rows": [["`saida(nome, valor)`", "multilinha com delimitador aleatório — o valor não injeta outra saída"], ["`exportar(nome, valor)`", "variável para os passos seguintes; nome com `=` é recusado"], ["`resumo(md)` + `tabela_markdown`", "a página do job; a `|` dentro de um valor é escapada"], ["`anotar` / `anotacao`", "`%`, `\\n`, `:` e `,` escapados"], ["`mascarar_no_log(segredo)`", "linha a linha — o executor casa por linha"], ["`grupo(nome, acao)`", "o `::endgroup::` sai mesmo se a ação falhar"], ["`contexto()` / `evento()`", "repositório, commit, quem disparou, a carga do evento"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Mascarar antes de imprimir", "texto": "`mascarar_no_log` só esconde o que for impresso **depois** dele. Um segredo lido de uma API e impresso para depurar antes da máscara já está no log — e o log de um repositório público é público."}},
  {"p": "Continue em [Webhooks](/docs/devops/webhooks) e [Arcane.GitHub](/docs/biblioteca/github)."},
];

const headings = [{ id: 'saida-e-resumo', text: "Saída e resumo", level: 2 as const }, { id: 'anotacoes-mascara-e-grupos', text: "Anotações, máscara e grupos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um passo de workflow em DataForge"}
      description={"Saídas, variáveis, resumo, anotações, máscara e grupos — com Arcane.GitHub, e sem injeção."}
      href={"/docs/devops/actions-na-linguagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
