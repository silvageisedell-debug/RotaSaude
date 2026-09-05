# ADR 005 — Strategy não entra no Marco 1

## Contexto

O homework do Marco 1 pede para registrar: a equipe aplica Strategy em algum ponto, onde, ou por que não. Hoje o domínio implementado é **um** model `Veiculo` com capacidade entre 2 e 5. Não há algoritmos intercambiáveis no código (custo por tipo, fila de despacho, tempo de resposta).

## Decisão

**Não aplicar Strategy agora.** O Marco 1 fecha com validação no model + cadastro por ModelForm. Strategy passaria a fazer sentido quando existirem **famílias de regra** de verdade — por exemplo calcular custo operacional ou prioridade de rota de forma diferente para ambulância, van e carro de passeio. Até lá, um `if` prematuro ou uma hierarquia vazia só aumentaria superfície sem comportamento.

Onde caberia depois (sem código neste ciclo): uma interface `PoliticaOperacional` com `custo()` / `tempo_resposta()`, escolhida pelo tipo do veículo no despacho — alinhado ao ADR 006 (polimorfismo de tipos), que também está só registrado.

## Alternativa descartada

Implementar Strategy neste sprint “para ter o padrão no Caderno”.

Sem dois algoritmos reais, Strategy é teatro: classes vazias, nenhum teste de troca em runtime, e o form de veículo nem tem tipo. A banca do Marco 1 avalia **por que** o código está assim, não a quantidade de padrões colados.

## Consequência

O código do Marco 1 permanece um `Veiculo` + validadores + `VeiculoForm`. O custo é adiar a variação por tipo; o ganho é não fingir arquitetura. Quando o produto tiver tipo e regra de alocação, este ADR se revisita e o 006 deixa de ser só proposta.

## Desafios

Não confundir “não agora” com “nunca”. Se alguém adicionar `if tipo == ambulancia` em produção, este ADR ficou velho e precisa de um sucessor com código.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
