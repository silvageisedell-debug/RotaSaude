# RotaSaúde

Protótipo acadêmico (ISW-030 Web III / ILP — FATEC Olímpia) de **transporte sanitário**. A regulação registra as solicitações dos pacientes, programa as viagens com veículo e motorista disponíveis, acompanha o embarque e mantém a frota pela porta da frente, sem usar o Django Admin.

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

A interface segue o protótipo de apresentação (um `index.html` só de frontend, usado como referência e não versionado), migrado para templates Django com apoio de IA (ADR 025).

## Arquitetura (MVT)

```text
portal/            projeto Django (settings, urls raiz, WSGI/ASGI, forms e navegação comuns)
contas/            Usuario (login por e-mail), perfis, liberação de acesso, PermissaoModulo
frota/             Marca, Modelo, Veiculo, Motorista, PontoEmbarque, PedidoPontoEmbarque
solicitacoes/      Categoria, Destino, Solicitacao, HistoricoSolicitacao + services.py
viagens/           Viagem, Parada + services.py (disponibilidade, programação, execução)
painel/            início com indicadores, resumo "Recuperar", comando popular_demo
caderno/           anotações e lembretes do atendente
templates/         base.html, parciais e páginas de erro
static/            css, js e imagens (logo)
docs/              Caderno de Design (ADRs), relatórios e protótipos
```

Cada app guarda os seus templates em `<app>/templates/<app>/`. As regras ficam nos `services.py`. As views só leem a requisição, chamam o serviço e escolhem o template.

## Regras de Negócio Implementadas

- **Acesso:** o login é por e-mail. O atendente que pede acesso fica inativo até o administrador liberar. Os módulos visíveis seguem a matriz de permissões. Usuários e Permissões são só do administrador, e o Caderno é só do atendente.
- **Frota:** placa (ABC-1D23 ou ABC-1234), chassi (17 caracteres, sem I, O e Q) e Renavam são únicos. A capacidade (1 a 60) não conta o motorista. Veículo com viagem registrada não pode ser apagado (`PROTECT`).
- **Motoristas:** o CPF é validado pelos dígitos verificadores e é único; a CNH tem 11 números e é única. Não se cadastra motorista com CNH vencida, e a CNH vencida bloqueia o motorista nas viagens. CPF e CNH aparecem mascarados nas listas.
- **Pontos de embarque:** o endereço é obrigatório e o CEP, opcional. Remover desativa o ponto, sem apagar. O atendente pode pedir um ponto novo; o administrador aprova ou recusa com motivo.
- **Solicitações:**
  - a data precisa ser a partir de hoje;
  - o fluxo é pendente → aprovada → agendada → em viagem → concluída;
  - negar exige motivo de pelo menos 5 letras;
  - só dá para cancelar a partir de pendente ou aprovada;
  - toda mudança fica no histórico, com o usuário e a hora.
- **Viagens:**
  - a disponibilidade é calculada pelo status do veículo, pela validade da CNH e pelas viagens ativas;
  - a viagem sai a partir das 05h, termina até as 20h e dura de 1 a 12 horas;
  - a data precisa ser a mesma das solicitações;
  - os passageiros (paciente + acompanhante) não passam da capacidade do veículo;
  - o veículo e o motorista não podem ter viagem sobreposta;
  - ao concluir, quem não embarcou volta para aprovada.
- **Itinerário:** as paradas são geradas ao programar (os embarques pelo horário dos pacientes e depois os destinos), com ordem única na mesma viagem.

## Rotas Mapeadas

