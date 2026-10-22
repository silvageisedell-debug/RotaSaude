# ADR-013: Interface e Registro de Disponibilidade de Veículo

## 1. Contexto e Problema

No sistema **RotaSaúde**, os operadores necessitam de uma interface estruturada para registrar quando um veículo da frota estará disponível para viagens, atendendo à necessidade da **História #55 do Taiga** (*"tenho lugar neste horário"*).

Para resolver essa funcionalidade de ponta a ponta, foram delimitadas duas etapas de trabalho:
1. **Tarefa 01 (Protótipo e Regras):** Desenhar o protótipo da tela com as regras de preenchimento do operador (seleção de veículos, restrições de data/horário e mensagens de feedback).
2. **Tarefa 02 (Template e Integração MVT):** Transformar o protótipo no template oficial do Django (`disponibilidade.html`), integrando com a view e as rotas do sistema sem violar o padrão arquitetural MVT.

---

## 2. Decisão Arquitetural

Decidimos estruturar a solução completa da História #55 com as seguintes diretrizes:

### A. Concepção da Interface e Regras do Operador (Tarefa 01)
- **Seletor de Veículo Vinculado (ADR-002):** A escolha do veículo ocorre unicamente por meio de uma lista suspensa (`<select>`), alimentada pelos veículos já cadastrados no banco de dados, proibindo digitação livre de texto.
- **Herança de Capacidade (ADR-011):** O formulário não possui campo avulso de vagas, pois a capacidade de passageiros é uma propriedade inerente ao cadastro do veículo, evitando duplicidade de dados.
- **Restrições Temporais:** A data informada não pode ser anterior à data de hoje (não retroativa) e o horário é de preenchimento obrigatório.
- **Ciclo de Feedback Visual:** A interface prevê mensagens claras de sucesso (verde) e de erro (vermelha) para orientar o operador.

### B. Implementação do Template e Padrão MVT (Tarefa 02)
- **Herança de Template:** Criação de `Veiculo/templates/Veiculo/disponibilidade.html` estendendo `base.html`, reaproveitando a identidade visual, navegação e rodapé do RotaSaúde.
- **Separação de Camadas (MVT):** O template HTML faz exclusivamente a apresentação visual dos campos e alertas, utilizando validação nativa simples do navegador (`required`), deixando a validação oficial a cargo da View.
- **Lógica e Roteamento:** Criação da view `disponibilidade_veiculo` em `Veiculo/views.py`, da rota `/Veiculo/disponibilidade/` em `Veiculo/urls.py` e do link de acesso no menu superior em `Veiculo/base.html`.
- **Responsividade Plena:** Interface testada no navegador via `runserver`, funcionando perfeitamente em telas de desktop e celulares.

---

## 3. Alternativas Descartadas

- **Permitir digitação livre de veículos:** Descartado para prevenir erros de digitação e garantir a integridade dos dados (ADR-002).
- **Incluir campo manual de vagas:** Descartado para respeitar a governança do ADR-011 e evitar redundância.
- **Permitir datas passadas:** Descartado pois inviabilizaria o planejamento logístico de viagens.
- **Embutir regras de negócio e validações pesadas no HTML:** Descartado para manter o padrão MVT (ADR-003), preservando o template limpo e desacoplado.

---

## 4. Consequências

- A História #55 fica 100% resolvida e documentada de ponta a ponta.
- A tela está pronta, integrada ao Django, responsiva e alinhada às decisões arquiteturais anteriores do projeto.
- O código e a documentação mantêm um padrão limpo e consistente para todo o time do RotaSaúde.

---

## 5. Status

**Adotado** (História #55 do Taiga — Tarefas 01 e 02).

---

## 6. Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

---

## 7. Commit

*(A ser preenchido após o commit do Git)*

