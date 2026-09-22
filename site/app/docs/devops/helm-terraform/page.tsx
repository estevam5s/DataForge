// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Helm e Terraform",
  description: "O chart para variar por ambiente, e o esqueleto de infraestrutura como código.",
};

const blocos: Bloco[] = [
  {"p": "Os manifestos de `k8s/` são um ambiente. Quando há três — desenvolvimento, homologação, produção —, copiar a pasta três vezes é o começo da divergência. O chart do Helm é **um** conjunto de modelos e um `values.yaml` por ambiente."},
  { code: `dataforge devops helm --registro=ghcr.io/minha-org
helm install loja ./chart -f chart/values.yaml
helm upgrade loja ./chart --set imagem.tag=1.4.2

dataforge devops terraform
cd infra && terraform init && terraform plan`, lang: 'bash' },
  {"table": {"head": ["Ferramenta", "Responde", "Não responde"], "rows": [["**Helm**", "o que roda **dentro** do cluster, e como varia por ambiente", "onde o cluster mora"], ["**Terraform**", "o que existe **fora**: cluster, banco gerenciado, DNS, bucket", "o que roda dentro dele"]]}},
  {"callout": {"tipo": "dica", "titulo": "O estado do Terraform é um segredo", "texto": "O `terraform.tfstate` guarda senhas e chaves em texto. Ele vai para um *backend* remoto com trava (S3 + DynamoDB, GCS, Terraform Cloud) — nunca para o repositório. O esqueleto gerado já traz o `.gitignore` com ele."}},
  {"h2": "O que o gerador não faz"},
  {"p": "Ele não fala com o cluster nem com a nuvem. `dataforge devops` gera **texto** e sai da frente: um `deploy` que falasse com Kubernetes por dentro esconderia o que a imagem é, e no dia em que alguém precisasse mudar uma camada não haveria onde mexer."},
  {"p": "Continue em [GitHub Actions](/docs/devops/github-actions)."},
];

const headings = [{ id: 'o-que-o-gerador-nao-faz', text: "O que o gerador não faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Helm e Terraform"}
      description={"O chart para variar por ambiente, e o esqueleto de infraestrutura como código."}
      href={"/docs/devops/helm-terraform"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
