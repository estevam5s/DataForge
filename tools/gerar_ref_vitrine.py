#!/usr/bin/env python3
"""
Gera a pagina de referencia da Vitrine a partir do proprio modulo.

    python3 tools/gerar_ref_vitrine.py

A lista de simbolos e as assinaturas saem de dataforge/stdlib/vitrine/.
Escrever isso a mao garantiria que, um dia, a doc listaria uma funcao
que nao existe mais — ou esconderia uma que existe. O script RECUSA
rodar se um simbolo do modulo nao estiver num grupo com resumo: e a
mesma trava do gerador da gramatica do editor.
"""

import inspect
import json
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import marca  # noqa: E402

marca.preparar_saida()

from dataforge.stdlib import get_module   # noqa: E402

DESTINO = os.path.join(RAIZ, "site", "app", "docs", "vitrine",
                       "referencia", "page.tsx")

#: Como agrupar. A ordem aqui e a ordem da pagina.
GRUPOS = [
    ("Aplicação e servidor", [
        "app", "configurar", "configurar_pagina", "pagina", "paginas",
        "rodar", "subir", "servir", "parar_servidor", "montar"]),
    ("Texto", [
        "titulo", "subtitulo", "cabecalho", "texto", "markdown", "codigo",
        "html", "divisor", "espaco"]),
    ("Entrada", [
        "botao", "entrada", "area_de_texto", "numero", "deslizante",
        "caixa", "interruptor", "opcao", "escolha", "escolhas", "data",
        "cor", "arquivo"]),
    ("Dados", ["tabela", "frame", "metrica", "json", "vault"]),
    ("Retorno ao usuário", [
        "sucesso", "erro", "aviso", "informacao", "progresso",
        "carregando", "imagem", "audio", "video", "link", "baixar"]),
    ("Layout", [
        "colunas", "linha", "container", "cartao", "expandir", "abas",
        "formulario", "vazio", "lateral", "espacador"]),
    ("Gráficos", [
        "grafico", "desenhar", "grafico_linha", "grafico_barras",
        "grafico_barras_h", "grafico_area", "grafico_dispersao",
        "grafico_pizza", "grafico_rosca", "histograma", "paleta"]),
    ("Estado e cache", ["estado", "geral", "cache"]),
    ("Navegação", [
        "navegar", "parar", "recarregar", "caminho", "parametros",
        "parametro", "menu"]),
    ("Segurança", [
        "autenticacao", "entrar", "sair", "usuario", "autenticado",
        "pode", "exigir_login", "exigir_permissao"]),
    ("Operação", [
        "registrar", "logs", "metricas", "saude", "plugin", "antes",
        "depois", "sessoes", "encerrar_sessao", "tarefa", "agendar",
        "atualizar_a_cada"]),
    ("Exportar", [
        "exportar_csv", "exportar_json", "html_da_pagina",
        "markdown_para_html"]),
    ("Testes", ["testar", "pedir"]),
]

