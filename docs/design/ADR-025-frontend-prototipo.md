# ADR 025 — Frontend migrado do protótipo de apresentação

## Contexto

A equipe apresenta o RotaSaúde com um protótipo só de frontend (um único `index.html`, usado como referência e não versionado no repositório), em que HTML, CSS e JavaScript ficam num único arquivo e os dados ficam só na memória do navegador. As telas Django antigas usavam Bootstrap e uma navbar simples, sem a identidade visual do protótipo.

## Decisão

A interface do protótipo foi levada para templates Django, com dados reais do banco:

- Layout com menu lateral recolhível, selos de pendência, saudação, faixa animada da ambulância (ativa quando há viagem em andamento) e tema escuro por `prefers-color-scheme`.
- Início com indicadores, gráfico de solicitações por status (Chart.js), disponibilidade de hoje, viagens do dia e pedidos que precisam de ação.
- Solicitações em kanban ou lista com busca e filtro. Viagens em quadro de horários (barras por veículo, das 05h às 20h). Ao programar, o seletor flutuante de veículo e motorista é alimentado por `/viagens/disponibilidade/`.
- Tour "Conheça o sistema", tabelas que viram cartões no celular e Caderno com bilhetes coloridos e lembretes.
- O botão "Recuperar" abre um resumo (pendências, viagens de hoje, últimas ações, copiar resumo) e oferece retomar rascunhos de formulário salvos no `localStorage` do aparelho.

O servidor renderiza todas as telas. Os avisos (toasts) vêm do framework de mensagens do Django. O CSS e o JS ficam em `static/` e o layout em `templates/base.html`.

Do projeto de referência de terceiros, a equipe aproveitou apenas ideias de regra, reescritas do zero no modelo deste projeto: checagem de conflito de horário, lotação por paciente e acompanhante, histórico de transições e justificativa obrigatória na recusa. Nenhum código ou template foi copiado.

## Alternativa descartada

Manter Bootstrap e redesenhar as telas sem seguir o protótipo. A apresentação e o sistema real ficariam visualmente diferentes, e o protótipo deixaria de servir como referência de validação.

Ficaram de fora, de propósito:

- o portal e app do paciente (o próprio protótipo deixou de ter cadastro de paciente);
- o backup e a restauração do banco inteiro pelo `localStorage` (no servidor, o administrador usa `dumpdata` e `loaddata`);
- o envio do resumo por e-mail via `mailto`, que depende de servidor de e-mail.

## Consequência

As telas precisam de internet só para a fonte e o Chart.js; o restante é estático do projeto. Os rascunhos do "Recuperar" ficam só no aparelho em que foram digitados. As regras continuam no servidor: o JavaScript só melhora a experiência e nunca é a validação oficial.

## Desafios

O protótipo montava as telas com JavaScript. A migração separou o que é regra (views e serviços) do que é apresentação (templates e `static/js`). O seletor flutuante desabilita opções ocupadas, mas o servidor revalida a programação ao salvar.

## Status

Adotado nesta entrega.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
