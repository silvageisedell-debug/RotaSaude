# Relatório — Aula 06: fechar o CRUD (editar e apagar)

**Projeto:** RotaSaúde  
**Disciplina:** ISW-030 Web III  
**Issue:** [#13](https://github.com/silvageisedell-debug/RotaSaude/issues/13) — Fechar o CRUD: editar e apagar  
**Data da validação:** 15/09/2026  
**Escopo:** `editar_veiculo` e `apagar_veiculo` no domínio **Veículo** (adaptação do roteiro Usuario/Paciente)

Este relatório registra o que foi conferido no código e no Django (`RequestFactory` + `Client` com `override_settings`). Só entra o que passou ou falhou de fato. Textos do Caderno desta linha foram redigidos com apoio de IA, em tom formal e informativo.

---

## 1. O que foi feito

Adaptado o laboratório da Aula 06 para `Veiculo` / `VeiculoForm` (ADR 004). ADR desta aula: [ADR-007-crud-editar-apagar.md](design/ADR-007-crud-editar-apagar.md).

| Artefato | Caminho / nome |
|---|---|
| View edição | `Veiculo/views.py` → `editar_veiculo` (`instance=veiculo`) |
| View exclusão | `apagar_veiculo` (GET confirma; POST `delete()`) |
| URLs | `/Veiculo/<int:pk>/editar/` e `/Veiculo/<int:pk>/apagar/` |
| Template confirmação | `Veiculo/templates/Veiculo/confirmar_apagar.html` |
| Lista | coluna Ações em `lista.html` |
| Form | `nova.html` reusado; título conforme `form.instance.pk` |

Banco no momento da validação: Marca `Toyota`, Modelo `Corolla`. A listagem de veículos estava **vazia** (os registros da Aula 05 não estavam mais no SQLite). Foi criado o veículo de prova `TST13A1` (capacidade 4), editado e em seguida apagado — o banco voltou vazio, que é empty state válido.

---

## 2. Sucessos

| # | Verificação | Resultado |
|---|---|---|
| 1 | `python manage.py check` | 0 issues |
| 2 | `GET /Veiculo/` | HTTP 200; HTML contém links `editar` e `apagar` |
| 3 | `GET /Veiculo/<pk>/editar/` | HTTP 200; placa `TST13A1` no form; capacidade 4 preenchida |
| 4 | `POST` edição (`ano=2021`, `capacidade=3`) | 302 → `/Veiculo/`; registro atualizado (não duplicado) |
| 5 | `GET /Veiculo/<pk>/apagar/` | HTTP 200; CSRF no form; placa visível; registro **ainda existe** |
| 6 | `POST /Veiculo/<pk>/apagar/` | 302 → `/Veiculo/`; registro deixou de existir |
| 7 | `GET /Veiculo/99999/editar/` | 404 (`get_object_or_404` / `Http404`) |
| 8 | `GET /Veiculo/99999/apagar/` | 404 |
| 9 | `Client` GET lista | 200 (`ALLOWED_HOSTS` de teste) |
| 10 | `Client` 404 editar e apagar | 404 em ambos |

**11/11.** Régua da issue (caminho feliz + caminho de erro) coberta no domínio Veículo.

Por que o GET de apagar não exclui: `GET` só consulta; exclusão no GET permitiria apagar por um clique ou prefetch. A view só chama `delete()` no `POST`, depois da confirmação e do CSRF.

---

## 3. Erros, falhas e correções

Nenhum erro de código nesta validação. O `RequestFactory` **não** exercita o middleware CSRF; a presença do token foi conferida no HTML de `confirmar_apagar.html`. O `Client` da Aula 05 quebrava com `DisallowedHost: testserver` se `ALLOWED_HOSTS` ficasse vazio — aqui o Client rodou só com `override_settings`, sem alterar `settings.py`.

---

## 4. Relação com o Caderno

| ADR | Papel nesta aula |
|---|---|
| 003 | Capacidade 2–5 continua no model; o POST de editar herda a regra |
| 004 | `VeiculoForm` reusado; esta aula **não** substitui o cadastro |
| 005 / 006 | Sem Strategy e sem subclasses; o CRUD não introduz tipo |
| 007 | Decisão nova: editar com `instance=` e apagar só no POST |

---

## 5. Como repetir

```bash
source .venv/bin/activate
python manage.py check
python manage.py runserver
```

1. Abrir `http://127.0.0.1:8000/Veiculo/` — tabela ou empty state; se houver linha, links editar/apagar
2. Editar: form preenchido; salvar; voltar à lista com o valor novo
3. Apagar: tela de confirmação **não** remove; confirmar no POST remove
4. Abrir `/Veiculo/99999/editar/` e `/Veiculo/99999/apagar/` — 404, não 500

---

## 6. Arquivos desta linha

```
Veiculo/views.py
Veiculo/urls.py
Veiculo/templates/Veiculo/base.html
Veiculo/templates/Veiculo/lista.html
Veiculo/templates/Veiculo/nova.html
Veiculo/templates/Veiculo/confirmar_apagar.html
docs/design/ADR-007-crud-editar-apagar.md
docs/relatorio-aula06.md
```

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo boas práticas de relatório técnico (o que foi feito, o que passou, o que falhou, como repetir).
