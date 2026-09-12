# RotaSaúde

Protótipo acadêmico (ISW-030 Web III / ILP — FATEC Olímpia) de **frota de transporte assistencial**. A organização parceira cadastra e lista veículos pela porta da frente, sem usar o Django Admin.

**Repositório:** [silvageisedell-debug/RotaSaude](https://github.com/silvageisedell-debug/RotaSaude)

## Engenheiro de projeto

| Papel | Identidade |
|---|---|
| Scrum Master | **silvageisedell** |
| Dev | **fjunior** |
| QA | **kaique029** |
| Interlocutor | **ignisolus** |
| Ambiente | WSL2 + Ubuntu, Python 3, Django 5.2 |

Commits e PRs deste Caderno devem ir com o autor acima — não com o Cursor.

## Arquitetura (MVT)

```
Portal/          projeto Django (settings, urls raiz, WSGI/ASGI)
  settings.py    INSTALLED_APPS inclui Veiculo
  urls.py        admin/ + include("Veiculo.urls")

Veiculo/         app de domínio
  models.py      Marca, Modelo, Veiculo (capacidade 2–5)
  admin.py       cadastro interno de marca/modelo/veículo
  forms.py       VeiculoForm (ModelForm) — porta da frente
  views.py       lista_veiculos, novo_veiculo
  urls.py        /Veiculo/ e /Veiculo/nova/
  templates/Veiculo/   base.html, lista.html, nova.html
  static/Veiculo/css/app.css
  migrations/    0001_initial

docs/design/     Caderno de Design (ADRs do Marco 1)
docs/roteiro-prs.md
```

Fluxo de cadastro:

1. GET `/Veiculo/nova/` — formulário vazio (CSRF)
2. POST — `VeiculoForm` valida com as regras do **model**
3. Válido → `save()` e redirect para `/Veiculo/`
4. Inválido (ex.: capacidade 1 ou 6) → mesma página, erro no campo, sem gravar

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

## Caderno de Design

| ADR | Decisão |
|---|---|
| 001 | WSL2 + venv + Django |
| 002 | Models Marca / Modelo / Veiculo |
| 003 | Validação de capacidade no model |
| 003-MVT | Lista no padrão MVT |
| 004 | Cadastro por ModelForm, não pelo admin |
| 005 | Strategy **não** no Marco 1 |
| 006 | Polimorfismo de tipos — só registrado |

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
