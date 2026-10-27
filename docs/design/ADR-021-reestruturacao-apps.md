# ADR 021 — Reestruturação em apps de domínio com nomes em minúsculo

## Contexto

O projeto nasceu com o pacote `Portal` e os apps `Veiculo` e `Rota`. As URLs misturavam maiúsculas e minúsculas (`/Veiculo/`, `/Veiculo/nova/`, `/rotas/`), e o app `Rota` acumulava disponibilidade, categoria, viagem e itinerário. O protótipo de apresentação (`prototipo_frontend/index.html`) trouxe novas áreas: contas e permissões, solicitações, frota com motoristas e pontos de embarque, viagens programadas, painel e caderno. Manter tudo em dois apps tornaria cada arquivo um depósito de regras sem relação entre si.

## Decisão

- O pacote do projeto passa a ser `portal/` (settings, urls, wsgi, asgi). O `manage.py` aponta para `portal.settings`.
- Os apps `Veiculo` e `Rota` saem e entram apps de domínio, todos em minúsculo:

| App | Responsabilidade |
|---|---|
| `contas` | usuário próprio, login por e-mail, perfis, liberação de acesso e matriz de permissões |
| `frota` | marca, modelo, veículo, motorista, ponto de embarque e pedido de ponto |
| `solicitacoes` | categoria, destino, solicitação de transporte e histórico |
| `viagens` | viagem, parada (itinerário) e regras de disponibilidade em `services.py` |
| `painel` | início com indicadores, resumo "Recuperar" e comando `popular_demo` |
| `caderno` | anotações e lembretes do atendente |

- Toda URL fica em minúsculo, com hífen quando houver mais de uma palavra, e cada app usa `app_name` (namespace). Exemplos: `/frota/veiculos/` (`frota:veiculos`), `/solicitacoes/nova/` (`solicitacoes:nova`), `/viagens/programar/` (`viagens:programar`), `/contas/solicitar-acesso/` (`contas:solicitar_acesso`), `/caderno/` (`caderno:inicio`). A tabela completa fica no README.
- As migrations foram recriadas do zero (uma `0001_initial` por app, mais as migrations de seed). O `db.sqlite3` de desenvolvimento também foi recriado; os dados de apresentação vêm de `python manage.py popular_demo`.
- O layout comum mora em `templates/` na raiz (base, parciais, erros). Cada app mantém seus templates em `<app>/templates/<app>/`. CSS, JS e imagens ficam em `static/`.

## Alternativa descartada

Manter as pastas `Veiculo` e `Rota` e só trocar as URLs para minúsculo. Preservaria as migrations antigas, mas deixaria o código misturado e os nomes de app fora da convenção do Django (`app_label` com maiúscula aparece até nas URLs do admin).

## Consequência

Bancos criados com as migrations antigas não migram para a nova estrutura: é preciso apagar o `db.sqlite3` e rodar `migrate` e `popular_demo`. Links antigos (`/Veiculo/`, `/disponibilidade/nova/`, `/rotas/`) deixam de existir. As referências nos templates passam a usar o namespace (`{% url 'frota:veiculos' %}`).

## Desafios

No Windows, renomear `Portal` para `portal` exige um nome intermediário, porque o sistema de arquivos não diferencia caixa. Os arquivos `.pyc` que estavam versionados por engano foram retirados do repositório. A dependência circular entre `solicitacoes` e `viagens` (a solicitação aponta para a viagem) foi resolvida com referência por texto (`"viagens.Viagem"`) e gerando a migration de `viagens` antes.

## Status

Adotado nesta entrega.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

4387940
