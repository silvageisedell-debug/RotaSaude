# ADR 008 — Responsabilidade misturada em `VeiculoForm.__init__`

## Contexto

A issue #12 (Homework 06c, ILP-037) pede enxergar no RotaSaúde uma classe ou função com mais de um motivo para mudar — SRP — e registrar. Não é obrigatório separar agora.

O ponto observado é `VeiculoForm.__init__` em `Veiculo/forms.py` (ADR 004). A classe acumula duas responsabilidades:

1. **Contrato de cadastro/edição** — `ModelForm` ligado a `Veiculo`, campos `placa` / `modelo` / `ano` / `chassi` / `renavam` / `capacidade`. Quem muda o domínio (novo campo, widget de validação) mexe aqui.
2. **Aparência Bootstrap** — o mesmo `__init__` percorre os campos e aplica `form-control`, `form-select` e `is-invalid`. Quem troca o visual (CSS próprio, outro framework, tema) também mexe aqui.

Um segundo cheiro, menor, está nas views `novo_veiculo` e `editar_veiculo`: as duas orquestram HTTP, `is_valid()`, `save()` e `render`. No Django isso é o padrão MVT da disciplina; o form é o acúmulo mais claro porque mistura **domínio** com **apresentação**.

A regra de capacidade **não** está misturada no form: ela permanece no model (ADR 003).

## Decisão

**Registrar e não separar agora.** O CRUD da ADR 007 acabou de fechar; extrair um mixin de widgets, crispy-forms ou classes só no template atrasaria a Sprint sem mudar comportamento. Fica dívida de design para o Marco 2: o form continua sendo a porta da frente; a pintura Bootstrap sai dele quando houver motivo real (troca de UI ou segundo canal que não use Bootstrap).

## Alternativa descartada

Refatorar nesta issue “para o Caderno mostrar SRP resolvido”.

Sem segundo cliente do form (API, admin custom, outro tema), a extração seria teatro: mais arquivos, mesmo HTML. A banca do homework avalia o **olho** para o smell, não a refatoração prematura.

## Consequência

Ganho de deixar como está: o laboratório da Aula 05/06 continua reproduzível; um arquivo explica o form. Custo: `VeiculoForm` muda por dois motivos — campo novo **ou** classe CSS. Quando separarmos, o form volta a ter um motivo (contrato com o model) e a view/template passam a donos do visual.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record. A observação — o `__init__` do `VeiculoForm` mistura ModelForm e Bootstrap — é do projeto RotaSaúde.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
