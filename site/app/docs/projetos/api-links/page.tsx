import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "API de links",
  description: "Encurtador de URL com servidor HTTP, validação e cache.",
};

const blocos: Bloco[] = [
  { code: `dataforge run src/main.df

curl -X POST localhost:8080/encurtar -d '{"url":"https://exemplo.com/pagina"}'
# {"codigo": "xYAXp7", "url": "https://exemplo.com/pagina"}   201

curl localhost:8080/xYAXp7        # 200
curl localhost:8080/naoexiste     # 404
curl localhost:8080/estatisticas  # os mais acessados`, lang: 'bash' },
  {"h2": "Regra separada de transporte"},
  {"p": "Toda a lógica está em `encurtador.df`, sem uma linha de HTTP. Os 11 testes rodam em milissegundos e não sobem servidor; `main.df` é uma casca de trinta linhas."},
  {"p": "Testar HTTP é lento e frágil. Se a regra estivesse dentro do handler, cada teste precisaria de porta, requisição e espera."},
  {"h2": "O alfabeto evita ambiguidade"},
  { code: `steady ALFABETO := "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
steady TAMANHO_CODIGO := 6`, lang: 'df' },
  {"p": "Sem `l`, `I`, `0` nem `O` — quem lê um código em voz alta ou copia de um papel não erra."},
  {"h2": "400, não 500"},
  {"p": "Uma URL inválida é erro de quem chamou, não falha do servidor. O status precisa dizer de quem é a responsabilidade — e o cliente que recebe 500 tenta de novo, enquanto o que recebe 400 corrige a requisição."},
  {"h2": "Semente no gerador"},
  {"p": "`E.novo(42)` produz sempre os mesmos códigos, o que torna o teste reproduzível. Sem semente, usa o relógio."},
];

const headings = [{ id: 'regra-separada-de-transporte', text: "Regra separada de transporte", level: 2 as const }, { id: 'o-alfabeto-evita-ambiguidade', text: "O alfabeto evita ambiguidade", level: 2 as const }, { id: '400-nao-500', text: "400, não 500", level: 2 as const }, { id: 'semente-no-gerador', text: "Semente no gerador", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"API de links"}
      description={"Encurtador de URL com servidor HTTP, validação e cache."}
      href={"/docs/projetos/api-links"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
