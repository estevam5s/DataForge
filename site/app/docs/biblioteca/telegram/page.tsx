// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/telegram.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Telegram",
  description: "Bots de Telegram, do primeiro '/start' ao webhook em producao: cliente da Bot API com o limite de taxa lido de onde ele chega, tratadores por comando, texto, botao, midia e consulta inline, conversa como maquina de estados por chat, teclados, o escape de MarkdownV2 que salva a mensagem inteira, e uma sonda que testa o bot sem token e sem rede.",
};

const blocos: Bloco[] = [
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`ESPERA_LONGA`", "`50`"], ["`RAIZ`", "`\"https://api.telegram.org\"`"], ["`acoes`", "`[\"typing\", \"upload_photo\", \"record_video\", \"upload_video\"…`"]]}},
  {"h2": "Funções (34)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Aplicacao(token, estado=None, limitador=None, raiz=None)`"], ["`Bot(token, raiz=None, prazo=25.0)`"], ["`BotFalso(respostas=None)`"], ["`Contexto(app, update)`"], ["`Limitador(por_segundo=25.0, por_chat_por_minuto=18)`"], ["`Sonda(aplicacao, chat=1001, usuario=None)`"], ["`app(token, estado=None, limitador=None, raiz=None)`"], ["`bloco(texto, linguagem='')`"], ["`bot(token, raiz=None, prazo=25.0)`"], ["`botao(texto, dados=None, url=None, inline_atual=None, pedir_contato=False, pedir_local=False, jogo=False, pagar=False, app_web=None)`"], ["`botoes(linhas)`"], ["`chamar(token, metodo, params=None, arquivos=None, prazo=25.0, raiz=None, tentativas=None)`"], ["`codigo(texto)`"], ["`dividir(texto, limite=4096)`"], ["`escapar(texto)`"], ["`escapar_html(texto)`"], ["`estado_em_arquivo(pasta='.telegram/estado')`"], ["`estado_em_memoria()`"], ["`forcar_resposta(dica='', seletivo=False)`"], ["`italico(texto)`"], ["`ler_pagina(dados, prefixo='pg')`"], ["`limitar(por_segundo=25.0, por_chat_por_minuto=18)`"], ["`link(texto, destino)`"], ["`mencao(texto, id_usuario)`"], ["`modo_servidor()`"], ["`negrito(texto)`"], ["`paginado(itens, pagina=1, por_pagina=5, prefixo='pg')`"], ["`remover_teclado(seletivo=False)`"], ["`riscado(texto)`"], ["`segredo_do_ambiente(nome='TELEGRAM_TOKEN')`"], ["`spoiler(texto)`"], ["`sublinhado(texto)`"], ["`teclado(linhas, uma_vez=True, ajustar=True, dica='', persistente=False)`"], ["`testar(aplicacao, chat=1001, usuario=None)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-34', text: "Funções (34)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Telegram"}
      description={"Bots de Telegram, do primeiro '/start' ao webhook em producao: cliente da Bot API com o limite de taxa lido de onde ele chega, tratadores por comando, texto, botao, midia e consulta inline, conversa como maquina de estados por chat, teclados, o escape de MarkdownV2 que salva a mensagem inteira, e uma sonda que testa o bot sem token e sem rede."}
      href={"/docs/biblioteca/telegram"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