#: O que cada simbolo faz, em uma linha. A docstring do Python e escrita
#: para quem le o runtime; isto e para quem escreve DataForge.
RESUMOS = {
    "app": "Cria a aplicação e passa a ser a atual.",
    "configurar": "Ajusta uma opção, ou várias por vault.",
    "configurar_pagina": "Título e ícone **só desta** página.",
    "pagina": "Registra uma página. Também serve de decorador.",
    "paginas": "As páginas registradas, para montar um menu.",
    "rodar": "Sobe a aplicação. Com uma ação, ela vira a página de `/`.",
    "subir": "Sobe e bloqueia. `recarregar := yes` reinicia ao salvar.",
    "servir": "Sobe em segundo plano e devolve a porta. Para testes.",
    "parar_servidor": "Desliga o servidor.",
    "montar": "O app Kiln por baixo — para acrescentar rota ou middleware.",

    "titulo": "O título da página, com ícone opcional.",
    "subtitulo": "Um subtítulo.",
    "cabecalho": "Um cabeçalho de seção, do nível 1 ao 6.",
    "texto": "Um parágrafo. Vários argumentos viram uma linha, como o `out`.",
    "markdown": "Títulos, listas, tabela, ênfase, código e link.",
    "codigo": "Um bloco de código, com a linguagem.",
    "html": "HTML **cru, sem escapar**. Nunca com o que veio do usuário.",
    "divisor": "Uma linha horizontal.",
    "espaco": "Espaço vertical em pixels.",

    "botao": "Devolve `yes` no ciclo em que foi clicado, `no` nos outros.",
    "entrada": "Campo de texto. Devolve o que está digitado.",
    "area_de_texto": "Campo de várias linhas.",
    "numero": "Campo numérico, com mínimo, máximo e passo.",
    "deslizante": "Escolher um número numa faixa.",
    "caixa": "Uma caixa de marcar. Devolve `yes`/`no`.",
    "interruptor": "O mesmo, com cara de chave.",
    "opcao": "Uma de poucas, em botões de rádio.",
    "escolha": "Uma de muitas, em lista suspensa.",
    "escolhas": "Várias de muitas. Devolve um cluster.",
    "data": "Um seletor de data. Devolve `\"2026-03-14\"`.",
    "cor": "Um seletor de cor. Devolve `\"#FED403\"`.",
    "arquivo": "Envio de arquivo. Devolve `void` até alguém mandar um.",

    "tabela": "Uma tabela estática. Aceita cluster de vaults, Frame ou matriz.",
    "frame": "Uma tabela com busca e ordenação, para explorar dado.",
    "metrica": "Um número grande, com a variação ao lado.",
    "json": "Um vault ou cluster, formatado e recolhível.",
    "vault": "Um vault como lista de chave e valor.",

    "sucesso": "Uma mensagem verde.",
    "erro": "Uma mensagem vermelha.",
    "aviso": "Uma mensagem amarela.",
    "informacao": "Uma mensagem azul.",
    "progresso": "Barra de 0 a 1.",
    "carregando": "Um giro com uma mensagem.",
    "imagem": "Uma imagem, com legenda.",
    "audio": "Um tocador de áudio.",
    "video": "Um tocador de vídeo.",
    "link": "Um link, opcionalmente em nova aba.",
    "baixar": "Um botão que entrega um arquivo ao visitante.",

    "colunas": "Divide em colunas. Devolve um cluster de áreas.",
    "linha": "Container horizontal — os filhos ficam lado a lado.",
    "container": "Um agrupamento, com borda e altura opcionais.",
    "cartao": "Uma caixa com título e subtítulo.",
    "expandir": "Uma seção que abre e fecha; o estado sobrevive.",
    "abas": "Abas. **Todas** são montadas; só a escolhida aparece.",
    "formulario": "Agrupa campos que só valem no envio.",
    "vazio": "Um espaço reservado para ser preenchido depois.",
    "lateral": "A barra lateral. Sempre a mesma, chamada de onde for.",
    "espacador": "Empurra o que vem depois para a outra ponta de uma `linha`.",

    "grafico": "Começa a montar um gráfico. Nada aparece até `desenhar`.",
    "desenhar": "Põe o gráfico montado na página.",
    "grafico_linha": "Linha, a forma curta.",
    "grafico_barras": "Barras verticais.",
    "grafico_barras_h": "Barras horizontais, para categorias de nome longo.",
    "grafico_area": "Linha com a área preenchida.",
    "grafico_dispersao": "Pontos.",
    "grafico_pizza": "Fatias, com o percentual escrito.",
    "grafico_rosca": "O mesmo, com o miolo vazado.",
    "histograma": "Distribuição: conta quantos valores caem em cada faixa.",
    "paleta": "As dez cores padrão, como cluster.",

    "estado": "O estado da sessão: `obter`, `definir`, `padrao`, `somar`…",
    "geral": "O estado do processo — **todas** as sessões veem o mesmo.",
    "cache": "`mark @V.cache` sobre uma ação, e ela para de recalcular.",

    "navegar": "Vai para outra página. Interrompe o programa aqui.",
    "parar": "Acaba a página neste ponto, sem erro.",
    "recarregar": "Roda de novo, do começo, jogando fora o que foi montado.",
    "caminho": "Onde a página está.",
    "parametros": "Os da rota e os da query, juntos.",
    "parametro": "Um deles, com padrão.",
    "menu": "Desenha o menu das páginas registradas na barra lateral.",

    "autenticacao": "Registra a ação que confere usuário e senha.",
    "entrar": "Tenta entrar. Devolve o vault do usuário, ou `void`.",
    "sair": "Derruba a sessão de quem está logado.",
    "usuario": "Quem está logado, ou `void`.",
    "autenticado": "`yes`/`no`.",
    "pode": "Se o papel de quem está logado tem a permissão.",
    "exigir_login": "A barreira: desenha a entrada e para a página.",
    "exigir_permissao": "O mesmo, e ainda cobra a permissão.",

    "registrar": "Escreve no log da aplicação.",
    "logs": "As últimas linhas, filtráveis por nível.",
    "metricas": "Execuções, erros, média em ms, sessões e cache.",
    "saude": "O que um balanceador pergunta antes de mandar tráfego.",
    "plugin": "Instala um plugin. O mesmo nome duas vezes é erro.",
    "antes": "Middleware que roda antes de toda página; `no` interrompe.",
    "depois": "Middleware de saída, com o contexto já montado.",
    "sessoes": "Quantas sessões estão vivas.",
    "encerrar_sessao": "Descarta a sessão de agora.",
    "tarefa": "Roda numa thread e devolve na hora. A página não espera.",
    "agendar": "Roda de tempos em tempos, enquanto o processo viver.",
    "atualizar_a_cada": "A página se recarrega sozinha nesse intervalo.",

    "exportar_csv": "Um botão que entrega os dados como CSV.",
    "exportar_json": "O mesmo, em JSON.",
    "html_da_pagina": "A página atual como HTML.",
    "markdown_para_html": "Converte Markdown sem pôr nada na página.",

    "testar": "Uma sonda: clica, digita e pergunta, sem navegador.",
    "pedir": "Um pedido HTTP de verdade contra a aplicação, sem socket.",
}


