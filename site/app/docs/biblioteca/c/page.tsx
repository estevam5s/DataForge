// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/c.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.C",
  description: "Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (23)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Biblioteca(lib, nome, caminho)`"], ["`Bloco(quantos)`"], ["`Ponteiro(endereco=0, tipo='u8')`"], ["`RetornoDeChamada(acao, argumentos, retorno)`"], ["`alinhamento_de(tipo)`"], ["`alocar(bytes_quantos)`"], ["`carregar(alvo, procurar=True)`"], ["`copiar(destino, origem, quantos)`"], ["`de_bytes(dados)`"], ["`do_processo()`"], ["`endianness()`"], ["`enumeracao(pares)`"], ["`estrutura(campos)`"], ["`liberar(bloco)`"], ["`matematica()`"], ["`nulo(tipo='u8')`"], ["`padrao()`"], ["`para_bytes(alvo, quantos)`"], ["`ponteiro(alvo, tipo='u8')`"], ["`retorno_de_chamada(acao, argumentos=None, retorno='void')`"], ["`tamanho_de(tipo)`"], ["`tipos()`"], ["`uniao(campos)`"]]}},
];

const headings = [{ id: 'funcoes-23', text: "Funções (23)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.C"}
      description={"Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia."}
      href={"/docs/biblioteca/c"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
