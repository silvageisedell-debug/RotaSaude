# ADR 024 — Fluxo das solicitações e pedidos de ponto de embarque

## Contexto

O transporte começa com um pedido do paciente, registrado pelo atendimento. O protótipo acompanha esse pedido por etapas (kanban e lista), exige motivo na recusa e mostra quem fez cada ação. Também permite que o atendente peça um ponto de embarque novo ao administrador.

## Decisão

O model `Solicitacao` (`solicitacoes/models.py`) guarda:

- paciente e telefone;
- tipo (consulta, hemodiálise, exame, cirurgia, fisioterapia);
- `categoria`, `ponto_embarque` e `destino`, todos com `PROTECT`;
- data e horário;
- acompanhante, mobilidade e observações;
- status, motivo da recusa, viagem, embarcou e quem registrou.

O status segue o fluxo:

- `pendente` → `aprovada` → `agendada` → `em_viagem` → `concluida`;
- `negada`, a partir de pendente ou aprovada, com motivo obrigatório de pelo menos 5 letras (`portal.forms.MotivoForm`);
- `cancelada`, a partir de pendente ou aprovada.

As transições ficam em `solicitacoes/services.py` (`registrar_solicitacao`, `aprovar`, `recusar`, `cancelar`) e em `viagens/services.py` (agendar, iniciar, concluir, cancelar viagem). Cada transição grava uma linha em `HistoricoSolicitacao`, com o texto, o usuário e a data e hora. Na conclusão da viagem, quem não embarcou volta para `aprovada`, sem viagem. Quem embarcou fica `concluida`. Cancelar a viagem devolve todos para `aprovada`.

`PedidoPontoEmbarque` (`frota/models.py`) guarda nome, endereço, CEP, justificativa, solicitante, status (`pendente`, `aprovado`, `recusado`), motivo da recusa e quem respondeu. O atendente envia em `/frota/pontos/solicitar/`. O administrador aprova (o ponto é criado na hora) ou recusa com motivo em `/frota/pontos/`.

Remover um ponto de embarque é exclusão lógica (`ativo=False`): as solicitações antigas continuam apontando para o local, e o sistema exige pelo menos um ponto ativo.

## Alternativa descartada

Trocar o status direto na view ou no admin, sem histórico. Perderia a rastreabilidade de quem aprovou, recusou ou cancelou, que o protótipo mostra no detalhe do pedido.

## Consequência

Uma solicitação só entra em viagem se estiver pendente ou aprovada e for da mesma data. Editar só é permitido em pendente ou aprovada. O selo do menu Solicitações mostra as pendentes; o selo de Frota mostra ao administrador os pedidos de ponto pendentes.

## Desafios

Cadastrar de novo um ponto com o nome de um ponto removido reativa o registro antigo, em vez de colidir com o nome único. O código exibido (`SOL-001`, `VG-01`) vem da chave primária, sem sorteio, para não haver colisão.

## Status

Adotado nesta entrega.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
