import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "cofre",
  description: "Configuração em camadas: padrão, arquivo, ambiente e argumentos.",
};

const blocos: Bloco[] = [
  { code: `dataforge add cofre`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"]]}},
  {"h2": "Por que existe"},
  {"p": "A ordem de precedência é sempre a mesma — argumento ganha de ambiente, que ganha de arquivo, que ganha de padrão. E `origem()` responde de onde veio cada valor, que é a pergunta que se faz quando algo está errado em produção."},
  {"h2": "Exemplo"},
  { code: `adopt cofre as C

cfg := C.novo()
cfg := C.padroes(cfg, {"porta": 8080, "debug": no})
cfg := C.do_arquivo(cfg, "config.json")
cfg := C.do_ambiente(cfg, "MEUAPP_")
cfg := C.dos_argumentos(cfg)

out C.pegar(cfg, "porta")
out C.origem(cfg, "porta")     // argumentos
out C.explicar(cfg)

C.exigir(cfg, ["porta", "banco_url"])   // falha cedo se faltar`, lang: 'df' },
  {"h2": "API"},
  {"table": {"head": ["Função", "O que faz"], "rows": [["`novo()`", "começa vazio"], ["`padroes(cfg, mapa)`", "a camada de baixo"], ["`do_arquivo(cfg, caminho)`", "JSON, TOML ou INI"], ["`do_ambiente(cfg, prefixo)`", "variáveis de ambiente"], ["`dos_argumentos(cfg)`", "`--chave valor`, `--chave=valor`, `--flag`, `--no-flag`"], ["`pegar(cfg, chave, padrao)`", "lê um valor"], ["`origem(cfg, chave)`", "de que camada veio"], ["`exigir(cfg, chaves)`", "falha listando o que falta"], ["`como_inteiro/texto/booleano/lista`", "leitura com tipo"], ["`explicar(cfg)`", "tudo, com a origem de cada um"]]}},
  {"h2": "Instalar"},
  { code: `dataforge add cofre
dataforge add cofre@1.0.0
dataforge add cofre@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'exemplo', text: "Exemplo", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"cofre"}
      description={"Configuração em camadas: padrão, arquivo, ambiente e argumentos."}
      href={"/docs/pacotes/cofre"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
