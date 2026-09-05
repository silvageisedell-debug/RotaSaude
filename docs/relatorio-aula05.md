# Relatório — Aula 05 e UI Bootstrap

**Projeto:** RotaSaúde  
**Disciplina:** ISW-030 Web III  
**Data do trabalho:** 31/08/2026  
**Escopo:** cadastro pela porta da frente (`ModelForm`) + visual Bootstrap nas páginas de veículo

Este relatório registra o que foi feito, o que passou, o que falhou e as correções aplicadas. Só entra o que foi confirmado no código, no `manage.py check`, no `VeiculoForm` ou por HTTP contra `127.0.0.1:8000`.

---

## 1. O que foi feito

### 1.1 Laboratório — Aula 05 (ModelForm)

Adaptado o exemplo `Reserva` do roteiro para o tema **Veículo**.

| Artefato | Caminho / nome |
|---|---|
| ModelForm | `Veiculo/forms.py` → `VeiculoForm` |
| View GET+POST | `Veiculo/views.py` → `novo_veiculo` |
| Lista (Aula 04) | `lista_veiculos` (mantida) |
| URLs | `/Veiculo/` (`lista_veiculos`) e `/Veiculo/nova/` (`novo_veiculo`) |
| Template do form | `Veiculo/templates/Veiculo/nova.html` |
| Template da lista | `Veiculo/templates/Veiculo/lista.html` |
| ADR 004 (homework) | `docs/design/ADR-004-cadastro-modelform.md` |

Campos do form (os que o usuário preenche): `placa`, `modelo`, `ano`, `chassi`, `renavam`, `capacidade`.

A view segue o padrão do roteiro: `VeiculoForm(request.POST or None)` → `is_valid()` → `save()` → `redirect("lista_veiculos")`.

Regra de ILP reaproveitada do model: capacidade entre 2 e 5 (`MinValueValidator` / `MaxValueValidator` + `clean()`).

### 1.2 UI Bootstrap (identidade RotaSaúde)

| Artefato | Função |
|---|---|
| `Veiculo/templates/Veiculo/base.html` | Navbar, footer, CDN Bootstrap 5.3 + Icons |
| `Veiculo/static/Veiculo/css/app.css` | Tokens teal/verde-saúde, card, tabela, empty state |
| `lista.html` | Extends `base`; tabela + empty state + “Novo veículo” |
| `nova.html` | Card central; POST + CSRF; campos um a um; erros visíveis |
| `VeiculoForm.__init__` | Classes `form-control` / `form-select` e `is-invalid` |

Views, URLs e validação do model **não** mudaram nesse passo.

Navegação (opcional do homework): lista → cadastro e cadastro → lista.

### 1.3 Dados usados na validação

Pré-existentes no SQLite:

- Marca `Toyota`, Modelo `Corolla` (cadastro via admin — FK necessária no form)
- Veículo `ABC1232` (ano 1999, capacidade 5)

Criado **pela porta da frente** (POST em `/Veiculo/nova/`):

- Placa `GHI8901`, modelo Corolla, ano 2022, capacidade 4

Tentativa inválida (não gravou):

- Placa `TST0001`, capacidade `1`

---

## 2. Sucessos

| # | Verificação | Resultado |
|---|---|---|
| 1 | `python manage.py check` | 0 issues |
| 2 | `GET /Veiculo/` | HTTP 200; lista renderiza; `ABC1232` aparece |
| 3 | `GET /Veiculo/nova/` | HTTP 200; CSRF presente; `method="post"`; campos com classes Bootstrap |
| 4 | CSS estático | `GET /static/Veiculo/css/app.css` → 200 |
| 5 | Form válido (`capacidade=4`) | `VeiculoForm.is_valid() == True` |
| 6 | Form capacidade `0`, `1` ou `6` | `is_valid() == False`; mensagens do **model** (“mínima é 2” / “máxima é 5”) |
| 7 | Placa duplicada `ABC1232` | Recusa unicidade |
| 8 | POST HTTP capacidade `1` | 200 (não redireciona); `is-invalid` + *“A capacidade mínima é de 2 pessoas.”*; `TST0001` **não** existe no banco |
| 9 | POST HTTP válido `GHI8901` | 302 → `/Veiculo/`; registro na lista e no banco (total 2) |
| 10 | Views via `RequestFactory` | `lista_veiculos` e `novo_veiculo` retornam 200 |

O encapsulamento do roteiro (Passo 6) ficou comprovado: a recusa veio do validador do model, sem regra nova no `forms.py`.

---

## 3. Erros, falhas e correções

### 3.1 `DisallowedHost: testserver`

