// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/desktop.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Empacotar",
  description: ".app, .exe e binário — e as três coisas que o PyInstaller cobra sem avisar.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge desktop empacotar` gera o lançador e chama o **PyInstaller**. É a mesma escolha do `iot carregar`, que chama o `arduino-cli`: empacotar um interpretador Python é um problema resolvido, e resolvê-lo de novo daria um subconjunto pior amarrado a esta linguagem."},
  { code: `$ dataforge desktop doctor
  ✓ Tk                   versão 8.6
  ✓ display              há para onde desenhar
  ✓ PyInstaller          /usr/local/bin/pyinstaller
  ✓ alvo desta máquina   .app (macOS)

$ dataforge desktop empacotar src/main.df --nome=Caixa
empacotando 'Caixa'…
pronto: dist/`, lang: 'bash' },
  {"h2": "As três coisas que ele cobra sem avisar"},
  {"table": {"head": ["O quê", "O sintoma", "O que o comando faz"], "rows": [["import lazy", "\"No module named 'dataforge'\" — parece falta de instalação", "o lançador importa no **topo**, onde a análise estática enxerga"], ["instalação editável", "idem, e só na máquina de quem desenvolve", "passa `--paths` com a raiz do pacote"], ["só o arquivo de entrada", "morre no primeiro `adopt ./vizinho`", "empacota a **pasta inteira** do programa"]]}},
  {"p": "As três produzem o mesmo tipo de falha: o executável **monta, abre e morre** — e a mensagem fala de uma biblioteca que quem escreveu nunca viu. Foram os três defeitos desta implementação, nesta ordem."},
  {"h2": "E a guarda do `__main__`"},
  { code: `// O lançador gerado tem isto, e não é decoração:
//
//     if __name__ == "__main__":
//         multiprocessing.freeze_support()
//         main()
//
// Sem ela, o 'spawn' de map_processos reexecuta o APLICATIVO INTEIRO
// em cada trabalhador — e a mensagem fala de "bootstrapping phase",
// vocabulário do multiprocessing, três camadas longe de quem chamou.
adopt Arcane.Concurrent as C
assert C.nucleos() >= 1
out "num executável congelado, freeze_support() vem ANTES de main()"`, lang: 'df' },
  {"h2": "O que sai, por sistema"},
  {"table": {"head": ["Sistema", "Sai", "O que o usuário vê"], "rows": [["macOS", "`dist/Nome.app` e `dist/Nome`", "o aviso do Gatekeeper até você assinar e notarizar"], ["Windows", "`dist/Nome.exe`", "o SmartScreen, até o executável ter reputação ou assinatura"], ["Linux", "`dist/Nome`", "depende da libc de quem construiu — construa na distro mais antiga que você suporta"]]}},
  {"h2": "O que NÃO existe"},
  {"list": ["**Assinatura e notarização** — é conta de desenvolvedor da Apple, e o comando não a pede nem a esconde.", "**Instalador** (`.dmg`, `.msi`, `.deb` do seu app) — o que sai é o executável.", "**Atualização automática.**", "**Compilação cruzada**: um `.exe` se faz no Windows, e um `.app` no macOS. O PyInstaller não cruza, e nenhuma opção aqui finge que cruza."]},
  {"callout": {"tipo": "atencao", "titulo": "O binário é grande, e isso é o interpretador", "texto": "Um app de tela simples sai com ~9 MB porque ele **carrega o Python inteiro** junto. É o preço de distribuir para quem não tem nada instalado — e é o mesmo preço do binário da própria CLI."}},
];

const headings = [{ id: 'as-tres-coisas-que-ele-cobra-sem-avisar', text: "As três coisas que ele cobra sem avisar", level: 2 as const }, { id: 'e-a-guarda-do-main', text: "E a guarda do `__main__`", level: 2 as const }, { id: 'o-que-sai-por-sistema', text: "O que sai, por sistema", level: 2 as const }, { id: 'o-que-nao-existe', text: "O que NÃO existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Empacotar"}
      description={".app, .exe e binário — e as três coisas que o PyInstaller cobra sem avisar."}
      href={"/docs/desktop/empacotar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
