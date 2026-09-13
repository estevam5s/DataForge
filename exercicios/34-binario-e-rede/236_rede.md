# Exercicio 236 — TCP, UDP e DNS com `Arcane.Rede`

## Enunciado

Fale um protocolo próprio, abaixo do HTTP.

## O que faltava

O Kiln fala HTTP e a Malha fala com outro serviço. **Abaixo disso não havia
nada**: um protocolo próprio, um agente que manda uma linha por UDP, ou
descobrir para onde um nome aponta pediam sair da linguagem.

## O TCP não tem fronteira de mensagem

Esta é a ideia central do exercício. O TCP entrega um **fluxo de bytes**, e não
mensagens: o que você mandou em três `enviar` pode chegar num `receber` só, ou
ao contrário.

O formato mais comum para resolver isso é **tamanho + corpo**:

```dataforge
action mandar(conexao, texto):
    dados := Bytes.de_texto(texto)
    conexao.enviar(Bytes.empacotar(">u32", len(dados)))
    conexao.enviar(dados)

action receber(conexao):
    quanto := Bytes.desempacotar(">u32", conexao.receber_exato(4))[0]
    yield Bytes.para_texto(conexao.receber_exato(quanto))
```

## `receber_exato`, e não `receber`

O `recv` devolve **menos** do que se pediu com frequência num pedaço que
atravessa pacotes. Tratar o retorno curto como a mensagem inteira corrompe a
próxima — e o sintoma é uma conexão que funciona e de repente para.

No exercício, o teste com 5 000 caracteres existe justamente para atravessar
mais de um pacote.

## O prazo e o limite têm padrão

| Sem | O que acontece |
|-----|----------------|
| prazo | o outro lado caiu sem fechar o socket, e o `recv` espera um byte que nunca vem |
| limite na linha | um cliente que nunca manda `\n` enche a memória do servidor — um ataque de uma linha |

## UDP: manda e esquece

Sem conexão, sem ordem, sem garantia. Parece pior, e é o **certo** para
métrica, descoberta e log: perder um pacote custa menos que a espera de
confirmar cada um.

```dataforge
coletor := Rede.udp(porta := 8125, escutar := yes)
chegou := coletor.receber()
out chegou["host"], chegou["dados"]
```

Repare que `receber` diz **de quem veio** — sem conexão, essa é a única forma
de saber.

## Portas

`esperar_porta` substitui o *"sobe o serviço e dorme dois segundos torcendo
para dar tempo"* de todo script de integração. Quando ela desiste, diz o que
costuma ser:

```
api:8080 não abriu em 30s.
  O serviço não subiu, subiu em outra porta, ou subiu em
  127.0.0.1 quando deveria ser 0.0.0.0.
```

**Armadilha:** `porta_aberta` abre uma conexão de verdade — não há como
perguntar sem bater na porta. Um servidor que conta conexões vai ver esta
também.

## O erro diz o que significa

```
conectar (127.0.0.1:63859): a conexao foi RECUSADA.
  Ha alguem escutando nessa porta? Recusa e resposta: o
  host esta de pe e nada atende ali.
```

Recusa e prazo esgotado são coisas **diferentes**: a primeira significa que o
host respondeu; a segunda, que ninguém respondeu. Confundi-las manda a pessoa
procurar no lugar errado.

## Saída esperada

```
FORJA
de 127.0.0.1: pedidos=42
conexao em porta vazia: RECUSADA
236 ok
```

## Para experimentar

- Troque `receber_exato` por `receber` e mande os 5 000 caracteres. Veja a
  mensagem chegar pela metade.
- Suba o servidor em `127.0.0.1` e tente conectar do IP da máquina.
- Mande um datagrama para uma porta onde ninguém escuta. UDP não reclama.
