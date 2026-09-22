// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Numa VM, sem contêiner",
  description: "A unidade systemd endurecida, o nginx na frente com TLS — e o que o Kiln não faz sozinho.",
};

const blocos: Bloco[] = [
  {"p": "Nem todo serviço precisa de um cluster. Uma VM pequena com systemd e nginx atende a maioria dos projetos — e tem menos peças para quebrar. `dataforge devops systemd` e `dataforge devops nginx` escrevem as duas."},
  { code: `dataforge devops systemd --usuario=loja
dataforge devops nginx --dominio=loja.exemplo.com

sudo useradd --system --home /srv/loja loja
sudo cp loja.service /etc/systemd/system/
sudo systemctl enable --now loja
sudo cp deploy/nginx.conf /etc/nginx/sites-enabled/loja
sudo certbot --nginx -d loja.exemplo.com`, lang: 'bash' },
  {"h2": "O endurecimento da unidade"},
  {"table": {"head": ["Diretiva", "O que ela contém"], "rows": [["`User=` sem privilégio", "a aplicação comprometida não é root"], ["`NoNewPrivileges=true`", "nem um binário *setuid* devolve o root"], ["`ProtectSystem=strict`", "o sistema de arquivos inteiro é somente-leitura…"], ["`ReadWritePaths=/srv/app/dados`", "…menos a pasta de dados, que é a única que ela escreve"], ["`ProtectHome` / `PrivateTmp`", "as pastas dos usuários somem, e o `/tmp` é só dela"], ["`Restart=on-failure`", "a queda às 3h volta sozinha, e o log diz por quê"]]}},
  {"h2": "Por que o nginx na frente"},
  {"p": "O Kiln roda sobre o `http.server` do Python: não tem **HTTP/2 nem TLS**. Em produção pública, o nginx (ou Caddy) termina o TLS, serve os estáticos, limita o corpo e repassa para o Kiln em `127.0.0.1`. O gerador já escreve o repasse de WebSocket e de SSE — sem os cabeçalhos de `Upgrade`, o tempo real para de funcionar atrás do proxy."},
  {"callout": {"tipo": "dica", "titulo": "Confira antes de subir", "texto": "`dataforge devops doctor` lê o projeto — sem executá-lo — e diz o que falta: porta, variáveis de ambiente, `0.0.0.0`, banco sem sonda. Ele funciona num projeto que não compila, que é quando ele é mais útil."}},
  {"p": "Volte para [DevOps](/docs/devops) ou veja [Observabilidade](/docs/tecnicas/observar)."},
];

const headings = [{ id: 'o-endurecimento-da-unidade', text: "O endurecimento da unidade", level: 2 as const }, { id: 'por-que-o-nginx-na-frente', text: "Por que o nginx na frente", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Numa VM, sem contêiner"}
      description={"A unidade systemd endurecida, o nginx na frente com TLS — e o que o Kiln não faz sozinho."}
      href={"/docs/devops/vm"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
