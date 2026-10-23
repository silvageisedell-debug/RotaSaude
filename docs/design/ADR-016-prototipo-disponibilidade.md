# ADR 016 — Protótipo da tela de disponibilidade

## Contexto

A frota já existe na porta da frente: marca, modelo e veículo em `/Veiculo/`. O operador ainda não tem tela para informar que um veículo está disponível num horário, com um número de vagas. O Taiga pede esse desenho no estilo “tenho lugar neste horário”, antes de existir view ou model.

Esta é a primeira atividade do pipeline de operação (ADR 015, issue #20). O protótipo é o contrato visual da issue seguinte, o formulário real.

## Decisão

A disponibilidade entra primeiro como HTML estático, em `docs/design/prototipo-disponibilidade.html`. O arquivo abre no navegador sem Django. Não há model, view, URL nem migration nesta entrega.

O estilo do app vai no próprio arquivo, num `<style>`, com as variáveis e as classes de `Veiculo/static/Veiculo/css/app.css`. Bootstrap 5.3 e Bootstrap Icons vêm do CDN. A barra e o rodapé são desenho: os links são `#`, com os itens Veículos e Disponibilidade. Teal `#0f766e` na barra e no botão `btn-rs`, teal escuro `#115e59` no hover, fundo `#f4f7f6`, texto `#134e4a`, card branco `rs-card` com cantos de `1rem` e sombra suave.

A página empilha três estados. Cada um tem o rótulo (“1. Formulário”, “2. Erro”, “3. Sucesso”) e uma anotação visível para quem for implementar. O exemplo é o mesmo nos três: veículo ABC1D23 — Toyota Corolla, data 21/10/2026, horário 08:00, 3 vagas.

1. **Formulário.** Card com o título “Registrar disponibilidade”. O veículo é um `<select>`, não texto livre, no mesmo espírito da ADR 002. As opções fixas são “Selecione um veículo”, “ABC1D23 — Toyota Corolla” (selecionada), “DEF4G56 — Fiat Ducato” e “HIJ7K89 — Renault Master”. Data (`type="date"`, valor `2026-10-21`), horário (`type="time"`, valor `08:00`) e vagas (`type="number"`, valor `3`). Ao lado da data: “A data não pode ser anterior à atual.” Ao lado do horário: “O horário é obrigatório.” O botão Salvar é `type="button"`, para o desenho não recarregar. Há também o link Voltar.

2. **Erro.** O mesmo card, com `alert alert-danger` e as frases “A data não pode ser anterior a hoje.” e “Informe o horário.” A data do exemplo inválido é `2026-10-19` e o horário fica em branco; os dois campos levam `is-invalid` e repetem essas frases no feedback. A anotação deixa explícito que a view valida e o template só exibe o alerta.

3. **Sucesso.** Card com o título “Disponibilidade registrada” e `alert alert-success`: “Disponibilidade registrada: veículo ABC1D23 — Toyota Corolla, data 21/10/2026, horário 08:00, 3 vagas.”

## Alternativa descartada

Desenhar a tela só no papel, ou só numa descrição da issue. Quem implementa o formulário real precisa abrir o HTML e reproduzir card, seletor, campos e alertas sem reinventar o layout.

Ligar este HTML numa view nesta issue. A ADR 015 reserva model, view e validação no servidor para a entrega seguinte. Antecipar a view misturaria o contrato visual com a gravação.

## Consequência

A issue do formulário real reproduz este contrato: o `<select>`, data, horário, vagas, as duas regras ao lado dos campos, o alerta vermelho com as duas frases, o feedback nos campos inválidos e a frase verde do sucesso. Mudar o visual depois exige atualizar o protótipo e a tela juntos.

O exemplo é ilustrativo. Gravar disponibilidade, validar a data no servidor, categorias, publicação de rota e paradas ficam fora desta decisão.

## Desafios

O HTML não consulta o banco. Os veículos do `<select>` são fixos; a lista real só existe quando a view da issue seguinte ler os veículos cadastrados. O campo de data mostra o valor no formato do navegador; o texto de sucesso permanece em 21/10/2026. Sem rede, o CDN do Bootstrap não carrega e a página perde o estilo. O botão Salvar não envia nada: neste arquivo ele só segura o desenho.

## Status

Proposto até o pull request desta issue entrar em `main`.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
