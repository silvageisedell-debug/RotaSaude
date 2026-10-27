# ADR 017 — Disponibilidade do veículo

## Contexto

A frota já se cadastra pela porta da frente (`Marca`, `Modelo`, `Veiculo`). O operador ainda não registra quando um veículo está disponível nem quantas vagas há naquele horário. O protótipo visual dessa tela é a issue #20. Esta entrega persiste o registro e valida de fato, no app novo `Rota`.

O Taiga separa as responsabilidades: o template só exibe campos e mensagens, o navegador só exige o preenchimento (`required`) e a view faz a validação oficial. A ADR 002 continua valendo: o veículo entra por chave estrangeira, nunca por placa digitada. A regra antiga de capacidade fixa no model `Veiculo` não se aplica a esta tela. Data e horário desta história moram na view.

## Decisão

Nasce o app `Rota`, incluído em `INSTALLED_APPS`, com `path("", include("Rota.urls"))` ao lado do include de `Veiculo`.

O model `Disponibilidade` guarda:

- `veiculo`: `ForeignKey` para `Veiculo`, `on_delete=PROTECT`, `related_name="disponibilidades"`
- `data`: `DateField`
- `horario`: `TimeField`
- `vagas`: `PositiveIntegerField`

`PROTECT` impede apagar um veículo que já tenha disponibilidade. A migration desta entrega cria só esse model.

A view `nova_disponibilidade` atende `/disponibilidade/nova/`. No GET carrega `Veiculo.objects.all()` e o formulário vazio. No POST lê veículo, data, horário e vagas. Horário ausente ou data anterior a hoje não grava: a view devolve o template com `erro` e os valores digitados. Caso válido grava e devolve `sucesso`, citando veículo, data, horário e vagas. Não há redirecionamento para `/admin/`.

O template `disponibilidade_nova.html` estende `Veiculo/base.html`. O veículo é um `<select>` dos já cadastrados. Data, horário e vagas usam `type="date"`, `type="time"` e `type="number"`, com `required` e sem `novalidate`. O template só imprime `{% if erro %}` e `{% if sucesso %}`. Não compara data e não decide regra. A navbar ganha o link Disponibilidade.

## Alternativa descartada

Repetir a regra só no HTML. O navegador segura campo vazio, mas uma data passada ainda chegaria ao servidor se a validação oficial não existisse.

Colocar “data não anterior a hoje” no `clean()` do model, como a capacidade antiga do veículo. A view desta história é a porta da frente pedida pelo Taiga. Quem gravar pelo admin ou pelo shell fica de fora dessa checagem, e isso fica explícito na consequência.

Um `CharField` de placa no lugar da chave estrangeira. Duplicaria a placa e furaria a ADR 002.

## Consequência

Admin e shell ainda não aplicam “data não anterior a hoje” sozinhos. Quem gravar por fora da view precisa conhecer essa limitação. O app `Rota` passa a ser o lugar das próximas issues (categoria, viagem, parada). Apagar um veículo com disponibilidade registrada o banco recusa.

O número de vagas não é limitado pela capacidade do veículo. Editar e apagar disponibilidade ficam fora desta entrega.

## Desafios

Sem veículo cadastrado o seletor não aparece: o template mostra o estado vazio e aponta o cadastro da frota. A ordem operacional continua Marca, Modelo, Veículo e só então disponibilidade. POST incompleto ou com veículo inexistente devolve erro e não grava, para não responder 500.

## Status

Substituído pela ADR 022 (disponibilidade calculada). Adotado originalmente na issue #21.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
