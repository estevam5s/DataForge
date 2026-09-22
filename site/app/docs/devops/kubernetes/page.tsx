// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Kubernetes",
  description: "Deployment, Service, Ingress, ConfigMap e HPA — com sondas e limites, que é o que falta em quase todo manifesto.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge devops k8s` escreve os cinco manifestos em `k8s/`. O Ingress e o HPA só saem quando o projeto é um servidor — um *job* que processa uma fila não recebe tráfego, e um Ingress para ele seria uma porta aberta para nada."},
  { code: `dataforge devops k8s --registro=ghcr.io/minha-org --dominio=loja.exemplo.com
kubectl apply -f k8s/
kubectl rollout status deploy/loja`, lang: 'bash' },
  {"h2": "As duas sondas não são a mesma pergunta"},
  {"table": {"head": ["Sonda", "Pergunta", "Se falha"], "rows": [["`readinessProbe`", "posso receber tráfego **agora**?", "sai do Service, e volta quando responder"], ["`livenessProbe`", "ainda estou vivo?", "o pod é **reiniciado**"], ["`startupProbe`", "já terminei de subir?", "as outras duas esperam"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Liveness que depende do banco derruba tudo", "texto": "Se a sonda de vida consulta o banco, uma lentidão no banco reinicia **todos** os pods ao mesmo tempo — e eles voltam juntos, martelando o banco que já estava lento. A sonda de vida pergunta só se o processo responde; a de prontidão pode olhar as dependências."}},
  {"h2": "Limites"},
  {"table": {"head": ["No manifesto", "Sem ele"], "rows": [["`resources.requests`", "o agendador não sabe onde o pod cabe, e empilha tudo num nó"], ["`resources.limits.memory`", "um vazamento come o nó inteiro, e derruba os vizinhos"], ["`HorizontalPodAutoscaler`", "o pico de tráfego encontra o mesmo número de réplicas da madrugada"], ["`securityContext.runAsNonRoot`", "a imagem que alguém trocou por uma que roda como root sobe sem aviso"]]}},
  {"p": "Continue em [Helm e Terraform](/docs/devops/helm-terraform)."},
];

const headings = [{ id: 'as-duas-sondas-nao-sao-a-mesma-pergunta', text: "As duas sondas não são a mesma pergunta", level: 2 as const }, { id: 'limites', text: "Limites", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Kubernetes"}
      description={"Deployment, Service, Ingress, ConfigMap e HPA — com sondas e limites, que é o que falta em quase todo manifesto."}
      href={"/docs/devops/kubernetes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
