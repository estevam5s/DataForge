// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/brasa.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Brasa",
  description: "O framework de aplicativos para o celular: o programa vira um PWA que o Android e o iPhone instalam na tela inicial — barra de abas, topo com voltar, lista tocável, botão flutuante, compartilhar, ligar, mapa e localização, com manifesto, service worker e ícones gerados. Sobre a Vitrine, e testável sem navegador. Não gera APK.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (19)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Sonda(aplicacao, caminho='/')`"], ["`app(nome='DataForge', cor='#E8453C', icone='', descricao='', versao='1', fundo='#FFFFFF')`"], ["`botao_flutuante(rotulo, destino, icone='mais')`"], ["`compartilhar(texto, rotulo='Compartilhar', url='')`"], ["`conferir_pwa(aplicacao)`"], ["`enderecos_na_rede(porta)`"], ["`icone_png(nome, cor='#E8453C', tamanho=192, maskable=False)`"], ["`ligar(numero, rotulo='')`"], ["`lista(itens, titulo='nome', detalhe='', destino='', icone='')`"], ["`localizacao(rotulo='Usar minha localização')`"], ["`manifesto(aplicacao)`"], ["`mapa(latitude, longitude, rotulo='Abrir no mapa')`"], ["`rodar(aplicacao, porta=8600, rede=True)`"], ["`secao(titulo)`"], ["`servir(aplicacao, porta=0)`"], ["`tela(caminho, acao, titulo='', icone='', aba=False, aplicacao=None)`"], ["`testar(aplicacao, caminho='/')`"], ["`topo(titulo, voltar=False, destino_voltar='/')`"], ["`vazio(mensagem, dica='')`"]]}},
];

const headings = [{ id: 'funcoes-19', text: "Funções (19)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Brasa"}
      description={"O framework de aplicativos para o celular: o programa vira um PWA que o Android e o iPhone instalam na tela inicial — barra de abas, topo com voltar, lista tocável, botão flutuante, compartilhar, ligar, mapa e localização, com manifesto, service worker e ícones gerados. Sobre a Vitrine, e testável sem navegador. Não gera APK."}
      href={"/docs/biblioteca/brasa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
