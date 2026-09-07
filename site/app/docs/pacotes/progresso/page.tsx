import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "progresso",
  description: "Terminal: barra de progresso, spinner, contagem e tempo estimado.",
};

const blocos: Bloco[] = [
  { code: `dataforge add progresso`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "8 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Redesenha a mesma linha com `\\r`. Quando a saída não é um terminal — redirecionada para arquivo, ou num pipe — imprime uma linha por atualização, senão o log fica com um borrão de caracteres de controle."},
  {"h2": "Uso"},
  { code: `adopt progresso as P

b := P.barra(len(arquivos), "copiando")
cycle a in arquivos:
    copiar(a)
    b.avancar()
b.terminar()

copiando  ████████████░░░░░░░░  60%  12/20  ~4s`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 8 símbolos:"},
  { code: `blueprint Barra
blueprint Spinner
barra(total, rotulo := "", largura := 24)
spinner(rotulo := "")
duracao_legivel(segundos)
tamanho_legivel(bytes)
BLOCOS
QUADROS`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add progresso
dataforge add progresso@1.0.0
dataforge add progresso@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"progresso"}
      description={"Terminal: barra de progresso, spinner, contagem e tempo estimado."}
      href={"/docs/pacotes/progresso"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