def assinatura(valor):
    """A assinatura como quem escreve DataForge a chama."""
    if not callable(valor):
        return ""
    try:
        texto = str(inspect.signature(valor))
    except (TypeError, ValueError):
        return "(…)"
    return texto.replace("**kw", "…").replace("**pares", "…")


def conferir_cobertura(modulo):
    """Recusa gerar uma referencia que mente.

    Um simbolo fora da pagina e trabalho que ninguem encontra; um
    listado que nao existe e uma promessa quebrada na primeira tentativa
    de quem le.
    """
    listados = {n for _, nomes in GRUPOS for n in nomes}
    reais = {n for n in modulo if n != "__name__"}
    faltando = reais - listados
    if faltando:
        raise SystemExit(
            f"simbolos da Vitrine fora da referencia: {sorted(faltando)}\n"
            f"acrescente cada um a GRUPOS e a RESUMOS em "
            f"tools/gerar_ref_vitrine.py")
    inventados = listados - reais
    if inventados:
        raise SystemExit(f"a referencia lista o que nao existe: "
                         f"{sorted(inventados)}")
    sem_resumo = reais - set(RESUMOS)
    if sem_resumo:
        raise SystemExit(f"sem resumo em RESUMOS: {sorted(sem_resumo)}")


def construir():
    modulo = get_module("Arcane.Vitrine")
    conferir_cobertura(modulo)
    total = len(modulo) - 1

    blocos = [
        {"p": "Esta página é gerada a partir de "
              "`dataforge/stdlib/vitrine/`. São **"
              f"{total} símbolos**, e o gerador recusa rodar se algum "
              "deles ficar de fora."},
        {"p": "Em todos os exemplos, `V` é o apelido de "
              "`adopt Arcane.Vitrine as V`."},
        {"callout": {"tipo": "dica", "titulo": "Toda área tem os mesmos componentes",
                     "texto": "Os grupos **Texto**, **Entrada**, **Dados**, "
                              "**Retorno** e **Gráficos** também são métodos de "
                              "qualquer área de layout — `coluna.metrica(…)`, "
                              "`aba.frame(…)`, `lateral.escolha(…)`. Aprender "
                              "um lugar ensina todos."}},
    ]

    for titulo, nomes in GRUPOS:
        blocos.append({"h2": titulo})
        linhas = []
        for nome in nomes:
            chamada = f"`V.{nome}{assinatura(modulo[nome])}`"
            linhas.append([chamada, RESUMOS[nome]])
        blocos.append({"table": {"head": ["Símbolo", "Faz"], "rows": linhas}})

    blocos.append({"h2": "Os métodos da sonda"})
    blocos.append({"p": "O que `V.testar(pagina)` devolve — ver "
                        "[Testar sem navegador](/docs/vitrine/testes)."})
    blocos.append({"table": {"head": ["Método", "Faz"], "rows": [
        ["`t.clicar(rótulo)`", "clica num botão e roda a página de novo"],
        ["`t.digitar(rótulo, valor)`", "preenche um campo"],
        ["`t.marcar(rótulo, ligado)`", "liga uma caixa ou interruptor"],
        ["`t.selecionar(rótulo, valor)`", "escolhe numa lista"],
        ["`t.abrir_aba(rótulo)`", "troca de aba"],
        ["`t.enviar(formulário)`", "aperta o botão de envio"],
        ["`t.enviar_arquivo(rótulo, nome, conteúdo)`", "simula um upload"],
        ["`t.ir_para(caminho)`", "vai para outra página"],
        ["`t.rodar()`", "roda de novo, sem interação"],
        ["`t.texto()`", "a página como texto corrido"],
        ["`t.achar(tipo)` · `t.primeiro(tipo)`", "os nós de um tipo"],
        ["`t.quantos(tipo)` · `t.existe(tipo, rótulo)`", "contar e conferir"],
        ["`t.metrica(rótulo)` · `t.valor(rótulo)`", "o que a tela mostra"],
        ["`t.alertas(nível)`", "as mensagens de sucesso, erro, aviso"],
        ["`t.estado(chave)`", "o estado da sessão"],
        ["`t.falhou()` · `t.falhas()`", "se algo disparou, e o quê"],
        ["`t.html()` · `t.arvore()`", "a página como HTML, ou como vault"],
    ]}})

    blocos.append({"h2": "As rotas que vêm prontas"})
    blocos.append({"table": {"head": ["Rota", "Devolve"], "rows": [
        ["`GET /__vitrine__/saude`", "estado, tempo no ar, sessões"],
        ["`GET /__vitrine__/metricas`", "execuções, erros, média em ms, cache"],
        ["`POST /__vitrine__/acao`", "o miolo da página, após uma interação"],
        ["`GET /__vitrine__/baixar/:chave`", "o arquivo de um `V.baixar`"],
        ["`GET /__vitrine__/manifesto.json`", "o manifesto PWA, se ligado"],
    ]}})

    corpo = json.dumps(blocos, ensure_ascii=False, indent=2)

    def slug(texto):
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto
                        if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9\s-]", "",
                      texto.lower()).strip().replace(" ", "-")

    titulos = [b["h2"] for b in blocos if "h2" in b]
    cabecalhos = ", ".join(
        "{ id: '%s', text: %s, level: 2 as const }"
        % (slug(t), json.dumps(t, ensure_ascii=False)) for t in titulos)

    descricao = (f"Os {total} símbolos do módulo, agrupados por assunto, "
                 f"com a assinatura extraída do código-fonte.")

    return f'''import type {{ Metadata }} from 'next';
import type {{ Bloco }} from '@/lib/content';
import {{ DocPage }} from '@/components/Doc';
import {{ Renderer }} from '@/components/Renderer';

// Gerado por tools/gerar_ref_vitrine.py — não edite à mão.

export const metadata: Metadata = {{
  title: "Referência da Vitrine",
  description: {json.dumps(descricao, ensure_ascii=False)},
}};

const blocos: Bloco[] = {corpo};

const headings = [{cabecalhos}];

export default function Page() {{
  return (
    <DocPage
      title="Referência da Vitrine"
      description={json.dumps(descricao, ensure_ascii=False)}
      href="/docs/vitrine/referencia"
      headings={{headings}}
    >
      <Renderer blocos={{blocos}} />
    </DocPage>
  );
}}
'''


def main():
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(construir())
    modulo = get_module("Arcane.Vitrine")
    print(f"referencia gerada: {os.path.relpath(DESTINO, RAIZ)}")
    print(f"  {len(modulo) - 1} simbolos em {len(GRUPOS)} grupos")


if __name__ == "__main__":
    main()
