// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Componentes",
  description: "Os quarenta componentes da Vitrine: texto, entrada, dados e retorno — e o que cada um devolve.",
};

const blocos: Bloco[] = [
  {"p": "Todo componente faz duas coisas: **põe um nó na árvore** e **devolve o que quem escreve precisa**. É essa devolução que dispensa callback."},
  {"h2": "Texto"},
  { code: `V.titulo("Vendas", icone := "📊")
V.subtitulo("Primeiro semestre")
V.cabecalho("Por região", nivel := 3)
V.texto("Um parágrafo.")
V.markdown("**negrito**, \`código\`, [link](/docs) e tabelas.")
V.codigo("x := 10", linguagem := "dataforge")
V.divisor()
V.espaco(24)`, lang: 'df' },
  {"p": "`V.texto` aceita vários argumentos e junta com espaço, como o `out`."},
  {"callout": {"tipo": "atencao", "titulo": "V.html não escapa nada", "texto": "`V.html(\"<b>x</b>\")` insere o HTML cru. É a única porta de XSS da Vitrine, e ela existe porque às vezes não há alternativa. **Nunca passe por ali algo que veio do usuário** — para isso, `V.texto`, que escapa."}},
  {"h2": "Entrada"},
  {"table": {"head": ["Componente", "Devolve", "Para"], "rows": [["`V.botao(rótulo)`", "`yes` no ciclo do clique", "uma ação"], ["`V.entrada(rótulo)`", "o texto digitado", "uma linha de texto"], ["`V.area_de_texto(rótulo)`", "o texto digitado", "várias linhas"], ["`V.numero(rótulo)`", "o número", "quantidade, com mínimo e máximo"], ["`V.deslizante(rótulo, min, max)`", "o número", "escolher numa faixa"], ["`V.caixa(rótulo)`", "`yes`/`no`", "uma opção ligada ou desligada"], ["`V.interruptor(rótulo)`", "`yes`/`no`", "o mesmo, com cara de chave"], ["`V.opcao(rótulo, opções)`", "a escolhida", "uma de poucas, em rádio"], ["`V.escolha(rótulo, opções)`", "a escolhida", "uma de muitas, em lista"], ["`V.escolhas(rótulo, opções)`", "um cluster", "várias de muitas"], ["`V.data(rótulo)`", "`\"2026-03-14\"`", "uma data"], ["`V.cor(rótulo)`", "`\"#FED403\"`", "uma cor"], ["`V.arquivo(rótulo)`", "`void` ou o vault do arquivo", "enviar arquivo"]]}},
  { code: `nome := V.entrada("Nome", "", dica := "como no documento")
senha := V.entrada("Senha", tipo := "senha")
idade := V.numero("Idade", 18, minimo := 0, maximo := 120)
fatia := V.deslizante("Desconto", 0, 100, valor := 10, passo := 5)
tags  := V.escolhas("Tags", ["novo", "urgente", "revisar"])`, lang: 'df' },
  {"h3": "O botão vale por uma execução"},
  {"p": "`V.botao` devolve `yes` **só** no ciclo em que foi clicado. Se fosse permanente, a ação dispararia de novo no próximo carregamento da página — e duplicar um pagamento é o tipo de bug que ninguém perdoa."},
  {"h3": "Formulário: quando cada tecla custa caro"},
  {"p": "Sem formulário, **cada tecla digitada roda o programa inteiro**. Num campo ligado a uma consulta pesada, isso é a diferença entre um app usável e um que trava a cada letra."},
  { code: `forma := V.formulario("cadastro")
nome  := forma.entrada("Nome")
email := forma.entrada("E-mail", tipo := "email")

given forma.enviar("Cadastrar"):
    criar_usuario(nome, email)
    V.sucesso("Usuário cadastrado.")`, lang: 'df' },
  {"p": "Dentro do formulário, os valores só chegam ao programa quando alguém aperta o botão de envio. Com `limpar := yes`, os campos são esvaziados depois — e só os **deste** formulário, não os da página inteira."},
  {"h3": "Arquivos"},
  { code: `arq := V.arquivo("Planilha", tipos := [".csv"], varios := no)
given arq is not void:
    V.texto($"{arq["nome"]} — {arq["tamanho"]} bytes")
    linhas := arq["texto"].lines()
    V.tabela(linhas)`, lang: 'df' },
  {"p": "O vault tem `nome`, `tamanho`, `tipo`, `conteudo` (bytes) e `texto`. Com `varios := yes`, devolve um cluster deles. O teto padrão é 8 MB, ajustável em `V.configurar(\"limite_upload\", …)`."},
  {"h3": "Validação"},
  {"p": "O erro aparece **sob o campo**, e não num alerta no topo. Num formulário de doze campos, um alerta dizendo \"há erros\" obriga a pessoa a caçar qual deles — e é a diferença entre corrigir na hora e desistir."},
  { code: `adopt Arcane.Regex as Regex

email := V.entrada("E-mail")
V.validar(email, Regex.is_email, "Digite um e-mail válido.")

// ou com a regra junto, devolvendo (valor, esta_bom)
senha, ok := V.campo_validado("Senha", lambda s: len(s) bigger 7,
                              "Mínimo de 8 caracteres.", tipo := "senha")`, lang: 'df' },
  {"p": "A regra é uma ação que recebe o valor e devolve `yes`/`no` — e aí a mensagem é a que você passou — ou um **texto**, que vira a mensagem (vazio significa que passou)."},
  { code: `V.validar(senha, lambda s: "" given len(s) bigger 7
                            otherwise $"faltam {8 - len(s)} caracteres")`, lang: 'df' },
  {"table": {"head": ["Comportamento", "Por quê"], "rows": [["campo vazio e nunca tocado não é acusado", "reclamar antes de a pessoa digitar é ruído, não ajuda"], ["uma regra que **dispara** vira \"a regra de validação falhou\"", "dizer \"E-mail inválido\" ali esconderia o bug real"], ["o campo ganha `aria-invalid` e aponta para a mensagem", "senão quem não vê a tela descobre o erro só ao voltar nele, se voltar"]]}},
  {"h2": "Dados"},
  { code: `V.tabela(linhas)                      // estática
V.frame(linhas)                       // com busca e ordenação
V.metrica("Receita", "R$ 850 mil", variacao := 18.0, ajuda := "vs. meta")
V.json(vault)
V.vault(vault)                        // lista de chave e valor`, lang: 'df' },
  {"p": "`V.tabela` e `V.frame` aceitam **três formas**, porque são as três que o resto da linguagem devolve:"},
  {"table": {"head": ["Forma", "Exemplo", "Vem de"], "rows": [["cluster de vaults", "`[{\"a\": 1}, {\"a\": 2}]`", "`IO.read_csv`, `Banco.consultar`"], ["vault de colunas", "`{\"a\": [1, 2]}`", "um `group_by`"], ["matriz", "`[[1, 2], [3, 4]]`", "cálculo direto"]]}},
  {"p": "Um `frame` do `Arcane.Analytics` também entra direto. A ordem das colunas é a de **aparição**, e não a alfabética: quem montou o vault escolheu uma ordem, e ela costuma ser a certa."},
  {"p": "A variação da métrica é um **número** e não um texto, porque a Vitrine precisa saber o sinal: ela sobe em verde e desce em vermelho."},
  {"h2": "Retorno ao usuário"},
  { code: `V.sucesso("Salvo.")
V.erro("Não foi possível salvar.")
V.aviso("Isto não pode ser desfeito.")
V.informacao("Os dados são de ontem.")

V.progresso(0.62, "62% processado")
V.carregando("Consultando o banco…")

V.imagem("/static/grafico.png", legenda := "Vendas")
V.audio("/static/podcast.mp3")
V.video("/static/tour.mp4")
V.link("Documentação", "/docs", nova_aba := yes)
V.baixar("Baixar relatório", texto, "relatorio.txt")`, lang: 'df' },
  {"p": "Para exportar dados já formatados, `V.exportar_csv(linhas)` e `V.exportar_json(dados)` desenham o botão e cuidam do escape."},
  {"h2": "Componentes próprios"},
  {"p": "Uma ação **já é** um componente. Chamá-la desenha o que ela desenha, e nada além disso é necessário:"},
  { code: `action cartao_de_usuario(nome, email):
    caixa := V.cartao(nome)
    caixa.texto(email)

cartao_de_usuario("Ana", "ana@exemplo.br")`, lang: 'df' },
  {"p": "O registro por nome existe para o caso em que o nome precisa atravessar módulos — um plugin que acrescenta componentes, ou um tema que substitui um deles sem que quem chama saiba:"},
  { code: `V.componente("usuario", cartao_de_usuario)
V.usar("usuario", "Ana", "ana@exemplo.br")

// também serve de decorador
mark @V.componente("usuario")
action cartao_de_usuario(nome, email):
    …`, lang: 'df' },
  {"p": "O registro vive na **aplicação**, e não no módulo: dois apps no mesmo processo — o que os testes fazem o tempo todo — não podem ver os componentes um do outro. E um nome errado sugere o parecido, em vez de falhar em silêncio."},
];

const headings = [{ id: 'texto', text: "Texto", level: 2 as const }, { id: 'entrada', text: "Entrada", level: 2 as const }, { id: 'o-botao-vale-por-uma-execucao', text: "O botão vale por uma execução", level: 3 as const }, { id: 'formulario-quando-cada-tecla-custa-caro', text: "Formulário: quando cada tecla custa caro", level: 3 as const }, { id: 'arquivos', text: "Arquivos", level: 3 as const }, { id: 'validacao', text: "Validação", level: 3 as const }, { id: 'dados', text: "Dados", level: 2 as const }, { id: 'retorno-ao-usuario', text: "Retorno ao usuário", level: 2 as const }, { id: 'componentes-proprios', text: "Componentes próprios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Componentes"}
      description={"Os quarenta componentes da Vitrine: texto, entrada, dados e retorno — e o que cada um devolve."}
      href={"/docs/vitrine/componentes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
