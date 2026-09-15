# ADR 004 — Polimorfismo (arquivo legado)

Este arquivo **não** é a ADR 004 do Caderno do RotaSaúde. Permanece no repositório só para quem ainda busca “004 polimorfismo”.

| O que você procura | Onde está |
|---|---|
| Cadastro pela porta da frente (`VeiculoForm`) | [ADR-004-cadastro-modelform.md](ADR-004-cadastro-modelform.md) — **004 vigente** |
| Polimorfismo de tipos de veículo | [ADR-006-polimorfismo.md](ADR-006-polimorfismo.md) |

A ADR 006 **não copia** este rascunho: ela **complementa** a ADR 004. As validações já feitas no 004 (um único `Veiculo`, capacidade 2–5 no model, `VeiculoForm` sem campo tipo) continuam valendo. O 006 só registra a hierarquia futura e a decisão de **não implementar** agora.

Não há subclasses `Ambulancia`, `Van` ou `CarroPasseio` no código. O model atual não usa `if/elif` por tipo — o rascunho antigo estava incorreto nesse ponto.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record.
