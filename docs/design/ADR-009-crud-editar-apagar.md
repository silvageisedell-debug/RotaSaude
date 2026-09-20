# ADR 007 — Editar e apagar veículo pela porta da frente

## Contexto

A ADR 004 entregou o cadastro (`VeiculoForm` + `novo_veiculo`). A lista (ADR 003-MVT) só lia. A issue #13 / Aula 06 pede fechar o CRUD: a atendente corrige um veículo existente e remove com confirmação, sem `/admin/`, no domínio **Veículo** (não o exemplo Usuario/Paciente do roteiro).

A regra de capacidade continua no model (ADR 003). Polimorfismo de tipos continua só registrado (ADR 006).

## Decisão

Reusar o mesmo `VeiculoForm` da ADR 004 e duas views novas:

- **Editar** — `editar_veiculo(request, pk)`: `get_object_or_404(Veiculo, pk=pk)` e `VeiculoForm(request.POST or None, instance=veiculo)`. GET mostra o form preenchido; POST válido `save()` e `redirect("lista_veiculos")`. Mesmo template `nova.html` (`form.instance.pk` troca o título).
- **Apagar** — `apagar_veiculo(request, pk)`: GET só renderiza `confirmar_apagar.html` (placa e modelo); `delete()` **somente** no POST, com `{% csrf_token %}`.
- **URLs** — `/Veiculo/<int:pk>/editar/` e `/Veiculo/<int:pk>/apagar/`.
- **Lista** — coluna Ações com `{% url 'editar_veiculo' r.pk %}` e `{% url 'apagar_veiculo' r.pk %}`.

Pk inexistente → 404 controlado, não 500.

## Alternativa descartada

- `Veiculo.objects.get(pk=pk)` — pk inválido vira 500.
- Apagar no GET — um link ou prefetch apagaria sem confirmação.
- Form separado de edição — duplicaria o contrato do ModelForm da ADR 004.
- Exclusão pelo admin — fura a porta da frente que o laboratório cobra.

## Consequência

O CRUD da frota fecha na interface própria. CSRF e validação do model (2–5) valem também na edição. Custo: mais duas rotas e um template de confirmação; ganho: a atendente não vai aos fundos para corrigir ou remover.

## Desafios

Sem `instance=` o POST de edição cria outro registro. Sem `pk` no `{% url %}` aparece `NoReverseMatch`. Sem CSRF no form de apagar, 403. A lista vazia continua sucesso (empty state da ADR 003-MVT).

## Validação (issue #13)

Registrada em [docs/relatorio-aula06.md](../relatorio-aula06.md): `manage.py check`; GET lista com links; GET editar preenchido; POST editar 302 e dado atualizado; GET apagar não exclui; POST apagar exclui; pk `99999` → 404.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record. A adaptação Usuario/Paciente → `Veiculo` é do projeto RotaSaúde.

## Commit

`b9b6a1b`
