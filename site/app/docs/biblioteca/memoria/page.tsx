// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/memoria.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Memoria",
  description: "O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (24)"},
  {"table": {"head": ["Assinatura"], "rows": [["`ao_descartar(obj, acao)`"], ["`arena(quantos, fabrica)`"], ["`arena_estatisticas(a)`"], ["`coletar(geracao=2)`"], ["`comparar_layout(um, outro, amostras=20)`"], ["`devolver(a, i)`"], ["`estatisticas()`"], ["`fraca(obj)`"], ["`gc_congelados()`"], ["`gc_congelar()`"], ["`gc_descongelar()`"], ["`gc_desligar()`"], ["`gc_geracoes()`"], ["`gc_ligado()`"], ["`gc_ligar()`"], ["`gc_limiares(*valores)`"], ["`layout(alvo, amostras=20)`"], ["`limpar(a)`"], ["`mapa_fraco()`"], ["`pegar(a)`"], ["`referencias(obj)`"], ["`sem_gc(acao)`"], ["`tamanho(obj)`"], ["`vivos(molde)`"]]}},
];

const headings = [{ id: 'funcoes-24', text: "Funções (24)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Memoria"}
      description={"O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada."}
      href={"/docs/biblioteca/memoria"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
