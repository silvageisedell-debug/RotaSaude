# ADR 018 — Categorias de rota com prioridade

## Contexto

A disponibilidade do veículo já existe no app `Rota` (ADR 017). O operador ainda não distingue viagem urgente de eletiva. O catálogo é pequeno e estável: cada categoria tem um nome e um número de prioridade. Prioridade 1 é a mais urgente. Esse número é dado de negócio gravado no registro, não a ordem alfabética do nome.

No RotaSaúde, catálogo estável fica no admin, no mesmo espírito de `Marca` e `Modelo` (ADR 002). Nesta história a porta da frente do operador é o `/admin/`. Não há template novo na navbar.

O Taiga não nomeia a terceira categoria. O seed desta entrega fixa as três linhas: Urgente (1), Prioritária (2) e Eletiva (3).

## Decisão

O model `CategoriaRota` fica em `Rota/models.py`:

- `nome`: `CharField(max_length=50, unique=True)`
- `prioridade`: `PositiveIntegerField`
- `__str__` devolve o nome
- `Meta.verbose_name` = "Categoria de rota"
- `Meta.verbose_name_plural` = "Categorias de rota"
- `Meta.ordering` = `["prioridade", "nome"]`

`unique=True` no nome é a regra que recusa duplicata no admin, no shell e em qualquer outro form. A mesma checagem não é reimplementada na view.

O admin registra `CategoriaRota` com `list_display = ("nome", "prioridade")`. A ordenação da lista segue a `Meta` do model. Não há `ordering` próprio no `ModelAdmin`.

A data migration `0003_seed_categoria_rota` chama `semear_categorias`, em `Rota/seeds.py`, que usa `get_or_create` pelos três nomes. Rodar `migrate` de novo não duplica linha e não desfaz prioridade alterada no admin.

## Alternativa descartada

Um enum fixo no código. A equipe não cadastraria categoria nova sem alterar o fonte e gerar outra entrega.

Uma tela na porta da frente nesta história. O critério pede o admin, como marca e modelo. Abrir formulário em `/rotas/` agora misturaria o catálogo com a publicação da viagem, que é a issue seguinte.

## Consequência

A issue de publicar rota passa a ter um seletor de categorias reais, não texto livre. Apagar uma categoria usada por viagem fica para o `PROTECT` dessa issue seguinte. Duas categorias podem compartilhar a mesma prioridade: só o nome é único.

Não há tela nova fora do `/admin/`.

## Desafios

O seed usa `get_or_create`. Mudar a prioridade no admin não é desfeito por um `migrate` seguinte. O teste de duplicata precisa isolar o `IntegrityError` numa transação, senão o banco de teste fica inutilizado depois da falha.

## Status

Proposto até este PR entrar em `main` (issue #22).

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
