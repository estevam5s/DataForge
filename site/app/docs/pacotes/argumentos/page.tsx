import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "argumentos",
  description: "Argumentos de linha de comando: flags, posicionais, subcomandos e ajuda automática.",
};

const blocos: Bloco[] = [
  { code: `dataforge add argumentos`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "3 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "A ajuda sai da mesma declaração que faz a leitura. Duas fontes para a mesma informação divergem na primeira vez que alguém tem pressa."},
  {"h2": "Uso"},
  { code: `adopt argumentos as Arg

p := Arg.programa("backup", "Faz backup de uma pasta")
p.posicional("origem", "a pasta a copiar")
p.opcao("destino", "d", "para onde copiar", "./backup")
p.flag("verboso", "v", "mostra cada arquivo")

r := p.processar(["/dados", "-d", "/mnt/hd", "-v"])
out r["origem"], r["destino"], r["verboso"]`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 3 símbolos:"},
  { code: `record Definicao
blueprint Programa
programa(nome, descricao := "")`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add argumentos
dataforge add argumentos@1.0.0
dataforge add argumentos@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"argumentos"}
      description={"Argumentos de linha de comando: flags, posicionais, subcomandos e ajuda automática."}
      href={"/docs/pacotes/argumentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
