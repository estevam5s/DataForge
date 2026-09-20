// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fechamento.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Versões lado a lado",
  description: "versions, use, switch e upgrade: uma venv por versão, o pino no forge.toml — e o pino é cobrado, não apenas mostrado.",
};

const blocos: Bloco[] = [
  {"p": "Havia um jeito de **instalar** e nenhum de **escolher**: trocar de versão era reinstalar por cima, e não havia como dizer *\"este projeto roda na 1.0.0\"*."},
  {"callout": {"tipo": "perigo", "titulo": "E metade do mecanismo já existia, sem ninguém cobrar", "texto": "O campo `project.dataforge` do `forge.toml` existia, e `Manifest.requires()` já sabia ler `>=`, `^` e `~`. **O único lugar que os usava era `dataforge info`, para mostrar na tela.** Um pino que não é cobrado não é um pino: é um comentário com sintaxe."}},
  {"h2": "Onde as versões moram"},
  { code: `~/.dataforge/
├── versoes/
│   ├── 1.0.0/          uma venv por versao
│   └── 2.0.0/
└── atual               a escolha GLOBAL`, lang: 'text', title: `a raiz — ou DATAFORGE_RAIZ` },
  {"p": "`DATAFORGE_RAIZ` troca a raiz. Não é um detalhe de conveniência: é o que torna tudo isto **testável** sem mexer na instalação de quem está rodando os testes."},
  { code: `dataforge versions            # o que existe, o que roda, o que o projeto exige
dataforge upgrade             # instala a mais nova AO LADO
dataforge upgrade 1.0.0 --check   # so diz o que faria
dataforge use 1.0.0           # fixa no projeto (forge.toml)
dataforge use 1.0.0 --global  # fixa para a maquina
dataforge switch 1.0.0        # o mesmo comando, outro nome`, lang: 'bash' },
  {"h2": "O pino é cobrado — senão `use` seria um gesto"},
  {"p": "`dataforge run` num projeto que exige outra versão **entrega a execução a ela**. São três saídas, e a terceira é a que importa:"},
  {"table": {"head": ["Situação", "O que acontece"], "rows": [["não há pino, ou ele é satisfeito", "segue nesta versão, e o custo é uma leitura de `forge.toml`"], ["há pino e a versão está instalada", "**troca** (`os.execve`), e a outra versão recebe os mesmos argumentos"], ["há pino e ela **não** está instalada", "**recusa**, com o comando que a instala"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Por que recusar, e não avisar", "texto": "Rodar na versão errada é exatamente o que o pino existe para impedir. Um aviso seria ignorado na segunda vez, e a diferença entre as versões aparece como um defeito no código de quem escreveu — não como um problema de versão. `DATAFORGE_SEM_TROCA=1` ignora o pino quando você quer, uma vez."}},
  { code: `$ dataforge run main.df
Erro: o projeto exige DataForge 9.9.9, e esta e a 1.0.0, e a 9.9.9 nao esta instalada.
      dataforge upgrade 9.9.9
      dataforge versions          (o que existe aqui)
      DATAFORGE_SEM_TROCA=1 dataforge run …   (ignorar o pino, uma vez)`, lang: 'bash', title: `a recusa, com as três saídas` },
  {"p": "E uma marca no ambiente impede a troca de acontecer **duas vezes**: um executável mal configurado que apontasse para si mesmo entraria em laço, e um laço na partida é o defeito mais difícil de interromper."},
  {"h2": "O manifesto é de uma pessoa, e não é reformatado"},
  {"p": "`use` reescreve o `forge.toml` **linha a linha**. Serializar o TOML de novo a partir da estrutura apagaria comentários e reordenaria campos — e um comando que mexe num arquivo de configuração não pode reformatá-lo por baixo."},
  { code: `# o meu projeto            <- o comentario fica
[project]
name = "loja"
version = "0.1.0"
entry = "main.df"
dataforge = "1.0.0"        <- entra DENTRO da secao, na ultima linha dela

[dependencies]             <- e a outra secao continua onde estava`, lang: 'text', title: `forge.toml depois de 'dataforge use 1.0.0'` },
  {"p": "O campo entra depois da **última linha com conteúdo** da seção, e não no fim dela: uma linha em branco separa as seções, e inserir depois dela punha o campo do `[project]` visualmente na seção seguinte. Fixar de novo **troca** em vez de duplicar."},
  {"h2": "O que não existe, e é o limite"},
  {"table": {"head": ["Não há", "Consequência"], "rows": [["um *shim* no PATH", "o `dataforge` que você chama é o que está instalado, e é ele que redireciona — quem instala a 2.0.0 e quer que ela atenda direto ainda precisa reinstalar"], ["troca no `check`, no `fmt` e nos outros", "a troca vale no `run`. Conferir sintaxe numa versão vizinha quase nunca muda a resposta, e re-executar todo comando dobraria a partida"], ["instalação sem rede", "`upgrade` usa `pip`. Sem rede, `--check` mostra os passos que ele daria"]]}},
];

const headings = [{ id: 'onde-as-versoes-moram', text: "Onde as versões moram", level: 2 as const }, { id: 'o-pino-e-cobrado-senao-use-seria-um-gesto', text: "O pino é cobrado — senão `use` seria um gesto", level: 2 as const }, { id: 'o-manifesto-e-de-uma-pessoa-e-nao-e-reformatado', text: "O manifesto é de uma pessoa, e não é reformatado", level: 2 as const }, { id: 'o-que-nao-existe-e-e-o-limite', text: "O que não existe, e é o limite", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Versões lado a lado"}
      description={"versions, use, switch e upgrade: uma venv por versão, o pino no forge.toml — e o pino é cobrado, não apenas mostrado."}
      href={"/docs/cli/versoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
