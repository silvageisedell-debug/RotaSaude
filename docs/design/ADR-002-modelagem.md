# ADR 002 — Modelagem: Marca, Modelo e Veiculo

## Contexto

A frota do RotaSaúde precisa persistir veículos com placa, ano, chassi, Renavam e capacidade. Um único `CharField` “modelo” misturaria marca e versão e impediria listar “todos os Corolla” ou trocar o nome da marca sem reescrever cada veículo.

## Decisão

Três models em `Veiculo/models.py`:

- `Marca` — nome único
- `Modelo` — nome + `ForeignKey` para `Marca`
- `Veiculo` — placa, `ForeignKey` para `Modelo` (`PROTECT`), ano, chassi, Renavam, capacidade

Migração `0001_initial` materializa o esquema. Cadastro de marca/modelo no Marco 1 fica no admin; o veículo passa a ter porta da frente depois (ADR 004).

## Alternativa descartada

Um model só, com `marca` e `modelo` como texto livre.

Parece mais rápido, mas duplica “Toyota” em todo registro, não dá para normalizar e quebra qualquer filtro por marca. A FK custa uma tela a mais no admin e evita lixo no banco.

## Consequência

Integridade referencial: apagar uma marca em uso some os modelos (`CASCADE`); apagar um modelo com veículo cadastrado o banco recusa (`PROTECT`). Quem cadastra veículo precisa de pelo menos um `Modelo` (ex.: Toyota Corolla).

## Desafios

Ordem de cadastro: Marca → Modelo → Veiculo. Sem isso o select do formulário fica vazio.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
