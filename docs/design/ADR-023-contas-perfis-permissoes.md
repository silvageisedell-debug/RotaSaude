# ADR 023 — Contas, perfis e permissões por módulo

## Contexto

Até aqui qualquer visitante abria todas as telas. O protótipo define perfis (Administrador, Atendente / Regulador, Auxiliar administrativo e Administrativo), cadastro de atendente que aguarda liberação e uma matriz em que o administrador decide quais módulos cada perfil enxerga.

## Decisão

- O usuário é o model próprio `contas.Usuario` (`AbstractUser`), configurado em `AUTH_USER_MODEL`, com `nome`, `email` único e `perfil` (`admin`, `atendente`, `auxadm`, `administrativo`). O superusuário vira `admin` ao salvar.
- O login é por e-mail e senha, pelo backend `contas.backends.EmailBackend`. `is_active` representa o acesso liberado.
- `/contas/solicitar-acesso/` é público: o atendente se cadastra (com aceite da LGPD) e nasce inativo. O administrador libera ou desativa em `/contas/usuarios/`, onde também cadastra usuários já liberados.
- `PermissaoModulo` (`perfil`, `modulo`, único no par) liga um módulo a um perfil. Sem linha, o módulo fica oculto. Em `/contas/permissoes/` o administrador liga ou desliga Início, Solicitações, Viagens e Frota para os três perfis não administradores. Usuários e Permissões são sempre só do administrador; o Caderno é só do atendente. A migration `0002_permissoes_padrao` libera Início, Solicitações e Viagens para os três perfis.
- As views usam os decoradores `modulo_requerido(modulo)` e `so_admin` (`contas/permissoes.py`), que exigem login e respondem 403 quando o perfil não tem o módulo.
- O context processor `contas.context_processors.menu` monta o menu lateral com os módulos liberados, os selos de pendência e a contagem de viagens em andamento.

## Alternativa descartada

Usar grupos e permissões nativos do Django por model (`add_`, `change_`). A granularidade é por tabela, não por área da tela, e o administrador precisaria entrar no admin para configurar.

## Consequência

Toda tela, menos login e solicitar acesso, exige usuário autenticado. Mudanças na matriz valem na próxima requisição. Como o model de usuário mudou, o banco precisou ser recriado (ADR 021). As contas de teste vêm do comando `popular_demo` e só aparecem na tela de login com `DEBUG` ligado.

## Desafios

O backend gasta o tempo de um hash mesmo quando o e-mail não existe, para não revelar quais e-mails estão cadastrados. O login diferencia "senha errada" de "acesso ainda não liberado" só quando a senha confere. O `next` do login é conferido para não redirecionar a outro site.

## Status

Adotado nesta entrega.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

4387940
