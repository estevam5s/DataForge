import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Levar para produção",
  description: "O que muda quando o servidor sai da sua máquina.",
};

const blocos: Bloco[] = [
  {"h2": "As três formas de rodar"},
  {"table": {"head": ["Forma", "Faz", "Quando"], "rows": [
    ["`Kiln.test(app, verbo, caminho)`", "executa a rota, sem socket", "teste"],
    ["`Kiln.serve(app, porta)`", "sobe em segundo plano, devolve a porta", "script, teste de integração"],
    ["`ignite app on 8080`", "sobe e bloqueia até Ctrl-C", "produção"]
  ]}},
  {"p": "`Kiln.serve(app, 0)` deixa o sistema escolher uma porta livre e devolve qual foi — numa suíte de testes, porta fixa dá conflito assim que dois testes rodam juntos."},
  {"h2": "Separar quem monta de quem acende"},
  { code: `// app.df — monta e NÃO sobe nada
server loja on 8080:
    route GET "/": …
relay loja

// main.df — lê a porta e acende
adopt app as App
ignite App.loja on porta` },
  {"p": "Não é enfeite: um teste que importasse o `main` subiria o servidor e **nunca terminaria**."},
  {"h2": "A porta e o endereço"},
  { code: `adopt Arcane.OS as OS

porta := int(OS.env("PORT") ?? "8080")
ignite loja on porta at "0.0.0.0"` },
  {"p": "O padrão é `127.0.0.1`, que só aceita conexões da própria máquina. Num contêiner você precisa de `0.0.0.0` — e precisa ter certeza de que há algo entre ele e a internet."},
  {"h2": "O que colocar na frente"},
  {"p": "O Kiln roda sobre o `http.server` do Python. Ele é sólido para uma aplicação interna, um painel, uma API de time — e não é um servidor de borda. Em produção pública, ponha um nginx ou um Caddy na frente para cuidar de TLS, compressão, arquivos estáticos e clientes lentos."},
  {"h2": "Uma thread por pedido"},
  {"p": "Cada pedido roda numa thread. Duas consequências que valem lembrar:"},
  {"table": {"head": ["", "O que fazer"], "rows": [
    ["estado compartilhado", "duas threads que escrevem na mesma variável podem perder atualizações — a linguagem não sincroniza threads"],
    ["banco de dados", "o `Arcane.Database` serializa o acesso, então funciona; uma transação, porém, **não** é isolada por thread"]
  ]}},
  {"p": "Para trabalho transacional concorrente, abra uma conexão por thread. Para contadores e caches em memória, lembre que o resultado sob carga pode não ser o que você esperava."},
  {"h2": "Modo debug"},
  { code: `Kiln.config(app, "debug", yes)` },
  {"p": "Com `debug`, o corpo do 500 traz a mensagem do erro e o traceback sai no terminal. **Deixe desligado em produção**: a mensagem de erro descreve a sua implementação para quem estiver olhando."},
  {"h2": "Antes de publicar"},
  {"table": {"head": ["Item", "Por quê"], "rows": [
    ["`debug` desligado", "a mensagem de erro descreve o seu código"],
    ["cookies com `seguro: yes`", "sem isso, o cookie de sessão viaja em HTTP"],
    ["`Kiln.cors` com origem, não `*`", "`*` deixa qualquer site chamar sua API"],
    ["`rate_limit` nas rotas de escrita", "o teto contém abuso acidental"],
    ["`limite_corpo` ajustado", "o padrão de 10 MB pode ser demais"],
    ["`assets` apontando só para o público", "`.git` e `.env` moram no mesmo disco"],
    ["senhas com hash lento e sal", "o Kiln não faz isso por você"],
    ["sessão no banco, se houver 2+ processos", "em memória, o visitante desloga"],
    ["log em arquivo, não só no terminal", "`Kiln.logger` escreve na saída padrão"]
  ]}},
  {"h2": "Em Docker"},
  { code: `FROM estevan5s/dataforge:4.2.0
WORKDIR /app
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["run", "src/main.df"]` },
  {"p": "A imagem oficial já traz a linguagem e a biblioteca inteira; não há `pip install` nem `npm install` porque não há dependência nenhuma para instalar."},
  {"h2": "Saber o que está acontecendo"},
  { code: `numeros := Kiln.stats(app)
out numeros["pedidos"], numeros["erros"], numeros["uptime"]` },
  {"p": "Toda resposta também sai com `X-Response-Time`, o que dá para medir latência sem instrumentar nada."},
];

const headings = [{ id: 'as-tres-formas-de-rodar', text: "As três formas de rodar", level: 2 as const }, { id: 'separar-quem-monta-de-quem-acende', text: "Separar quem monta de quem acende", level: 2 as const }, { id: 'a-porta-e-o-endereco', text: "A porta e o endereço", level: 2 as const }, { id: 'o-que-colocar-na-frente', text: "O que colocar na frente", level: 2 as const }, { id: 'uma-thread-por-pedido', text: "Uma thread por pedido", level: 2 as const }, { id: 'modo-debug', text: "Modo debug", level: 2 as const }, { id: 'antes-de-publicar', text: "Antes de publicar", level: 2 as const }, { id: 'em-docker', text: "Em Docker", level: 2 as const }, { id: 'saber-o-que-esta-acontecendo', text: "Saber o que está acontecendo", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Levar para produção"}
      description={"O que muda quando o servidor sai da sua máquina."}
      href={"/docs/kiln/producao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
