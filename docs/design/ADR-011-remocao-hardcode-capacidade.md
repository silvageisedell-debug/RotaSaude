# ADR-011: Remoção de Limites Rígidos (Hardcoded) na Capacidade de Veículos

## 1. Contexto e Problema
Na versão inicial do modelo `Veiculo` e no seu respectivo formulário `VeiculoForm`, a capacidade de ocupantes foi limitada estaticamente através de *validators* definidos em código, variando entre um mínimo de 2 e um máximo de 5 lugares (hardcoded).

Com a evolução do domínio do sistema RotaSaúde — no qual o transporte de pacientes frequentemente exige acomodar vans ou micro-ônibus —, manter essa regra estática acoplada ao *core* do `models.py` tornou-se um bloqueio para a escalabilidade e o registro correto da frota atual.

## 2. Decisão Arquitetural
Foi decidido **remover integralmente as validações engessadas de capacidade** do sistema central. 
As seguintes ações foram tomadas nestas classes:
- Retirada do `MinValueValidator` e `MaxValueValidator` da propriedade `capacidade` em `Veiculo`.
- Remoção do método nativo `clean()` do Model que disparava erros de tela baseados nessa mesma margem.
- Remoção da injeção de atributos em HTML (`min="2"` e `max="5"`) na renderização do form em `VeiculoForm`.

## 3. Motivos e Consequências
**Motivação Principal:**
Evitar que lógicas de negócio transitórias fiquem presas ("chumbadas") na modelagem base de infraestrutura. A capacidade do veículo não deve ser controlada de forma estática, mas sim ser fruto da modelagem futura dos "Tipos de Veículo" (via bancos dinâmicos ou por herança de polimorfismo discutida na `ADR-006` e `ADR-008`).

**Consequências:**
- **Positivas:** A aplicação desbloqueia instantaneamente a manutenção de veículos utilitários maiores sem necessidade de intervenção de código; melhora da simplicidade da classe base `Veiculo`.
- **Pontos de Atenção e Governança:** Devido à remoção dessa proteção inicial do código, a validação e as restrições passarão a ser configuradas organicamente no sistema pelo **setor administrativo (Backoffice)**. O administrador será responsável por parametrizar corretamente a capacidade no cadastro específico para cada "Tipo de Veículo" (vans, micro-ônibus, ônibus, utilizando o Design Pattern *Strategy*). As **atendentes (Frontend)** apenas consumirão esses cadastros confiáveis criados pelo ADM para organizar quantos passageiros irão em cada viagem agendada, assegurando a regra de negócio sem a necessidade de impeditivos no código-fonte.
