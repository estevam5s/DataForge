// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Licença",
  description: "Por que uma biblioteca sem licença não pode ser usada, e o que cada família permite.",
};

const blocos: Bloco[] = [
  {"p": "Código sem licença é, por padrão, **todos os direitos reservados**: ninguém pode usar, copiar ou modificar legalmente, por mais pública que seja a página. Uma biblioteca sem licença é uma biblioteca que uma empresa não pode adotar."},
  { code: `[project]
name = "placa"
version = "1.0.0"
license = "MIT"            # o identificador SPDX`, lang: 'toml', title: `forge.toml` },
  {"table": {"head": ["Família", "Exemplos", "Quem usa pode…", "Exige"], "rows": [["permissiva", "MIT, BSD, Apache-2.0", "usar em código fechado", "manter o aviso de copyright"], ["copyleft fraca", "MPL-2.0, LGPL", "usar em código fechado", "publicar mudanças **no arquivo** da biblioteca"], ["copyleft forte", "GPL-3.0", "usar", "publicar o programa inteiro que a inclui"], ["rede", "AGPL-3.0", "usar", "publicar o código mesmo quando só oferecido como serviço"]]}},
  {"callout": {"tipo": "nota", "titulo": "Isto não é parecer jurídico", "texto": "A tabela é o resumo que ajuda a escolher. Para um caso específico — uma dependência com licença diferente da sua, um cliente com política própria —, consulte quem responde por isso na sua organização."}},
  {"p": "A linguagem é MIT; os pacotes deste repositório também. Apache-2.0 acrescenta uma concessão explícita de patente, o que algumas empresas exigem."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Licença"}
      description={"Por que uma biblioteca sem licença não pode ser usada, e o que cada família permite."}
      href={"/docs/bibliotecas/licenca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
