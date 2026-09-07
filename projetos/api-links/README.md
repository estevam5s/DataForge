# api-links

Encurtador de URL com servidor HTTP.

```bash
dataforge install
dataforge run src/main.df

curl -X POST localhost:8080/encurtar -d '{"url":"https://exemplo.com/pagina"}'
# {"codigo": "xYAXp7", "url": "https://exemplo.com/pagina"}   201

curl localhost:8080/xYAXp7        # 200, com o destino
curl localhost:8080/naoexiste     # 404
curl localhost:8080/estatisticas  # os mais acessados
```

## Estrutura

| Arquivo | Responsabilidade |
|---------|------------------|
| `src/encurtador.df` | toda a regra de negócio, sem HTTP |
| `src/main.df` | rotas, códigos de status e log |

## Decisões

**Regra separada de transporte.** Testar HTTP é lento; com a lógica em
`encurtador.df`, os 11 testes rodam em milissegundos e não sobem servidor. O
`main.df` é uma casca de trinta linhas.

**Semente no gerador.** `E.novo(42)` produz sempre os mesmos códigos, o que torna
o teste reproduzível. Sem semente, usa o relógio.

**O código evita caracteres ambíguos.** O alfabeto não tem `l`, `I`, `0` nem `O`
— quem lê um código em voz alta ou copia de um papel não erra.

**400 para URL inválida, não 500.** Um erro do cliente não é falha do servidor, e
o status precisa dizer de quem é a responsabilidade.
