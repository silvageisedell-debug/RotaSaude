# Roteiro de commits e PRs (você executa)

Autor Git esperado: **fjunior** `<frf.junior17@outlook.com>`.  
Confira com `git config user.name` e `git config user.email` **antes** do primeiro commit.

O Cursor **não** deve rodar `git commit`, `git push` nem `gh pr create`.

**Nunca** use `git add .` — o `.venv` já foi versionado por engano no passado.

Base de todos os PRs: `main`  
Repo: `silvageisedell-debug/RotaSaude`

Depois de cada commit, se quiser rastrear o hash no ADR:

```bash
git rev-parse --short HEAD
# cole no campo Commit do ADR e faça um segundo commit só disso
```

---

## Antes de qualquer PR

```bash
cd /home/ffernandes/RotaSaude
git fetch origin
git checkout main
git pull origin main
```

Arquivos soltos no working tree **viajam** com você de branch em branch. Por isso cada bloco abaixo dá `git add` **só** no arquivo daquela issue.

Não commitar: `.venv/`, `__pycache__/`, `IMPRIMIR_*.md`, `docs/design/ADR-005 ModelForm-UI.md` (cópia antiga; o relatório certo é `docs/relatorio-aula05.md`).

---

## PR 1 — Issue #1 (ADR 001 ambiente)

```bash
git checkout main
git checkout -b docs/issue-1-ambiente
git add docs/design/ADR-001-ambiente.md
git status   # só esse arquivo staged
git commit -m "$(cat <<'EOF'
docs: ADR 001 registra WSL2 e Django como ambiente do RotaSaúde

Fecha a issue #1 com a decisão de ambiente reproduzível da equipe.
EOF
)"
git push -u origin HEAD
gh pr create --base main --title "ADR 001 — Ambiente WSL2 e Django" --body "$(cat <<'EOF'
## Summary
- ADR 001: WSL2 + Ubuntu + venv + Django; projeto `Portal`, app `Veiculo`
- Fecha o Caderno da aula 00 (o código do startproject já está em main)

## Test plan
- [ ] Arquivo visível em `docs/design/ADR-001-ambiente.md`
- [ ] Cinco seções preenchidas (alternativa descartada justifica)

Closes #1
EOF
)"
```

---

## PR 2 — Issue #2 (ADR 002 modelagem)

```bash
git checkout main
git checkout -b docs/issue-2-modelagem
git add docs/design/ADR-002-modelagem.md
git status
git commit -m "$(cat <<'EOF'
docs: ADR 002 justifica Marca, Modelo e Veiculo

Fecha a issue #2: modelagem normalizada em vez de texto livre.
EOF
)"
git push -u origin HEAD
gh pr create --base main --title "ADR 002 — Modelagem Marca, Modelo e Veiculo" --body "$(cat <<'EOF'
## Summary
- ADR 002: três models com FK (`PROTECT` no veículo)
- Código dos models já está em main; este PR só documenta a decisão

## Test plan
- [ ] ADR com alternativa descartada (um model só com CharField)
- [ ] Conferir `Veiculo/models.py` em main bate com o texto

Closes #2
EOF
)"
```

---

## PR 3 — Issue #3 (ADR 003 validação)

O card pede “ADR 002” no texto do hotel. No Caderno do RotaSaúde a validação é **ADR 003**.

```bash
git checkout main
git checkout -b docs/issue-3-validacao
git add docs/design/ADR-003-validacao.md
git status
git commit -m "$(cat <<'EOF'
docs: ADR 003 coloca a regra de capacidade no model

Fecha a issue #3: validar no model, não só na tela ou na view.
EOF
)"
git push -u origin HEAD
gh pr create --base main --title "ADR 003 — Validação de capacidade no model" --body "$(cat <<'EOF'
## Summary
- Capacidade 2–5 no model (`MinValueValidator` / `MaxValueValidator` + `clean()`)
- Alternativa descartada: validar só no HTML ou na view
- Numeração: issue #3 dizia ADR 002; no Caderno é 003 (002 é modelagem)

## Test plan
- [ ] Tentar capacidade 1 no admin e ver a recusa
- [ ] ADR com as cinco seções

Closes #3
EOF
)"
```

---

## PR 4 — Issue #4 (ADR 003-MVT lista)

