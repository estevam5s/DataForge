// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Preferências e tema",
  description: "O que a aplicação lembra entre uma abertura e outra, na pasta certa de cada sistema — e o tema claro, escuro ou o do sistema.",
};

const blocos: Bloco[] = [
  {"h2": "Preferências"},
  {"p": "`t.pref(chave, padrão)` lê; `t.guardar_pref(chave, valor)` grava **na hora**, num `preferencias.json`. A gravação escreve ao lado e troca o arquivo: uma aplicação fechada no meio não deixa um JSON pela metade. E um arquivo corrompido não impede a aplicação de abrir — ela volta aos padrões."},
  { code: `adopt Arcane.Bigorna as B
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}"
app := B.app("Notas", pasta_de_config := pasta)

action tela(t):
    tamanho := t.pref("fonte", 14)
    t.texto($"fonte {tamanho}")
    given t.botao("Aumentar"):
        t.guardar_pref("fonte", tamanho + 2)
        t.atualizar()

app.tela("t", tela)

B.testar(app).clicar("Aumentar")

// Outra execução da aplicação lê o que ficou gravado.
de_novo := B.app("Notas", pasta_de_config := pasta)
de_novo.tela("t", tela)
assert B.testar(de_novo).tem("fonte 16")`, lang: 'df' },
  {"h2": "Onde elas ficam"},
  {"table": {"head": ["Sistema", "Pasta"], "rows": [["macOS", "`~/Library/Application Support/<nome>`"], ["Windows", "`%APPDATA%\\<nome>`"], ["Linux", "`$XDG_CONFIG_HOME/<nome>`, ou `~/.config/<nome>`"]]}},
  { code: `adopt Arcane.Bigorna as B

out B.pasta_de_config("Minha Aplicação")`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Nunca ao lado do executável", "texto": "É o erro clássico: num `.app` assinado e em \"Arquivos de Programas\" a pasta do executável é só de leitura, e a preferência some sem erro nenhum. O `pasta_de_config` no `B.app` existe para o teste e para quem precisa de outra pasta — não para isso."}},
  {"h2": "Tema"},
  { code: `adopt Arcane.Bigorna as B

assert B.temas() is ["claro", "escuro", "sistema"]
escuro := B.app("Painel", tema := "escuro")
out escuro.tema`, lang: 'df' },
  {"p": "`sistema` (o padrão) deixa o Tk seguir o sistema — no macOS, o modo escuro vem sozinho. `claro` e `escuro` pintam fundo, campos, tabela e barra de status com uma paleta própria, igual nos três sistemas."},
];

const headings = [{ id: 'preferencias', text: "Preferências", level: 2 as const }, { id: 'onde-elas-ficam', text: "Onde elas ficam", level: 2 as const }, { id: 'tema', text: "Tema", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Preferências e tema"}
      description={"O que a aplicação lembra entre uma abertura e outra, na pasta certa de cada sistema — e o tema claro, escuro ou o do sistema."}
      href={"/docs/desktop/preferencias-e-tema"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
