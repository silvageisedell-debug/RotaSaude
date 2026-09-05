# ADR 003 — A regra de capacidade mora no model

## Contexto

A frota do RotaSaúde só admite 2 a 5 ocupantes. Sem validador, o admin (e o shell) gravam capacidade 0, 1 ou 6 — o laboratório pediu exatamente esse absurdo para mostrar o buraco. A issue #3 do GitHub chama isso de “ADR 002” no texto do hotel; no Caderno do RotaSaúde a validação é a **terceira** decisão (a segunda é a modelagem).

## Decisão

A regra fica no **model** `Veiculo.capacidade`:

- `MinValueValidator(2)` e `MaxValueValidator(5)` — o admin e o `ModelForm` reaproveitam
- `clean()` reforça o intervalo no `full_clean()`

Não reescrever a mesma regra na view nem só no HTML.

## Alternativa descartada

Validar só na tela (`min`/`max` no input) ou só na view.

Validação de tela não protege quem cria o registro pelo shell, pelo admin ou por outro form. A view duplicaria a regra e divergiria do model. O validador no campo é o encapsulamento de ILP: uma regra, vários clientes.

## Consequência

Admin e formulário próprio recusam capacidade fora de 2–5 com a mensagem do model. Qualquer porta nova herda a regra. Exige `makemigrations` quando o validador entra no estado persistido (já refletido em `0001_initial`).

## Desafios

`PositiveIntegerField` ainda renderiza `min="0"` no HTML; o form usa `novalidate` para o POST inválido chegar no Django e o Passo 6 do laboratório funcionar.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
