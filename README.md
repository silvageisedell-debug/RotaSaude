# RotaSaúde

Protótipo acadêmico (ISW-030 Web III / ILP — FATEC Olímpia) de **frota de transporte assistencial**. A organização parceira lista, cadastra, edita e apaga veículos pela porta da frente, sem usar o Django Admin.

**Repositório:** [silvageisedell-debug/RotaSaude](https://github.com/silvageisedell-debug/RotaSaude)

## Engenheiro de projeto

| Papel | Identidade |
|---|---|
| Engenheiro de projeto | **fjunior** |
| E-mail (Git) | frf.junior17@outlook.com |
| Ambiente | WSL2 + Ubuntu, Python 3, Django 5.2 |

Commits e PRs deste Caderno devem ir com o autor acima — não com o Cursor.

## Como este Caderno foi escrito

Os textos em `docs/` (ADRs e relatórios) foram redigidos com **apoio de IA**, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record: contexto, decisão, alternativa descartada e consequência. A observação de domínio (Veículo, não o exemplo Reserva/Usuario do roteiro) é da equipe.

Os templates HTML usam **Bootstrap 5** aplicado com apoio de IA (utilitários, navbar, formulários e confirmação). O crédito está em comentário de fonte nos `.html`, para não poluir a interface.

## Arquitetura (MVT)

```
Portal/          projeto Django (settings, urls raiz, WSGI/ASGI)
  settings.py    INSTALLED_APPS inclui Veiculo
  urls.py        admin/ + include("Veiculo.urls")

Veiculo/         app de domínio
  models.py      Marca, Modelo, Veiculo (capacidade 2–5)
  admin.py       cadastro interno de marca/modelo/veículo
  forms.py       VeiculoForm (ModelForm) — porta da frente
  views.py       lista_veiculos, novo_veiculo, editar_veiculo, apagar_veiculo
  urls.py        /Veiculo/, /nova/, /<pk>/editar/, /<pk>/apagar/
  templates/Veiculo/   base.html, lista.html, nova.html, confirmar_apagar.html
  static/Veiculo/css/app.css
  migrations/    0001_initial

docs/design/     Caderno de Design (ADRs)
docs/roteiro-prs.md
docs/relatorio-aula05.md
docs/relatorio-aula06.md
```

Fluxo de cadastro (ADR 004):

1. GET `/Veiculo/nova/` — formulário vazio (CSRF)
2. POST — `VeiculoForm` valida com as regras do **model**
3. Válido → `save()` e redirect para `/Veiculo/`
4. Inválido (ex.: capacidade 1 ou 6) → mesma página, erro no campo, sem gravar

Fluxo de edição e exclusão (ADR 007 / issue #13):

1. GET `/Veiculo/<pk>/editar/` — mesmo form, preenchido (`instance=`)
2. POST válido — grava o **mesmo** registro e volta à lista
3. GET `/Veiculo/<pk>/apagar/` — confirmação; **não** apaga
4. POST com CSRF — `delete()` e redirect; pk inexistente → 404

## Regras de negócio (Marco 1)

- Capacidade do veículo: **2 a 5** ocupantes (`MinValueValidator` / `MaxValueValidator` + `clean()`)
- Placa, chassi e Renavam únicos
- `Modelo` pertence a `Marca`; `Veiculo` referencia `Modelo` com `PROTECT`
- Marca e Modelo, neste marco, só pelo admin

## Rotas

| URL | Nome | Função |
|---|---|---|
| `/admin/` | — | fundos (equipe) |
| `/Veiculo/` | `lista_veiculos` | lista da frota |
| `/Veiculo/nova/` | `novo_veiculo` | cadastro (ModelForm) |
| `/Veiculo/<pk>/editar/` | `editar_veiculo` | edição (mesmo ModelForm) |
| `/Veiculo/<pk>/apagar/` | `apagar_veiculo` | confirmação GET; exclusão no POST |

## Caderno de Design

| ADR | Decisão |
|---|---|
| 001 | WSL2 + venv + Django |
| 002 | Models Marca / Modelo / Veiculo |
| 003 | Validação de capacidade no model |
| 003-MVT | Lista no padrão MVT |
| 004 | Cadastro por ModelForm, não pelo admin |
| 005 | Strategy **não** no Marco 1 |
| 006 | Polimorfismo de tipos — só registrado (complementa o 004) |
| 007 | Editar e apagar pela porta da frente |

O arquivo `docs/design/ADR-004-polimorfismo.md` é um **ponteiro legado**. A ADR 004 vigente é o ModelForm; polimorfismo está na 006.

## Como rodar

```bash
cd ~/RotaSaude          # ou o clone local
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/Veiculo/`. Se o form de veículo vier sem modelos, cadastrar Marca e Modelo em `/admin/` antes.

## Commits e PRs

O passo a passo para você executar (sem o Cursor commitar) está em [docs/roteiro-prs.md](docs/roteiro-prs.md).
