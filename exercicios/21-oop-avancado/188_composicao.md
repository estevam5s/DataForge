# Exercicio 188 — Composição no lugar de herança

## Enunciado

Monte comportamento juntando objetos, em vez de estender uma hierarquia.

## Conceitos

A regra prática que decide:

- **Herança** quando A *é* um B — um Artigo é um Documento.
- **Composição** quando A *tem* um B — um Carro tem um Motor.

```dataforge
blueprint Carro:
    action setup(modelo, motor):
        self.motor := motor          // TEM um motor

    action dar_partida():
        yield self.motor.ligar()
```

Herança amarra o filho ao pai para sempre. Composição permite **trocar a peça**:

```dataforge
carro.motor := spawn MotorCombustao(100)   // mesmo carro, outro motor
```

Com herança, isso exigiria outro tipo.

## O que observar

**O trait define o encaixe.** `Motor` diz o que qualquer motor precisa saber
fazer; o carro depende do contrato, não da implementação.

**Testar fica mais simples.** Para testar o carro, passe um motor de mentira —
não é preciso montar a hierarquia inteira.

## Armadilhas

- Composição custa uma indireção: `self.motor.ligar()` em vez de `self.ligar()`.
  Para uma relação que realmente é "é um", herança é mais direta.
- Um objeto que compõe cinco outros e só repassa chamadas provavelmente devia ser
  cinco objetos separados.

## Relacionados

- [186 — Abstratos e traits](186_abstratos_e_traits.md)
- [190 — Polimorfismo](190_polimorfismo.md)
