# ADR 022 — Disponibilidade calculada e viagem programada

## Contexto

A ADR 017 criou o cadastro manual `Disponibilidade` (veículo, data, horário e vagas) e a ADR 019 publicou a rota (`Viagem`) em cima dele. No protótipo de apresentação, o operador não registra disponibilidade: ele escolhe data, saída e duração, e o sistema mostra quais veículos e motoristas estão livres ou ocupados naquele horário. Manter o cadastro manual criaria duas verdades sobre o mesmo veículo e não impediria dois agendamentos no mesmo horário.

## Decisão

O model `Disponibilidade` sai. A disponibilidade passa a ser calculada em `viagens/services.py` (`disponibilidade(data, saida=None, duracao_horas=None)`), a partir de:

- status do veículo (`Disponível`, `Em viagem`, `Manutenção`);
- validade da CNH do motorista na data;
- viagens ativas (`programada` e `em_andamento`) que se sobrepõem à janela pedida.

Sem horário, a função devolve a visão do dia (Disponível, Programado, Em viagem, Manutenção, CNH vencida). Com horário, devolve a visão da janela (Disponível, Ocupado, Em viagem, Manutenção, CNH vencida). O endpoint `/viagens/disponibilidade/` (`viagens:disponibilidade`) entrega essa lista em JSON para o seletor da tela de programar.

O model `Viagem` (`viagens/models.py`) passa a ter `veiculo` e `motorista` (`PROTECT`), `data`, `saida`, `duracao_horas` (1 a 12), `destino` (resumo), `status` (`programada`, `em_andamento`, `concluida`, `cancelada`) e `criado_por`. As solicitações se ligam à viagem por `Solicitacao.viagem`.

`validar_programacao` recusa a viagem quando:

- nenhum paciente foi marcado;
- a data é anterior a hoje ou difere da data da solicitação;
- a saída é antes das 05h ou a chegada passa das 20h;
- o veículo está em manutenção;
- a CNH do motorista está vencida na data;
- a soma de lugares (paciente + acompanhante) passa da capacidade do veículo;
- o veículo ou o motorista já têm viagem ativa que se sobrepõe.

`programar_viagem` grava tudo numa transação. `iniciar_viagem`, `concluir_viagem`, `cancelar_viagem` e `alternar_embarque` cuidam da execução.

A `CategoriaRota` (ADR 018) vira `solicitacoes.Categoria`, com o mesmo seed (Urgente 1, Prioritária 2, Eletiva 3): a prioridade é do pedido do paciente, não do trajeto. A `Parada` (ADR 020) continua em `viagens`, com `UniqueConstraint` em `(viagem, ordem)` e `CASCADE`. Agora é gerada ao programar: os pontos de embarque, na ordem do horário dos pacientes, e no fim os destinos.

## Alternativa descartada

Manter o cadastro manual e acrescentar o cálculo ao lado. Duplicaria a regra, e uma disponibilidade registrada poderia contradizer as viagens já agendadas.

## Consequência

As ADRs 017 e 019 ficam substituídas. Não existe mais a tela `/disponibilidade/nova/`: a disponibilidade aparece no Início e no quadro de Viagens. A validação mora no serviço, então o formulário e qualquer outra porta de entrada que chame o serviço aplicam a mesma regra. O admin do Django grava sem passar por ela.

## Desafios

A sobreposição é comparada em minutos (`início < fim existente` e `início existente < fim`). Um veículo marcado como "Em viagem" sem viagem registrada no dia continua indisponível hoje. O itinerário automático não permite reordenar paradas à mão; isso fica para uma próxima entrega, se a equipe precisar.

## Status

Adotado nesta entrega.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
