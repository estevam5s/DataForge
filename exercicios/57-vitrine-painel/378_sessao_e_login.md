# 378 — quem está vendo o painel

`exigir_login` **para** a página. Ela levanta um sinal que deriva de
`BaseException`, como `halt` e `skip`.

## Sem isso, viraria uma mensagem no meio da tela

O interpretador embrulha toda `Exception` que sai de função Python num
`RuntimeError_` — e a página continuaria desenhando o que o visitante
não pode ver.

## Entrar reexecuta a página do COMEÇO

Continuar de onde parou deixaria a tela vazia para quem escreveu
`given V.autenticado(): …`.

## E o cookie de sessão é uma STRING

O Kiln guarda cookie como a linha `Set-Cookie` pronta. Passar um vault
faz o navegador **descartar** o cookie, e cada pedido abre sessão nova —
o sintoma é um contador que nunca passa de 1, sem nenhum erro. E
`V.testar` não devolve cookies: esse bug só aparece com socket.