- **Quando:** primeiro teste com `django.test.Client` no `manage.py shell`
- **Causa:** `ALLOWED_HOSTS = []` (DEBUG) aceita `localhost` / `127.0.0.1`, não o host `testserver` do Client
- **Efeito:** todos os GET/POST do Client voltaram 400 — falso negativo
- **Correção:** abandonar o Client nesse shell; validar o form direto (`VeiculoForm(...)`) e as views com `RequestFactory` + `override_settings`; o fluxo real foi testado em HTTP em `127.0.0.1:8000`
- **O que não foi feito:** alterar `ALLOWED_HOSTS` em produção/settings só para o teste

### 3.2 `runserver` não escutou (StatReloader)

- **Quando:** primeiro `runserver` na sessão
- **Sintoma:** log parou em `Watching for file changes with StatReloader`; `curl` em `127.0.0.1:8000` falhou (`Couldn't connect`)
- **Causa provável:** sandbox / WSL sem bind efetivo; processo depois abortado
- **Correção:** novo `runserver` com ambiente menos restrito
- **Efeito colateral:** tentativa seguinte deu `Error: That port is already in use` — outro processo (`pid 3136`) já estava em `127.0.0.1:8000` e **servia** as páginas novas. Uso desse servidor para o curl

### 3.3 Browser da IDE indisponível

- **Quando:** validação visual da UI (plano pedia desktop e ~375px)
- **Falha:** namespace `cursor-ide-browser` sem tools (`browser_navigate` / `browser_tabs` não encontrados)
- **Correção / substituto:** verificação por HTTP (HTML, CSS, POST válido/inválido)
- **Resíduo:** collapse da navbar em 375px **não** foi visto em viewport real

### 3.4 Validação HTML5 vs regra do model

- **Risco:** `NumberInput` com `min`/`max` pode impedir o browser de enviar capacidade `1` ou `6` — o Passo 6 do roteiro não rodaria
- **Correção:** `novalidate` no `<form>` de `nova.html`, para o POST chegar no Django e o erro do model aparecer em `invalid-feedback`
- **Observação:** o HTML renderizado de `ano` e `capacidade` ainda mostra `min="0"` (o `PositiveIntegerField` sobrepõe o `min` do widget). Com `novalidate`, isso **não** bloqueou o teste. A recusa de capacidade continua sendo do model

### 3.5 Contraste do menu no mobile

- **Risco:** `navbar-toggler` escuro sobre fundo teal
- **Correção:** classe `navbar-dark` em `base.html`

### 3.6 CSRF (prevenido, não ocorreu em produção do lab)

- O roteiro alerta `Forbidden (403)` sem `{% csrf_token %}`
- O token ficou **dentro** do `<form method="post">`
- Os POSTs com cookie + token do GET funcionaram (200 inválido / 302 válido)

---

## 4. Pendências (não são falha de código da aula)

| Item | Situação |
|---|---|
| Editar / apagar veículo | Fora do escopo (semente do roteiro: próximas aulas) |
| `Veiculo/tests.py` | Vazio — o roteiro não exige testes automatizados |
| Versionamento | Seguir `docs/roteiro-prs.md` (você commita; não usar `git add .`) |
| Numeração ADR-004 | Resolvida no Caderno: 004 = ModelForm; polimorfismo = ADR 006 |
| Print do homework | Cada aluno ainda precisa da captura da lista **depois** do save pelo form |
| Texto individual (3–5 linhas) | Homework item 2 — não é código |
| Hash nos ADRs | Placeholder até o commit de cada PR |
| Marca / Modelo | Só pelo admin; o form de veículo depende de ao menos um `Modelo` (já há Toyota/Corolla) |
| Viewport 375px | Não validado visualmente (ver 3.3) |

---

## 5. Como repetir a validação

```bash
python manage.py runserver
```

1. Abrir `http://127.0.0.1:8000/Veiculo/` — tabela + navbar + “Novo veículo”
2. Abrir `http://127.0.0.1:8000/Veiculo/nova/` — card com campos; **não** usar `/admin/`
3. Enviar capacidade `1` ou `6` — deve permanecer na página, mostrar erro vermelho, não gravar
4. Enviar dado válido (placa nova, Corolla, capacidade 2–5) — 302 para a lista com o registro novo

---

## 6. Arquivos tocados nesta linha de trabalho

```
Veiculo/forms.py
Veiculo/views.py
Veiculo/urls.py
Veiculo/templates/Veiculo/base.html          (novo)
Veiculo/templates/Veiculo/lista.html
Veiculo/templates/Veiculo/nova.html
Veiculo/static/Veiculo/css/app.css           (novo)
docs/design/ADR-004-cadastro-modelform.md
docs/relatorio-aula05.md                     (este arquivo)
```
