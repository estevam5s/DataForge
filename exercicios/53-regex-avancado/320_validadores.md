# 320 — o que eles NÃO conferem

`is_cpf` confere o **formato**, e não o dígito verificador. Um
validador de forma aceita `111.111.111-11`, que não é um CPF — e o
cadastro descobre isso na primeira nota fiscal.

## Os dois juntos

Formato e dígito verificador respondem coisas diferentes, e a
mensagem de erro precisa dizer qual das duas falhou.

## E os padrões prontos

E-mail, cor hexadecimal, slug, CEP — o catálogo existe para não haver
cinco versões do mesmo padrão espalhadas pelo projeto.
