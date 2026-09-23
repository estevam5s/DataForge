// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Engenharia de dados",
  description: "O que separa uma análise que roda de um pipeline que se pode confiar — e as três formas de errar em silêncio.",
};

const blocos: Bloco[] = [
  {"p": "Uma análise erra e alguém percebe: o gráfico fica estranho. Um **pipeline** erra e ninguém percebe — o número é plausível, o processo termina com código zero, e a conclusão errada vira decisão. Esta seção é sobre as formas de errar que **não dão erro**."},
  {"table": {"head": ["O erro", "Como ele aparece", "A defesa"], "rows": [["janela sem partição", "média móvel \"por loja\" atravessa as lojas", "`por := \"loja\"`"], ["junção que multiplica", "o total sobe, e as linhas também", "`cardinalidade := \"muitos_para_um\"`"], ["deriva de esquema", "o `id` chega como texto, e o `join` para de casar", "`Qualidade.exigir_esquema`"], ["reprocessar sem idempotência", "o mesmo dia contado duas vezes", "marca d'água, e partição sobrescrita"], ["ausência virando zero", "a soma cai, e a média sobe", "`void` é vão, e não zero"]]}},
  {"cards": [{"title": "Janelas por grupo", "desc": "média móvel, acumulado e ranking dentro da partição.", "href": "/docs/dados/particao"}, {"title": "Junções que não inflam", "desc": "declarar a cardinalidade, e o total que subiu de 30 para 40.", "href": "/docs/dados/cardinalidade"}, {"title": "Deriva de esquema", "desc": "o que mudou no que chega, e se isso quebra.", "href": "/docs/dados/deriva"}, {"title": "Carga incremental", "desc": "marca d'água, reprocessamento e idempotência.", "href": "/docs/dados/incremental"}]},
  {"h2": "O caminho inteiro, num programa"},
  { code: `adopt Arcane.Quadro as Q
adopt Arcane.Qualidade as Qual

// ── 1. o que chegou ────────────────────────────────────────
bruto := [
    {"dia": "2026-01-05", "loja": "sul",   "produto": "cafe",   "valor": 98.7},
    {"dia": "2026-01-05", "loja": "norte", "produto": "cafe",   "valor": 32.9},
    {"dia": "2026-01-06", "loja": "sul",   "produto": "filtro", "valor": 42.5},
    {"dia": "2026-01-06", "loja": "norte", "produto": "cafe",   "valor": 65.8},
    {"dia": "2026-01-07", "loja": "sul",   "produto": "cafe",   "valor": 51.0},
]

// ── 2. o esquema esperado, e a conferência ────────────────
esperado := Qual.esquema_de(bruto)
relato := Qual.exigir_esquema(bruto, esperado)
assert relato["ok"] is yes

// ── 3. o quadro, e a janela POR LOJA ──────────────────────
vendas := Q.de_vaults(bruto).ordenar("dia")
com_media := vendas.janela("valor", 2, "media", "media_2", void, "loja")
assert com_media.altura() is 5

// ── 4. o apoio, com a cardinalidade declarada ─────────────
lojas := Q.de_vaults([
    {"loja": "sul", "regiao": "SE"},
    {"loja": "norte", "regiao": "N"},
])
junto := com_media.juntar(lojas, "loja", "dentro", "muitos_para_um")
assert junto.altura() is 5          // não inflou

// ── 5. a resposta ─────────────────────────────────────────
por_regiao := junto >> agrupar "regiao" >> resumir {"valor": "soma"}
out por_regiao.texto()`, lang: 'df' },
  {"p": "Cinco passos, e quatro deles são sobre **não errar em silêncio**. É a proporção certa: o trabalho de um pipeline é quase todo em garantir que o número final significa o que ele diz significar."},
];

const headings = [{ id: 'o-caminho-inteiro-num-programa', text: "O caminho inteiro, num programa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Engenharia de dados"}
      description={"O que separa uma análise que roda de um pipeline que se pode confiar — e as três formas de errar em silêncio."}
      href={"/docs/dados/engenharia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
