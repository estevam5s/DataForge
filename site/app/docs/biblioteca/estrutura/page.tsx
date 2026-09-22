// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/estrutura.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Estrutura",
  description: "Layout binario com NOME, e o ponteiro que o percorre: uma estrutura de campos nomeados com a ordem dos bytes cobrada e o alinhamento declarado (e conferido), uma janela que le e escreve no bloco original sem copiar, um bloco que sabe dizer quando foi liberado, e um ponteiro com aritmetica por ELEMENTO, cast, distancia e dono fraco. Fica entre o Arcane.Bytes, que empacota por formato posicional, e o Arcane.C, que exige FFI.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (33)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Bloco(tamanho_ou_dados=0)`"], ["`Janela(bloco_alvo, molde, deslocamento=0)`"], ["`Molde(nome, campos, ordem='rede', empacotado=False)`"], ["`MoldeDeBits(nome, campos, largura=8)`"], ["`Ponteiro(bloco_alvo, tipo='u8', deslocamento=0, ordem='rede')`"], ["`alinhamento_de(tipo_ou_molde)`"], ["`bit_ligado(a, posicao)`"], ["`bits_e(a, b)`"], ["`bits_nao(a, largura)`"], ["`bits_ou(a, b)`"], ["`bits_xou(a, b)`"], ["`bloco(tamanho_ou_dados=0)`"], ["`campos_de_bits(nome, campos, largura=8)`"], ["`contar_uns(a)`"], ["`crc32(dados, inicial=0)`"], ["`de_bytes(dados)`"], ["`definir(nome, campos, ordem='rede', empacotado=False)`"], ["`desfazer_zigzag(numero)`"], ["`desligar_bit(a, posicao)`"], ["`deslocar(a, casas)`"], ["`janela(alvo, molde, deslocamento=0)`"], ["`janelas(alvo, molde, quantos=None, deslocamento=0)`"], ["`ler_varint(dados, deslocamento=0)`"], ["`ligar_bit(a, posicao)`"], ["`mapear(caminho, escrita=False)`"], ["`nulo()`"], ["`ponteiro(alvo, tipo='u8', deslocamento=0, ordem='rede')`"], ["`tamanho_de(tipo_ou_molde)`"], ["`tipos()`"], ["`trocar_ordem(valor, tipo='u32')`"], ["`uniao(nome, campos, ordem='rede')`"], ["`varint(numero)`"], ["`zigzag(numero)`"]]}},
];

const headings = [{ id: 'funcoes-33', text: "Funções (33)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Estrutura"}
      description={"Layout binario com NOME, e o ponteiro que o percorre: uma estrutura de campos nomeados com a ordem dos bytes cobrada e o alinhamento declarado (e conferido), uma janela que le e escreve no bloco original sem copiar, um bloco que sabe dizer quando foi liberado, e um ponteiro com aritmetica por ELEMENTO, cast, distancia e dono fraco. Fica entre o Arcane.Bytes, que empacota por formato posicional, e o Arcane.C, que exige FFI."}
      href={"/docs/biblioteca/estrutura"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
