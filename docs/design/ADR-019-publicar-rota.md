# ADR 019 — Publicar rota

## Contexto

A disponibilidade do veículo (ADR 017) e as categorias de rota (ADR 018) já existem no app `Rota`. O operador ainda não materializa a viagem: origem e destino em cima de uma vaga, classificada por categoria. Sem as duas chaves estrangeiras, a rota seria texto solto e perderia o veículo e a prioridade quando a disponibilidade mudasse de dia.

O model no código se chama `Viagem`, para não colidir com o app `Rota`. Na interface o operador lê rota.

## Decisão

O model `Viagem` fica em `Rota/models.py`:

- `disponibilidade`: `ForeignKey` para `Disponibilidade`, `on_delete=PROTECT`, `related_name="viagens"`
- `categoria`: `ForeignKey` para `CategoriaRota`, `on_delete=PROTECT`, `related_name="viagens"`
- `origem`: `CharField(max_length=120)`
- `destino`: `CharField(max_length=120)`
- `__str__` devolve origem, destino e categoria

`PROTECT` nas duas FKs: não se apaga disponibilidade nem categoria que já sustente uma viagem. Veículo, disponibilidade e categoria não são texto livre. Origem e destino são texto porque não há catálogo de locais.

A view `nova_rota` atende `/rotas/nova/`. No POST exige disponibilidade, categoria, origem e destino. Campo ausente ou chave inexistente não grava: a view devolve `erro` e os valores digitados. Caso válido grava e devolve `sucesso`. O template só imprime as mensagens e marca os campos com `required`.

A view `lista_rotas` atende `/rotas/` e mostra origem, destino, veículo (via disponibilidade), data, horário e categoria. Sem registro, o template usa `rs-empty`. A navbar ganha o link Rotas.

Não há model `Parada` nesta entrega. A tela fica pronta para o itinerário acrescentar as paradas no mesmo formulário.

## Alternativa descartada

Repetir placa, data e categoria como `CharField` na viagem. Isso duplicaria dado e quebraria o vínculo quando a disponibilidade mudasse de dia.

## Consequência

Publicar rota exige ao menos uma disponibilidade e as categorias do seed. A issue do itinerário entra nesta mesma tela. Apagar disponibilidade ou categoria em uso o banco recusa. Mais de uma viagem por disponibilidade continua possível: não há `unique` nesta entrega. Editar e apagar rota ficam fora, exceto o que a issue do itinerário pedir na tela de editar.

## Desafios

O select de disponibilidade fica vazio enquanto ninguém registrar vaga. A interface diz rota e o model diz `Viagem`. O tamanho 120 de origem e destino não veio no card; cabe um nome de local sem abrir catálogo.

## Status

Adotado nesta entrega (issue #23).

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

8ccd786
