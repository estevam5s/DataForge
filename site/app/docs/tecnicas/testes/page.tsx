import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes",
  description: "Escrever testes que o dataforge test descobre e executa sozinho.",
};

const blocos: Bloco[] = [
  {"h2": "Descoberta automática"},
  {"table": {"head": ["Padrão", "Exemplo"], "rows": [["`*_test.df`", "`matematica_test.df`"], ["`test_*.df`", "`test_matematica.df`"], ["qualquer `.df` em `tests/`", "`tests/regras.df`"]]}},
  {"p": "Dentro do arquivo, **toda ação `test_*` é um caso**:"},
  { code: `action test_fatorial_casos_base():
    assert fatorial(0) is 1, "fatorial de 0"
    assert fatorial(1) is 1, "fatorial de 1"

action test_fatorial_cresce():
    assert fatorial(5) is 120, "fatorial de 5"`, title: `tests/matematica_test.df` },
  { code: `dataforge test              # tudo
dataforge test tests/ -v    # mostra cada caso
dataforge test --filter=primo
dataforge test --fail-fast`, lang: 'bash' },
  {"h2": "Ganchos"},
  {"table": {"head": ["Ação", "Roda"], "rows": [["`setup_all`", "uma vez, antes de tudo"], ["`setup`", "antes de cada caso"], ["`teardown`", "depois de cada caso"], ["`teardown_all`", "uma vez, no fim"]]}},
  {"h2": "Anatomia de um bom teste"},
  {"h3": "Nome que descreve o comportamento"},
  { code: `action test_saque_acima_do_saldo():     # bom
action test_sacar_2():                  # ruim` },
  {"h3": "Mensagem em cada assert"},
  {"p": "Quando falha, é ela que você lê:"},
  { code: `assert depois.saldo is 700, "saldo apos saque"` },
  {"h3": "Um comportamento por caso"},
  {"p": "Se um `test_tudo` falha, você não sabe qual das oito verificações quebrou."},
  {"h2": "Testar erros"},
  {"p": "O erro esperado é parte do contrato, e merece teste:"},
  { code: `action test_saque_acima_do_saldo():
    erro := ""
    monitor:
        sacar(Conta("Ana", 100), 500)
    handle e:
        erro := e.message
    assert erro is "saldo insuficiente", "mensagem do guard"` },
  {"p": "Note que o `assert` verifica a **mensagem**, não só que algo falhou. Isso pega o caso em que a ação falha pelo motivo errado."},
  {"h2": "Testar imutabilidade"},
  { code: `action test_saque_nao_muda_o_original():
    c := Conta("Ana", 1000)
    depois := sacar(c, 300)
    assert depois.saldo is 700, "saldo apos saque"
    assert c.saldo is 1000, "o original nao muda"` },
  {"p": "O segundo `assert` é o que garante ausência de efeito colateral. Sem ele, uma implementação que mutasse o original passaria."},
  {"h2": "Cobrir faixas"},
  { code: `action test_primos_conhecidos():
    cycle n in [2, 3, 5, 7, 11, 13]:
        assert eh_primo(n) is yes, $"{n} e primo"` },
  {"p": "A mensagem interpolada diz **qual** valor falhou."},
  {"h2": "A saída"},
  { code: `✓ tests/matematica_test.df (3/3)
    ok   test_fatorial_casos_base 0.1ms
    ok   test_fatorial_cresce 0.1ms
✗ tests/texto_test.df (1/2)
    FALHOU test_juncao
      join
      em tests/texto_test.df:12
        via test_juncao (linha 10)

4 passaram, 1 falharam em 2 arquivo(s) — 0.02s`, lang: 'text' },
  {"h2": "Regras puras são testáveis"},
  {"p": "Uma ação que não imprime, não lê arquivo e não consulta banco tem teste de uma linha:"},
  { code: `assert situacao_de(Produto("X", 1, 0)) is Situacao.EmFalta` },
  {"p": "Se ela também formatasse a saída, testá-la exigiria comparar strings — e mudar o formato quebraria o teste da regra. Separe [as camadas](/docs/tecnicas/projeto)."},
];

const headings = [{ id: 'descoberta-automatica', text: "Descoberta automática", level: 2 as const }, { id: 'ganchos', text: "Ganchos", level: 2 as const }, { id: 'anatomia-de-um-bom-teste', text: "Anatomia de um bom teste", level: 2 as const }, { id: 'nome-que-descreve-o-comportamento', text: "Nome que descreve o comportamento", level: 3 as const }, { id: 'mensagem-em-cada-assert', text: "Mensagem em cada assert", level: 3 as const }, { id: 'um-comportamento-por-caso', text: "Um comportamento por caso", level: 3 as const }, { id: 'testar-erros', text: "Testar erros", level: 2 as const }, { id: 'testar-imutabilidade', text: "Testar imutabilidade", level: 2 as const }, { id: 'cobrir-faixas', text: "Cobrir faixas", level: 2 as const }, { id: 'a-saida', text: "A saída", level: 2 as const }, { id: 'regras-puras-sao-testaveis', text: "Regras puras são testáveis", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes"}
      description={"Escrever testes que o dataforge test descobre e executa sozinho."}
      href={"/docs/tecnicas/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