```bash
git checkout main
git checkout -b docs/issue-4-mvt
git add docs/design/ADR-003-mvt.md
git status
git commit -m "$(cat <<'EOF'
docs: ADR da lista MVT sem cadastro pelo admin

Fecha a issue #4: view, URL e template da frota na porta da frente (só leitura).
EOF
)"
git push -u origin HEAD
gh pr create --base main --title "ADR 003-MVT — Lista de veículos no padrão MVT" --body "$(cat <<'EOF'
## Summary
- Documenta `lista_veiculos`, `/Veiculo/` e `lista.html`
- Alternativa descartada: mandar o usuário final ao admin

## Test plan
- [ ] `http://127.0.0.1:8000/Veiculo/` abre a lista
- [ ] ADR com as cinco seções

Closes #4
EOF
)"
```

---

## PR 5 — Issue #5 (ModelForm + UI) — único PR de feature

```bash
git checkout main
git checkout -b feat/issue-5-modelform
git add \
  Veiculo/forms.py \
  Veiculo/views.py \
  Veiculo/urls.py \
  Veiculo/templates/Veiculo/base.html \
  Veiculo/templates/Veiculo/lista.html \
  Veiculo/templates/Veiculo/nova.html \
  Veiculo/static/Veiculo/css/app.css \
  docs/design/ADR-004-cadastro-modelform.md
git status
git commit -m "$(cat <<'EOF'
feat: cadastro de veículo pela porta da frente com ModelForm

O usuário final grava pela página nossa; a regra de capacidade continua no model.
EOF
)"
git push -u origin HEAD
gh pr create --base main --title "Cadastro de veículos pela porta da frente (ModelForm)" --body "$(cat <<'EOF'
## Summary
- `VeiculoForm` + view `novo_veiculo` + `/Veiculo/nova/`
- CSRF, POST, redirect para a lista
- UI Bootstrap (base, lista, nova) sem mudar o contrato da aula
- ADR 004: ModelForm, não o admin

## Test plan
- [ ] GET `/Veiculo/` — tabela + “Novo veículo”
- [ ] GET `/Veiculo/nova/` — form com CSRF
- [ ] POST válido — 302 e registro na lista
- [ ] POST capacidade 1 ou 6 — recusa, não grava
- [ ] Não usar `/admin/` neste fluxo

Closes #5
EOF
)"
```

---

## PR 6 — Issue #6 (Caderno Marco 1 + Strategy + README) — último

Sai da branch da issue 5 (já com o form). Se o PR 5 ainda não mergeou:

```bash
git checkout feat/issue-5-modelform
git checkout -b docs/issue-6-marco-1
```

Se o PR 5 **já** estiver em `main`:

```bash
git checkout main
git pull origin main
git checkout -b docs/issue-6-marco-1
```

Arquivos deste PR:

```bash
git rm docs/design/ADR-004-polimorfismo.md
git add \
  docs/design/ADR-005-strategy.md \
  docs/design/ADR-006-polimorfismo.md \
  docs/relatorio-aula05.md \
  docs/roteiro-prs.md \
  README.md \
  .gitignore
git status
git commit -m "$(cat <<'EOF'
docs: Caderno do Marco 1, Strategy e README do RotaSaúde

Consolida os ADRs, registra que Strategy não entra agora e descreve a arquitetura.
EOF
)"
git push -u origin HEAD
gh pr create --base main --title "Marco 1 — Caderno consolidado, Strategy e README" --body "$(cat <<'EOF'
## Summary
- ADR 005: Strategy não se aplica no Marco 1 (sem algoritmos intercambiáveis)
- ADR 006: polimorfismo só registrado (sai o número 004 antigo)
- README com MVT, rotas, regra de capacidade e engenheiro fjunior
- `.gitignore` para `.venv` e caches
- Relatório da aula 05 / UI

## Test plan
- [ ] `docs/design/` tem 001, 002, 003, 003-mvt, 004, 005, 006
- [ ] Cada ADR tem alternativa descartada com porquê
- [ ] README abre e o `runserver` ainda sobe
- [ ] Pasta `docs/design/` visível no GitHub após o merge

Closes #6
EOF
)"
```

---

## Depois de mergear

No GitHub, conferir que cada issue fechou (`Closes #N`).  
No Teams, o Relator cola o link da pasta:

`https://github.com/silvageisedell-debug/RotaSaude/tree/main/docs/design`

## Ordem sugerida

1 → 2 → 3 → 4 (podem ser PRs paralelos, arquivos diferentes)  
5 (feature)  
6 (último — README e Caderno)
