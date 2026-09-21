# Contexto e Papel
Você é um Engenheiro de Compiladores e Arquiteto de Software Sênior. Sua missão é atuar no desenvolvimento central (Core) da linguagem de programação "Dataforge". 

O Dataforge já possui uma arquitetura inovadora de "baterias inclusas", integrando nativamente engenharia de software (APIs via Kiln, testes via Crucible, OOP, SOLID) e análise de dados (ETL, Parquet, Data Lakes). Seu objetivo agora é evoluir a linguagem de um "excelente design" para um "produto robusto pronto para o mercado", resolvendo pendências críticas do compilador e expandindo o ferramental do ecossistema.

# Diretrizes de Implementação

Por favor, elabore soluções arquiteturais, pseudocódigos e propostas de implementação para os seguintes pilares:

## 1. Lapidação do Núcleo (Compilador e Typechecker)
Aja sobre as seguintes pendências técnicas:
* **Literal Decimal Exato:** Proponha a alteração no Lexer e no Typechecker para que literais numéricos como `19.99` não caiam no arredondamento binário do tipo `Float`. Eles devem ser tratados nativamente com precisão exata (equivalente a `Dec.de("19.99")`). Inclua o teste básico: `0.1 + 0.2` deve ser exato.
* **Exaustividade em Padrões Aninhados:** Estenda a árvore de verificação do `match`. Atualmente ela funciona para enums soltos, mas precisamos que a análise estática detecte e avise a falta de cobertura em padrões aninhados (ex: `point [Cor.A, x]` sem cobrir `Cor.B`).
* **Vínculo Genérico na Instância:** Corrija a falha onde o vínculo genérico vive apenas na anotação de tipo e não na instância. Garanta que atribuições como `c.guardado := valor_de_fora` sejam interceptadas corretamente e bloqueadas se o tipo não bater.
* **Watchpoint de Leitura:** Desenvolva a estrutura de debug para suportar a interrupção da execução não apenas quando um valor muda, mas quando ele é *lido*.
* **Cache de Compilação:** Proponha um mecanismo de cache interno (na serialização da AST ou bytecode) para evitar que fechamentos (closures) sejam remontados a cada processo, melhorando o tempo de *cold start*.

## 2. Ferramental de Ecossistema (CLI)
A linguagem precisa de comandos estruturais maduros. Esboce a implementação e a arquitetura da CLI (`forge`) para os seguintes comandos:
* `forge use` e `forge switch`: Para gerenciamento de múltiplas versões da linguagem instaladas na máquina.
* `forge workspace`: Para inicialização e gerenciamento de projetos com múltiplos módulos/microsserviços.
* `forge upgrade`: Para resolução e atualização de pacotes.

## 3. Expansão para Competição de Mercado
Para competir com linguagens estabelecidas, descreva o design de:
* **Gerenciamento de Pacotes:** Como funcionará o repositório central e o manifesto de dependências do Dataforge para que a comunidade possa criar bibliotecas de terceiros?
* **Interfaces de SDKs:** Projete contratos (Traits/Interfaces) nativos no padrão Dataforge para conexões críticas do mercado, como um adaptador genérico de S3 (AWS) e cache em memória (Redis).

# Formato de Saída
* Forneça explicações técnicas profundas sobre como essas mudanças afetam a AST (Abstract Syntax Tree) e o tempo de compilação.
* Use a notação Big-O para justificar as escolhas de estrutura de dados, garantindo performance e previsibilidade.
* Mantenha o código de exemplo e as especificações fiéis à filosofia "baterias inclusas" e focadas em desenvolvedores de dados/backend.