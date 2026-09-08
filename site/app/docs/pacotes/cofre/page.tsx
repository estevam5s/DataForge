import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "cofre",
  description: "Configuração em camadas: padrões, arquivo, ambiente e argumentos, com tipos e validação.",
};

const blocos: Bloco[] = [
  { code: `dataforge add cofre`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "17 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "A ordem de precedência é sempre a mesma: argumento ganha de ambiente, que ganha de arquivo, que ganha de padrão. E `origem()` responde de onde veio cada valor — a pergunta que se faz quando algo está errado em produção."},
  {"h2": "Uso"},
  { code: `adopt cofre as C

cfg := C.novo()
cfg := C.padroes(cfg, {"porta": 8080, "debug": no})
cfg := C.do_arquivo(cfg, "config.json")
cfg := C.do_ambiente(cfg, "MEUAPP_")
cfg := C.dos_argumentos(cfg)

out C.pegar(cfg, "porta")`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 17 símbolos:"},
  { code: `record Config
novo()
padroes(cfg, mapa)
do_arquivo(cfg, caminho, obrigatorio := no)
do_ambiente(cfg, prefixo := "")
dos_argumentos(cfg, argumentos := void)
pegar(cfg, chave, padrao := void)
tem(cfg, chave)
origem(cfg, chave)
definir(cfg, chave, valor)
tudo(cfg)
exigir(cfg, chaves)
explicar(cfg)
como_inteiro(cfg, chave, padrao := 0)
como_texto(cfg, chave, padrao := "")
como_booleano(cfg, chave, padrao := no)
como_lista(cfg, chave, separador := ",", padrao := void)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add cofre
dataforge add cofre@1.0.0
dataforge add cofre@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"cofre"}
      description={"Configuração em camadas: padrões, arquivo, ambiente e argumentos, com tipos e validação."}
      href={"/docs/pacotes/cofre"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
