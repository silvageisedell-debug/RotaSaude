# ADR 006 — Onde polimorfismo caberia no RotaSaúde

## Contexto

No RotaSaúde existem tipos de veículo que fazem coisas semelhantes de formas diferentes (ambulância, van, carro de passeio): capacidade, tempo de resposta e custo operacional. O model atual é um único `Veiculo`. Este arquivo existia em main como `ADR-004-polimorfismo.md`; no Caderno o 004 é o ModelForm — daí o número 006.

## Decisão

**Registrar** polimorfismo como desenho futuro: classe base `Veiculo` e subclasses (`Ambulancia`, `Van`, `CarroPasseio`) com `capacidade_maxima()`, `tempo_resposta()`, `custo_operacional()`. Uma função genérica trata todos os tipos sem `if/elif`. **Ainda não implementar** — o Marco 1 não tem tipo no cadastro (ADR 005).

## Alternativa descartada

Manter `if/elif` por tipo no código de despacho quando esses tipos existirem.

Funciona com dois tipos; cada tipo novo obriga a mexer na função e arrisca quebrar os que já passaram no teste. Não escala. Também descartamos implementar a hierarquia agora só para o Caderno ficar “completo”: viraria código morto.

## Consequência

A decisão fica rastreável sem inflar o model. Quando o produto tiver tipo, este ADR autoriza subclasses (e combina com Strategy no cálculo, ADR 005). Até lá, capacidade 2–5 no model único continua valendo.

## Desafios

O arquivo antigo usava o número 004 e colidia com o homework de ModelForm. Quem for defender oralmente: 004 = porta da frente; 006 = tipos no futuro.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
