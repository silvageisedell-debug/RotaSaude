# ADR 004 — O cadastro do usuário final é um ModelForm, não o admin

## Contexto

O admin já cadastra veículos. Sem uma página nossa, a organização parceira não usa o protótipo — só a equipe entra nos fundos. O laboratório (issue #5) pede a “porta da frente”: GET mostra o form vazio, POST valida e grava.

## Decisão

O cadastro do usuário final é um **ModelForm** (`VeiculoForm` em `Veiculo/forms.py`) com view própria `novo_veiculo`:

- GET/POST na mesma view (`VeiculoForm(request.POST or None)`)
- `form.is_valid()` + `form.save()` + `redirect("lista_veiculos")`
- URL `/Veiculo/nova/` (`name="novo_veiculo"`)
- Template com `method="post"` e `{% csrf_token %}`

A regra de capacidade **não** é reescrita no form: ela vem do model (ADR 003).

## Alternativa descartada

Dar login de admin para o usuário final.

O admin expõe Marca, Modelo, Veículo e o restante do sistema, e não tem a cara do RotaSaúde. Um `ModelForm` é a porta do cliente; o admin continua sendo ferramenta interna.

## Consequência

Quem abre `/Veiculo/nova/` cadastra sem `/admin/`. Capacidade 0, 1 ou 6 é recusada com a mensagem do model. Ainda não há editar nem apagar (semente das próximas aulas). Marca e Modelo seguem no admin.

## Desafios

Sem pelo menos um `Modelo` no banco o select vem vazio. CSRF ausente vira 403. Validação HTML5 (`min`/`max`) pode impedir o teste da regra — o form usa `novalidate` para o POST chegar no Django.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
