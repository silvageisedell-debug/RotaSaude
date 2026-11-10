# ADR 026 — Decorator no cálculo de extras e na auditoria do RotaSaúde

- Data: 2026-11-06
- Status: aceito
- Decisores: [nomes da equipe]

## Contexto
Analisamos onde o RotaSaúde teria responsabilidades opcionais a somar
a uma ação: (1) os extras de uma solicitação de transporte (embarque
domiciliar, ambulância, acompanhante), em [caminho do arquivo, ex.:
transporte/services.py]; (2) a auditoria em volta de ações como aceitar
uma solicitação ou aprovar um empréstimo; (3) a validação do ponto de
embarque a partir do endereço e da condição de mobilidade.

## Decisão
NÃO APLICAMOS o padrão Decorator em nenhum ponto do projeto neste momento.

## Justificativa
Os extras da solicitação são uma soma fixa: cada extra tem um valor
conhecido e o total é a soma dos que foram marcados. Uma lista de
adicionais com sum() resolve com menos código, sem uma classe por extra,
e o Decorator seria cerimônia onde bastaria somar uma lista.

A validação do ponto de embarque é uma sequência obrigatória de regras
(endereço, mobilidade, raio), não responsabilidades opcionais
empilháveis. Ela sempre roda inteira, então não há combinação variável
a justificar o padrão.

A auditoria seria o único candidato real, pois é opcional e envolve a
ação sem alterá-la. Porém o Django já oferece signals e middleware para
registrar eventos, e o projeto tem poucas ações auditáveis. Criar uma
hierarquia de decoradores só para isso aumentaria a complexidade sem
ganho proporcional.

Também registramos a delimitação: o @ de função do Python (como
@login_required) é uma sintaxe da linguagem para envolver funções e não
é o padrão Decorator de projeto, que envolve um objeto mantendo a mesma
interface. Usamos o @ onde ele já resolve, como nas views, sem tratá-lo
como aplicação do padrão.

## Consequências
Os extras continuam como lista somada e a auditoria, quando necessária,
fica com signals do Django. O código fica mais simples e fácil de
defender na P3. Reavaliaremos se surgirem combinações opcionais
variáveis, como descontos empilháveis, que passem a justificar o padrão.