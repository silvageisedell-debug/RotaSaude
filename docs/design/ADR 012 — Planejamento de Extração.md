# ADR 012 — Planejamento de Extração de Service no RotaSaúde

## Contexto

Analisamos as views atuais do módulo de Veículo (lista_veiculos, novo_veiculo, editar_veiculo, apagar_veiculo) e identificamos que todas são simples: realizam operações básicas de CRUD sem misturar responsabilidades complexas. Cada view executa uma única tarefa — buscar dados, validar formulário ou renderizar template — sem aplicar regras de negócio elaboradas.

Reconhecemos que extrair um Service neste momento seria desnecessário. No entanto, conforme o RotaSaúde evolua e novas funcionalidades sejam implementadas (como reservas, cálculo de tarifas com desconto, validação de compatibilidade de mobilidade), haverá oportunidade de aplicar extração.

## Decisão

Não extrairemos um Service das views de Veículo agora. Quando funcionalidades mais complexas forem desenvolvidas — especialmente views que busquem dados de múltiplos modelos, apliquem regras de negócio ou transformem dados antes de renderizar — identificaremos o candidato ideal e executaremos a extração seguindo este mesmo padrão de ADR.

## Alternativa descartada

Forçar a extração de um Service mesmo em views triviais. Descartado porque adicionaria complexidade desnecessária ao código.

## Consequência

O código de Veículo permanece simples e direto, fácil de entender e manter. Quando a complexidade aumentar, teremos experiência e padrão documentado para extrair Services de forma clara e justificada.

## Status

Planejado — a extração será feita quando funcionalidades mais complexas exigirem.
