# ADR 026 — Redesign visual: moldura em L e folha branca

## Contexto

O ADR-025 levou o protótipo de apresentação para os templates Django. A parte visual veio junto: menu lateral em degradê verde-escuro, indicadores com borda esquerda colorida e sombra que sobe no hover, fonte Plus Jakarta Sans em peso 800, raios de 16 a 24px, emoji em títulos e avisos, chips em quase todo controle e a faixa animada da ambulância no rodapé. Para quem usa o sistema todo dia, o conjunto parecia demonstração, não ferramenta de trabalho.

## Decisão

Só a camada visual muda. Telas, rotas, formulários, regras e comportamentos do ADR-025 continuam os mesmos.

- Estrutura: a sidebar e a barra do topo (48px) dividem um fundo verde-acinzentado (`--ground: #f4f7f5`), sem linha entre elas. O conteúdo fica numa folha branca com borda de 1px, raio de 16px, afastada 8px da direita e de baixo, sem sombra.
- Cor: o verde da marca (`--accent` e `--chart-1`, `#15803d`) fica no logo, no sublinhado da aba ativa e na ação primária de cada tela. O restante da interface é cinza. O status aparece numa pílula neutra com um ponto da cor do estado.
- Tipografia: IBM Plex Sans 400, 500 e 600. Título da página em 22px/600, seções em 16px, números com `tabular-nums`. A Caveat sai; o título do bilhete do Caderno passa a usar Plex 600 em 16px.
- Componentes: indicadores num único contêiner com divisórias de 1px. Tabelas sem cartão em volta, com linhas de 48px e cabeçalho cinza em 12px. Filtros de status viram abas sublinhadas, Kanban e Lista viram controle segmentado, e os botões têm 34px e raio de 6px (um preenchido, os outros contornados).
- Faixa de viagens (`#road`): o elemento e o texto ficam, mas na barra do topo, com um ponto de 6px (verde quando há viagem em andamento). O SVG da ambulância e a animação saem.
- Gráfico de solicitações por status: barras horizontais numa cor só (`--chart-1`), em vez da rosca com uma cor por status.
- Menu lateral: fica sempre na lateral, em qualquer largura. A partir de 1200px aparece completo e pode ser recolhido pelo botão ‹ ›, e a preferência fica salva no aparelho. Abaixo de 1200px, inclusive no celular, vira uma coluna só de ícones (64px, ou 56px até 640px), e o contador de pendências vira um ponto sobre o ícone. Ao abrir, o menu completo fica por cima da tela, com um fundo escurecido que bloqueia o conteúdo. Para usar a tela é preciso recolher o menu, pelo botão, clicando no fundo ou com Esc.
- Menu da conta: o avatar, o nome e o perfil ficam à direita da barra do topo, no lugar do rótulo de perfil. Ao clicar, abre uma lista com "Alterar senha", a troca de tema e "Sair". No celular a barra mostra só o avatar, e o menu repete o nome e o perfil.
- Responsividade:
  - Kanban: colunas com no mínimo 240px e rolagem horizontal.
  - Indicadores: ficam em 2×2 abaixo de 1200px.
  - Abaixo de 900px: a folha perde a moldura.
  - Abaixo de 640px: tabelas viram cartões, e formulários e ação principal ocupam toda a largura.
- Tema: o modo escuro segue o `prefers-color-scheme` e só redefine os tokens de cor, com neutros sem azul. A troca manual fica no menu da conta. A escolha vai para o `localStorage` (`rs_tema`) e é aplicada por um script no `<head>`, antes de desenhar a página, para não piscar. O atributo `data-theme` no `<html>` vale mais que o tema do sistema.
- Todas as cores ficam em tokens no `:root` de `static/css/rotasaude.css`. Exceção: as cores do bilhete, que vêm do modelo (`Anotacao.CORES`).

## Alternativa descartada

Ajustar o visual antigo aos poucos, por exemplo tirando só os degradês e o emoji. A sidebar escura, os indicadores coloridos e a faixa animada continuariam brigando pela atenção com os dados, e cada tela ficaria com uma regra diferente.

## Consequência

A tela fica mais densa e calma: a cor aparece nos dados e na ação principal, não no cromo. As regras de negócio no JavaScript não mudaram. Mudou só a interface:
- as cores fixas do seletor de disponibilidade passaram a usar tokens;
- o gráfico passou de rosca para barras de uma cor e lê as cores dos tokens na hora de desenhar, para acompanhar a troca de tema;
- entraram o menu lateral sobreposto (classe `aberto`, que não é gravada), o fechamento do menu da conta ao clicar fora ou com Esc, e a troca de tema. Os ganchos usados pelo JS e pelo tour (ids, `data-*` e classes) continuam iguais. A fonte e o Chart.js ainda dependem de internet.

## Desafios

Os textos do tour vêm de atributos `data-tour-texto` que não mudaram. O texto da faixa de viagens ainda fala da ambulância que se move.
O passo "Seu perfil" do tour passou do rótulo de perfil para o resumo do menu da conta.
"Alterar senha" ainda não tem tela. O item aponta para `#`, com um `TODO` em `templates/base.html`. As cores de status vêm do servidor (`painel/templatetags/rs.py`) com tons saturados. Como o redesign não mexe em Python, elas ficaram restritas ao ponto do selo e às barras claras do quadro de horários.

## Status

Adotado nesta entrega. Substitui a parte visual do ADR-025.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

73e7447
