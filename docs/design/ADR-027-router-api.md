# ADR 027 — Telas no router da API

## Contexto

As telas do RotaSaúde são renderizadas no servidor (ADR 003 e ADR 025). Quem chama a mesma URL fora do navegador, como o Postman, recebe HTML e esbarra no CSRF da sessão. A regra de negócio já está nos formulários e nos `services.py`. Faltava uma porta que devolvesse só JSON, com o mesmo contrato de permissão por módulo (ADR 023), sem desligar as páginas que o operador usa.

## Decisão

Entra o Django REST Framework 3.16.1. Um `DefaultRouter` em `portal/api_urls.py` é incluído em `/api/` por `portal/urls.py`. O renderer padrão é só JSON. A autenticação tenta primeiro o token (`rest_framework.authtoken`) e depois a sessão.

`POST /api/entrar/` recebe `email` e `senha`, reutiliza o `LoginForm` e devolve `{token, usuario}`. `POST /api/sair/` apaga o token. As demais chamadas enviam `Authorization: Token <chave>`.

Cada tela vira um viewset com serializer. O viewset não reescreve a regra: grava pelo `ModelForm` que a tela já usa e, nas ações, chama o serviço existente. Sem token a resposta é `401`. Perfil sem o módulo é `403`.

| Tela | Viewset | Rotas |
|---|---|---|
| Início | `InicioViewSet` | `GET /api/inicio/` |
| Resumo | `ResumoViewSet` | `GET /api/resumo/` |
| Veículos | `VeiculoViewSet` | `GET` e `POST /api/veiculos/`, `GET` `PUT` `PATCH` e `DELETE /api/veiculos/<pk>/`, `POST …/status/` |
| Modelos | `ModeloViewSet` | `GET /api/modelos/` |
| Motoristas | `MotoristaViewSet` | `GET` e `POST /api/motoristas/`, `GET` `PUT` e `PATCH /api/motoristas/<pk>/` |
| Pontos | `PontoEmbarqueViewSet` | `GET` e `POST /api/pontos/`, `GET` `PUT` `PATCH` e `DELETE /api/pontos/<pk>/` |
| Pedidos de ponto | `PedidoPontoViewSet` | `GET` e `POST /api/pedidos-ponto/`, `POST …/aprovar/` e `…/recusar/` |
| Usuários | `UsuarioViewSet` | `GET` e `POST /api/usuarios/`, `GET /api/usuarios/<pk>/`, `POST …/acesso/` |
| Permissões | `PermissaoViewSet` | `GET` e `POST /api/permissoes/` |
| Categorias e destinos | `CategoriaViewSet`, `DestinoViewSet` | `GET /api/categorias/`, `GET /api/destinos/` |
| Solicitações | `SolicitacaoViewSet` | `GET` e `POST /api/solicitacoes/`, `GET` `PUT` e `PATCH /api/solicitacoes/<pk>/`, `POST …/aprovar/`, `…/recusar/` e `…/cancelar/` |
| Viagens | `ViagemViewSet` | `GET` e `POST /api/viagens/`, `GET /api/viagens/<pk>/`, `GET /api/viagens/disponibilidade/`, `POST …/iniciar/`, `…/concluir/`, `…/cancelar/` e `…/embarque/` |
| Caderno | `AnotacaoViewSet` | `GET` e `POST /api/anotacoes/`, `GET` `PUT` `PATCH` e `DELETE /api/anotacoes/<pk>/`, `POST …/concluir/`, `…/adiar/` e `POST /api/anotacoes/avisado/` |

Frota, usuários e permissões continuam do administrador. O caderno continua só do atendente. `DELETE` de veículo com viagem responde `409` e não apaga (`PROTECT`). `DELETE` de ponto desativa o registro, como a tela. A collection `postman/RotaSaude.postman_collection.json` cobre essas rotas.

As URLs HTML (`/frota/veiculos/`, `/viagens/`, `/contas/entrar/` e as demais) permanecem. A disponibilidade calculada (ADR 022) não muda de lugar: `GET /api/viagens/disponibilidade/` só publica o que `viagens.services.disponibilidade` já calculava.

## Alternativa descartada

Trocar as views HTML por JSON. O operador perderia as telas. Também foi descartado um `JsonResponse` solto em cada view, sem serializer nem router: cada tela inventaria o próprio formato e a própria autenticação.

## Consequência

O navegador e o Postman passam pela mesma validação. Quem integra usa o token e não mexe no CSRF das páginas. Entra a migration do `authtoken`. O cabeçalho é `Token`, não `Bearer`.

## Desafios

A lista e o detalhe devolvem o CPF do motorista mascarado. Criar e editar ainda exigem o valor completo, porque o formulário valida o documento. O `PATCH` existe nos viewsets que editam; a collection usa `PUT` com o corpo inteiro.

## Status

Adotado nesta entrega.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).
