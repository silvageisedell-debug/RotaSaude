# ADR 004 — Onde polimorfismo caberia no RotaSaúde

## Contexto
No projeto **RotaSaúde**, temos vários tipos de veículos que fazem coisas semelhantes mas de formas diferentes.
Hoje temos: Ambulância, Van e Carro de passeio.
Cada tipo tem uma capacidade diferente (1 a 5 ocupantes), um tempo de resposta diferente e um custo operacional diferente.
Atualmente, o código usa `if/elif` para decidir qual tipo de veículo usar, o que não é escalável.

## Decisão
Aplicar polimorfismo criando uma classe base `Veiculo` e subclasses para cada tipo (Ambulancia, Van, CarroPasseio).
Cada subclasse implementa seus próprios métodos: `capacidade_maxima()`, `tempo_resposta()`, `custo_operacional()`.
Uma função genérica trata todos os tipos de veículo igual, sem precisar de `if/elif`.

## Alternativa descartada
Manter o `if/elif` atual no código.
Funciona agora, mas cada novo tipo de veículo obriga a mexer na função e arrisca quebrar os tipos existentes.
Não é escalável quando o projeto cresce.

## Consequência
Adicionar um novo tipo de veículo passa a não exigir mexer no código que já existe.
O código fica mais limpo, mais fácil de testar e mais fácil de manter.
Cada tipo de veículo fica isolado em sua própria classe.

## Status
Proposto — ainda não implementado. Só registrando a decisão de design.
