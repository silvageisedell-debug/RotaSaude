# RotaSaúde

Protótipo acadêmico (ISW-030 Web III / ILP — FATEC Olímpia) de **frota de transporte assistencial**. A organização parceira lista, cadastra, edita e apaga veículos pela porta da frente, sem usar o Django Admin.

**Repositório:** [silvageisedell-debug/RotaSaude](https://github.com/silvageisedell-debug/RotaSaude)

## Equipe e Responsabilidades

Cada papel tem um dono específico designado para os ciclos de entrega do projeto.

| Papel | Quem | GitHub |
|---|---|---|
| Tech Lead e Arquiteto | **Fabio** | [frfjunior](https://github.com/frfjunior) |
| QA e Controle do Taiga | **Geise** | [silvageisedell-debug](https://github.com/silvageisedell-debug) |
| Scrum Master | **Igor** | [ignisolus](https://github.com/ignisolus) |
| Apoio de Documentação Física | **Kaique** | [Kaique029](https://github.com/Kaique029) |

### Tech Lead e Arquiteto — Fabio

Responsável técnico central pela engenharia de software e modelo de dados. Desenha a arquitetura do domínio (**Veículo**, etc.) implementando models, views, forms e templates, e é o responsável exclusivo por pautar e redigir as Decisões de Arquitetura no Caderno de Design (ADRs) disponíveis em `docs/design/`.

### QA e Controle do Taiga — Geise

Controladora do repositório ágil e das pontes operacionais. Detém o controle sistemático do _Taiga_, orquestrando a gestão de issues, apontando dependências e validando entregas cruzadas no GitHub antes da aprovação final (Merge). Ela dita a cadência das *User Stories*.

### Scrum Master — Igor

Responsável por blindar a equipe técnica, remover impedimentos e assegurar que as cerimônias ágeis e a comunicação avancem de forma sinérgica. Atua ativamente na organização administrativa das Sprints, orquestrando as pautas de alinhamento e operando como o facilitador chave do processo metodológico da equipe para garantir fluência desde a issue até a entrega final.

### Apoio de Documentação Física — Kaique

Atua no suporte logístico da equipe. É o encarregado formal de repassar as técnicas e diagramações desenvolvidas digitalmente (em código e texto) para o caderno de entrega físico do projeto exigido como documento final da disciplina.

## Como este Caderno foi escrito

Os textos em `docs/` (ADRs e relatórios) foram redigidos com **apoio de IA**, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record: contexto, decisão, e consequência. A observação de domínio técnica central (Veículo, em contraponto aos exemplos das aulas) foi definida pelo Tech Lead.

Os templates HTML usam **Bootstrap 5** aplicado com apoio de IA (utilitários, navbar, formulários e confirmação). O crédito está em comentário de fonte nos `.html`, para não poluir a interface.

## Arquitetura (MVT)

```text
Portal/          projeto Django (settings, urls raiz, WSGI/ASGI)
  settings.py    INSTALLED_APPS inclui Veiculo e Rota
  urls.py        admin/ + include("Veiculo.urls") + include("Rota.urls")

Veiculo/         app de domínio da frota
  models.py      Marca, Modelo, Veiculo
  admin.py       cadastro interno de marca/modelo/veículo
  forms.py       VeiculoForm (ModelForm) — porta da frente
  views.py       lista_veiculos, novo_veiculo, editar_veiculo, apagar_veiculo
  urls.py        /Veiculo/, /nova/, /<pk>/editar/, /<pk>/apagar/
  templates/     base.html, lista.html, nova.html, confirmar_apagar.html
  static/css/    app.css

Rota/            app da operação
  models.py      Disponibilidade (FK para Veiculo, PROTECT); CategoriaRota; Viagem
  views.py       nova_disponibilidade; lista_rotas e nova_rota
  urls.py        /disponibilidade/nova/, /rotas/, /rotas/nova/
  templates/     disponibilidade_nova.html, lista_rotas.html, rota_nova.html
```

## Regras de Negócio Implementadas

- Os formulários e lógicas básicas suportam cadastro livre para gerenciar Veículos, e os limites orgânicos operacionais (ex: ocupantes do veículo) serão parametrizados futuramente geridos de maneira escalável pelo ADM baseado no **Tipo do Veículo**, em vez de validações fixas.
- Placa, chassi e Renavam devem ser únicos e exclusivos.
- A exclusão em cascata é protegida: o `Modelo` pertence à `Marca`, e a deleção do Veículo possui a flag `PROTECT` para preservar logs. A disponibilidade também usa `PROTECT` no veículo.
- Disponibilidade: a data não pode ser anterior a hoje e o horário é obrigatório. Essa checagem mora na view `nova_disponibilidade`, não no model.
- Rota publicada (`Viagem`): origem e destino em texto, ligados a uma disponibilidade e a uma categoria já cadastradas (`PROTECT`). A tela não pede placa nem nome de categoria digitados.

## Rotas Mapeadas

| URL | Nome | Função |
|---|---|---|
| `/admin/` | — | Administração de fundos (equipe) |
| `/Veiculo/` | `lista_veiculos` | Lista geral da frota |
| `/Veiculo/nova/` | `novo_veiculo` | Realizar cadastro da frota |
| `/Veiculo/<pk>/editar/` | `editar_veiculo` | Edição dos dados |
| `/Veiculo/<pk>/apagar/` | `apagar_veiculo` | Confirmação em GET, apagado no POST |
| `/disponibilidade/nova/` | `nova_disponibilidade` | Registrar disponibilidade e vagas |
| `/rotas/` | `lista_rotas` | Lista das rotas publicadas |
| `/rotas/nova/` | `nova_rota` | Publicar origem, destino, disponibilidade e categoria |

## Caderno de Design

Todo o escopo que validou e desenhou decisões técnicas está documentado em detalhes nos arquivos ADR (`docs/design/`):

| ADR | Decisão |
|---|---|
| ADR-001 | Adoção do ecossistema WSL2 + venv e Django |
| ADR-002 | Models estruturais de Marca / Modelo / Veiculo |
| ADR-003 | Definição da listagem no padrão nativo MVT |
| ADR-004 | Padronização das exclusividades de validação cruzada |
| ADR-005 | Cadastro da frota realizado somente por ModelForm externo |
| ADR-006 | Registro descritivo da necessidade de Polimorfismo futuro |
| ADR-007 | Strategy Pattern removido do MVP atual |
| ADR-008 | Uso do Polimorfismo postergado e registrado de forma descritiva |
| ADR-009 | Permissão para Editar e Apagar pela porta da frente (não-admin) |
| ADR-010 | Single Responsibility: Débito do VeiculoForm e suas limitações |
| ADR-011 | Remoção de limites Hardcoded estáticos de ocupantes e escalabilidade |
| ADR-013 | MVVM não entra no embarque nem no CRUD atual |
| ADR-014 | Adapter não entra no acesso ao banco |
| ADR-015 | Pipeline da operação e distribuição das atividades |
| ADR-017 | Disponibilidade do veículo no app Rota, com validação na view |
| ADR-018 | Categorias de rota com prioridade, cadastro no admin e seed |
| ADR-019 | Publicar rota: model Viagem, origem, destino, disponibilidade e categoria |

## Como Rodar o Sistema

Na primeira vez, na raiz do projeto, crie o ambiente virtual e instale as dependências nesta ordem:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Com o ambiente ativo, aplique as migrações e suba o servidor:

```bash
python manage.py migrate
python manage.py runserver
```

Acesso via `http://127.0.0.1:8000/Veiculo/`. A disponibilidade fica em `http://127.0.0.1:8000/disponibilidade/nova/`. As rotas ficam em `http://127.0.0.1:8000/rotas/`. (Garantir um superuser no `/admin/` e as modelagens de Marca, Modelo e Veículo registradas no banco).
