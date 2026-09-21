# 380 — o formulário que só envia uma vez

Sem formulário, **cada** campo reexecuta o programa. Num cadastro de
oito campos isso são oito execuções — e se um deles consulta o banco,
são oito consultas para preencher um cadastro.

## A economia acontece no NAVEGADOR

Ele segura os valores e manda tudo no envio. A sonda não vê isso — ela
simula um pedido por ação, e é uma das fronteiras dela.

## A validação fica JUNTO do campo

Com `role="alert"` e `aria-describedby` ligando ao campo — e não numa
caixa solta no topo da página.

## E um campo vazio e nunca tocado não é acusado

Reclamar antes de a pessoa digitar qualquer coisa é ruído, não
ajuda.
