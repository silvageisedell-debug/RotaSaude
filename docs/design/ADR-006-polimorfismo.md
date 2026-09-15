# ADR 006 — Polimorfismo de tipos: só registrar, complementar a ADR 004

## Contexto

A ADR 004 (ModelForm) já fechou a porta da frente com **um** model `Veiculo` e um `VeiculoForm` **sem** campo de tipo. A ADR 003 já colocou capacidade 2–5 nesse model. Não há, no código, ambulância, van ou carro de passeio como classes distintas.

Este arquivo existia em `main` como `ADR-004-polimorfismo.md` e colidia com o número do ModelForm. A versão vigente do 004 é [ADR-004-cadastro-modelform.md](ADR-004-cadastro-modelform.md). O rascunho antigo ficou em [ADR-004-polimorfismo.md](ADR-004-polimorfismo.md) como ponteiro — **não** é decisão.

Este ADR **complementa** o 004: não revalida cadastro, CSRF nem intervalo de capacidade.

## Validações já feitas na ADR 004 (e na 003)

Não repetir evidência; só apontar o que o 006 herda:

- um `Veiculo` persistido (`placa`, `modelo`, `ano`, `chassi`, `renavam`, `capacidade`);
- capacidade 2–5 no model (`MinValueValidator` / `MaxValueValidator` + `clean()`);
- cadastro pela porta da frente com `VeiculoForm` — a regra **não** é reescrita no form;
- o formulário **não** pede tipo de veículo; não há hierarquia no banco.

Enquanto isso valer, polimorfismo no despacho seria código morto.

## O que este ADR acrescenta

1. **Numeração do Caderno:** 004 = ModelForm; 006 = tipos no futuro (quem defender oralmente usa essa chave).
2. **Decisão de desenho, sem código:** quando existir tipo de verdade, classe base `Veiculo` e subclasses `Ambulancia`, `Van`, `CarroPasseio` com `capacidade_maxima()`, `tempo_resposta()`, `custo_operacional()`, tratadas por uma função genérica — sem `if/elif` por tipo.
3. **Alinhamento com a ADR 005:** Strategy também não entra agora; as duas decisões andam juntas (tipo + política operacional).
4. **Correção do rascunho 004-polimorfismo:** o código atual **não** usa `if/elif` para tipo — o rascunho inventava um problema que o Marco 1 não tem.

## Decisão

**Registrar** polimorfismo como desenho futuro. **Ainda não implementar.** O Marco 1 (e o CRUD da ADR 007) continua no model único da ADR 004.

## Alternativa descartada

Implementar a hierarquia agora “para o Caderno ficar completo”, ou copiar o texto do arquivo 004-polimorfismo como se fosse outra decisão.

Sem tipo no cadastro, subclasses vazias não têm teste de troca em runtime. Duplicar o rascunho no 006 quebraria a regra de uma decisão por ADR.

## Consequência

O Caderno fica rastreável sem inflar `models.py`. Quando o produto tiver tipo, este ADR autoriza subclasses (e combina com Strategy no cálculo — ADR 005). Até lá, as validações do 004 seguem sendo a régua do código.

## Desafios

Não tratar o stub `ADR-004-polimorfismo.md` como decisão. Não confundir “não agora” com “nunca”: o primeiro `if tipo == ambulancia` em produção envelhece este ADR e o 005.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência). A observação de domínio — um `Veiculo` sem tipo — é do projeto, não da ferramenta.

## Commit

`20c94f3`
