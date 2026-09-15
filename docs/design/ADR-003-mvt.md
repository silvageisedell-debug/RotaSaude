# ADR 003-MVT — Lista de veículos no padrão MVT, sem cadastro pelo admin

## Contexto

Depois do model e do admin, o dado só existia nos fundos (`/admin/`). A organização parceira precisa **ver** a frota numa página nossa. O exemplo da disciplina é `lista_reservas` + `reservas/lista.html`; no RotaSaúde o mesmo desenho usa `Veiculo`.

## Decisão

Separar as três peças do MVT:

- **Model** — `Veiculo` (já existia)
- **View** — `lista_veiculos` em `Veiculo/views.py` (`Veiculo.objects.all()`)
- **Template** — `Veiculo/templates/Veiculo/lista.html`
- **URL do app** — `/Veiculo/` (`name="lista_veiculos"`)
- **URL do projeto** — `path("", include("Veiculo.urls"))` em `Portal/urls.py`

Nesta etapa a página **só lia**. Gravar pela porta da frente é a ADR 004; editar e apagar são a ADR 007. A coluna Ações da lista é complemento posterior — a decisão desta ADR (MVT na porta da frente, sem mandar o usuário ao admin) permanece.

## Alternativa descartada

Mandar o usuário final para o admin para “ver a lista”.

O admin expõe Marca, Modelo, usuários e o resto do sistema. Não é a cara do produto e não ensina o MVT que a P3 cobra.

## Consequência

`GET /Veiculo/` mostra a frota ou “Nenhum veículo cadastrado ainda” — os dois são sucesso. Dois `urls.py` (app vs projeto) passam a ser o ponto frágil: confundir os dois quebra a rota.

## Desafios

O nome do app se repete em `templates/Veiculo/` de propósito (loader do Django). Template no lugar errado vira `TemplateDoesNotExist`.

## Status

Adotado (issue #4 / PR #10). Lista com coluna Ações: ver ADR 007.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

`a04e54a`
