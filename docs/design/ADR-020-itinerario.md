# ADR 020 — Itinerário ordenado

## Contexto

A viagem já tem origem e destino (ADR 019). Falta descrever o caminho: as paradas no meio, na sequência em que o veículo passa. Origem e destino continuam sendo os extremos.

A ordem é um número informado na própria tela, não a posição em que a linha foi desenhada no HTML. Duas paradas da mesma viagem não podem dividir o mesmo número.

## Decisão

O model `Parada` fica em `Rota/models.py`:

- `viagem`: `ForeignKey` para `Viagem`, `on_delete=CASCADE`, `related_name="paradas"`
- `ordem`: `PositiveIntegerField`
- `local`: `CharField(max_length=120)`
- `Meta.ordering` = `["ordem"]`
- `UniqueConstraint` em `(viagem, ordem)`

`CASCADE` porque a parada não existe sem a viagem. Isso é diferente do `PROTECT` de veículo, disponibilidade e categoria, que são cadastros reutilizados.

O formset de local e ordem entra na mesma tela de publicar (`/rotas/nova/`) e na tela de editar (`/rotas/<pk>/editar/`). A view grava a viagem e as paradas no mesmo POST, dentro de uma transação. Ordem repetida na mesma viagem não grava e devolve a mensagem da view. O template só renderiza as linhas e as mensagens: não reordena e não compara duplicata.

Linha em branco no formset vale como rota só com origem e destino. A lista mostra as paradas pela ordenação do model.

## Alternativa descartada

Um `CharField` único com o caminho inteiro, e também ordenar só pela posição visual sem número persistido. Os dois impedem consultar qual é a segunda parada e reeditar a sequência.

## Consequência

Apagar a viagem apaga as paradas. A unicidade é do par viagem e ordem, não da ordem no sistema inteiro. A lista segue o campo `ordem`, mesmo se o formulário tiver sido preenchido ao contrário.

## Desafios

Formset vazio continua sendo uma rota válida. A checagem do número repetido fica na view, para o template não embutir a regra. Trocar a ordem de paradas já salvas regrava o conjunto na mesma transação, para o banco não recusar um passo intermediário da troca.

## Status

Adotado nesta entrega (issue #24).

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

a72026b
