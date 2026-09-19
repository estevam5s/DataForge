// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A diferença é real, ou é ruído?",
  description: "Mann-Whitney sobre as amostras: o teste que impede a ferramenta de inventar ganho — e por que não é o teste t.",
};

const blocos: Bloco[] = [
  {"p": "**Comparar uma ação com ela mesma não pode dar \"3% mais rápida\".** É o que separa medição de superstição, e é o primeiro teste do arquivo de testes."},
  { code: `adopt Arcane.Perfil as P

action consulta():
    yield sum(range(400))

// a MESMA acao dos dois lados: a diferenca e ruido, e a ferramenta
// tem de dizer isso
v := P.comparar(consulta, consulta, {"amostras": 40})
assert v["mais_rapido"] is "empate"
assert not v["significativo"]`, lang: 'df' },
  { code: `adopt Arcane.Perfil as P

action rapida():
    yield sum(range(400))

action lenta():
    yield sum(range(9000))

d := P.comparar(rapida, lenta, {"amostras": 30})
assert d["significativo"]
assert d["mais_rapido"] is "a"
assert d["fator"] bigger 2
assert d["p_valor"] smaller 0.05`, lang: 'df' },
  {"h2": "Por que Mann-Whitney, e não o teste t"},
  {"p": "Tempo de execução **não é normal**: tem cauda longa à direita, piso duro à esquerda (nada roda em tempo negativo) e picos de escalonamento do sistema. Um teste t supõe normalidade e responde com confiança sobre uma suposição falsa."},
  {"p": "O U de Mann-Whitney não supõe nada sobre a forma — ele compara **ordens**. E a correção de empates importa quando o relógio tem resolução grossa e muitas amostras dão o mesmo valor."},
  {"table": {"head": ["Campo", "O que diz"], "rows": [["`p_valor`", "a chance de ver esta diferença se as duas fossem iguais"], ["`significativo`", "`p_valor` abaixo de `alfa` (padrão 0,05)"], ["`sobreposicao`", "o **tamanho do efeito**: a chance de um sorteio de A ser menor que um de B. É o que `p` **não** diz"], ["`fator`", "quantas vezes, na mediana — e só quando é significativo"], ["`a`, `b`", "a distribuição completa de cada lado"]]}},
  {"callout": {"tipo": "atencao", "titulo": "As duas medições são intercaladas, e isso não é detalhe", "texto": "Medir A inteiro e depois B inteiro faz uma queda de clock no meio da sessão virar \"B é mais lenta\". Alternar A, B, A, B espalha a deriva da máquina igualmente pelos dois lados — é a diferença entre comparar duas implementações e comparar dois momentos."}},
  {"h2": "Regressão: piorou desde a semana passada?"},
  {"p": "Um número sozinho não responde isso. A linha de base fica num arquivo, e o `conferir` compara."},
  { code: `adopt Arcane.Perfil as P
adopt Arcane.IO as IO
adopt Arcane.OS as OS

base := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}.json"
P.guardar("consulta", {"p95": 1.0, "p50": 1.0, "media": 1.0}, base)

// tres vezes mais lento: regrediu
ruim := P.conferir("consulta", {"p95": 3.0, "p50": 3.0, "media": 3.0},
                   {"arquivo": base, "tolerancia": 0.2})
assert ruim["regrediu"] and ruim["fator"] is 3.0

// 5% mais lento, com 20% de tolerancia: e ruido de maquina
ok := P.conferir("consulta", {"p95": 1.05, "p50": 1.05, "media": 1.05},
                 {"arquivo": base, "tolerancia": 0.2})
assert not ok["regrediu"]

// a PRIMEIRA medida nunca reprova: sem base nao ha regressao
nova := P.conferir("nunca-medida", {"p95": 1.0}, {"arquivo": base})
assert not nova["conhecida"] and not nova["regrediu"]

IO.delete(base)`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Duas escolhas que mantêm o CI utilizável", "texto": "**A primeira medida nunca reprova** — reprovar ali faria todo CI novo nascer vermelho, e a primeira coisa que se faz com um CI vermelho por desenho é desligá-lo. E **a tolerância é obrigatória**: sem ela, todo CI fica vermelho por ruído de máquina, o que dá no mesmo."}},
];

const headings = [{ id: 'por-que-mann-whitney-e-nao-o-teste-t', text: "Por que Mann-Whitney, e não o teste t", level: 2 as const }, { id: 'regressao-piorou-desde-a-semana-passada', text: "Regressão: piorou desde a semana passada?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A diferença é real, ou é ruído?"}
      description={"Mann-Whitney sobre as amostras: o teste que impede a ferramenta de inventar ganho — e por que não é o teste t."}
      href={"/docs/observabilidade/comparar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