| URL | Nome | Função |
|---|---|---|
| `/admin/` | — | Administração interna (equipe) |
| `/` | `painel:raiz` | Leva ao login ou à primeira tela liberada |
| `/inicio/` | `painel:inicio` | Painel de regulação (indicadores, disponibilidade, viagens de hoje) |
| `/resumo/` | `painel:resumo` | Recuperar: pendências, viagens de hoje e últimas ações |
| `/sem-modulo/` | `painel:sem_modulo` | Aviso para perfil sem módulos liberados |
| `/contas/entrar/` | `contas:login` | Login por e-mail |
| `/contas/sair/` | `contas:sair` | Sair (POST) |
| `/contas/solicitar-acesso/` | `contas:solicitar_acesso` | Cadastro público de atendente |
| `/contas/usuarios/` | `contas:usuarios` | Lista e cadastro de usuários (admin) |
| `/contas/usuarios/<pk>/acesso/` | `contas:alternar_acesso` | Liberar ou desativar acesso (POST, admin) |
| `/contas/permissoes/` | `contas:permissoes` | Matriz de permissões por perfil (admin) |
| `/frota/veiculos/` | `frota:veiculos` | Lista e cadastro de veículos |
| `/frota/veiculos/<pk>/editar/` | `frota:editar_veiculo` | Editar veículo |
| `/frota/veiculos/<pk>/apagar/` | `frota:apagar_veiculo` | Confirmação em GET, apagado no POST |
| `/frota/veiculos/<pk>/status/` | `frota:status_veiculo` | Trocar status (POST) |
| `/frota/motoristas/` | `frota:motoristas` | Lista e cadastro de motoristas |
| `/frota/motoristas/<pk>/editar/` | `frota:editar_motorista` | Editar motorista |
| `/frota/pontos/` | `frota:pontos` | Pontos de embarque e pedidos pendentes |
| `/frota/pontos/<pk>/editar/` | `frota:editar_ponto` | Editar ponto |
| `/frota/pontos/<pk>/remover/` | `frota:remover_ponto` | Desativar ponto |
| `/frota/pontos/solicitar/` | `frota:solicitar_ponto` | Atendente pede ponto novo |
| `/frota/pontos/pedidos/<pk>/aprovar/` | `frota:aprovar_pedido` | Aprovar pedido (POST) |
| `/frota/pontos/pedidos/<pk>/recusar/` | `frota:recusar_pedido` | Recusar pedido com motivo |
| `/solicitacoes/` | `solicitacoes:lista` | Kanban ou lista (`?modo=lista&status=&q=`) |
| `/solicitacoes/nova/` | `solicitacoes:nova` | Registrar solicitação |
| `/solicitacoes/<pk>/` | `solicitacoes:detalhe` | Detalhe com histórico e ações |
| `/solicitacoes/<pk>/editar/` | `solicitacoes:editar` | Editar (pendente ou aprovada) |
| `/solicitacoes/<pk>/aprovar/` | `solicitacoes:aprovar` | Aprovar (POST) |
| `/solicitacoes/<pk>/recusar/` | `solicitacoes:recusar` | Recusar com motivo |
| `/solicitacoes/<pk>/cancelar/` | `solicitacoes:cancelar` | Cancelar (POST) |
| `/viagens/` | `viagens:quadro` | Quadro de horários do dia (`?data=AAAA-MM-DD`) |
| `/viagens/programar/` | `viagens:programar` | Programar viagem (`?solicitacao=<pk>`) |
| `/viagens/disponibilidade/` | `viagens:disponibilidade` | JSON de veículos e motoristas livres na janela |
| `/viagens/<pk>/` | `viagens:detalhe` | Passageiros, itinerário e ações |
| `/viagens/<pk>/iniciar/` | `viagens:iniciar` | Iniciar viagem (POST) |
| `/viagens/<pk>/concluir/` | `viagens:concluir` | Concluir viagem (POST) |
| `/viagens/<pk>/cancelar/` | `viagens:cancelar` | Cancelar viagem (POST) |
| `/viagens/<pk>/embarque/<solicitacao_pk>/` | `viagens:embarque` | Marcar ou desfazer embarque (POST) |
| `/caderno/` | `caderno:inicio` | Anotações e lembretes (`?f=&q=&editar=`) |
| `/caderno/avisado/` | `caderno:avisado` | Fechar o aviso de lembretes (POST) |
| `/caderno/<pk>/concluir/` | `caderno:concluir` | Concluir ou reabrir (POST) |
| `/caderno/<pk>/apagar/` | `caderno:apagar` | Apagar (POST) |
| `/caderno/<pk>/adiar/` | `caderno:adiar` | Adiar lembrete (POST) |

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
| ADR-017 | Disponibilidade do veículo no app Rota *(substituída pela ADR 022)* |
| ADR-018 | Categorias com prioridade, cadastro no admin e seed (hoje `solicitacoes.Categoria`) |
| ADR-019 | Publicar rota: Viagem com origem, destino, disponibilidade e categoria *(substituída pela ADR 022)* |
| ADR-020 | Itinerário: paradas com ordem única na mesma viagem |
| ADR-021 | Reestruturação em apps de domínio e URLs em minúsculo |
| ADR-022 | Disponibilidade calculada e viagem programada |
| ADR-023 | Contas, perfis e permissões por módulo |
| ADR-024 | Fluxo das solicitações e pedidos de ponto de embarque |
| ADR-025 | Frontend migrado do protótipo de apresentação |

## Como Rodar o Sistema

Na primeira vez, na raiz do projeto, crie o ambiente virtual e instale as dependências.

Linux / WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Com o ambiente ativo, crie o banco, carregue os dados de apresentação e suba o servidor:

```bash
python manage.py migrate
python manage.py popular_demo
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`. Contas de demonstração:

| Perfil | E-mail | Senha |
|---|---|---|
| Administrador | `admin@rotasaude.com.br` | `admin123` |
| Atendente / Regulador | `atendente@rotasaude.com.br` | `atend123` |

Para rodar os testes:

```bash
python manage.py test
```

Quem tinha um `db.sqlite3` da estrutura antiga (apps `Veiculo` e `Rota`) precisa apagá-lo antes do `migrate` (ADR 021).
