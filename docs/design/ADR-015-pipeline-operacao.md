# ADR 015 — Pipeline da operação e distribuição das atividades

## Contexto

O marco da frota está fechado nas issues #1 a #13: marca, modelo, veículo, listagem, cadastro por ModelForm, edição e exclusão. O caderno já ocupa os dois números seguintes. A ADR 013 recusa MVVM no embarque e no CRUD atual. A ADR 014 recusa Adapter no acesso ao banco. Esta decisão é a 015.

O Taiga abre a operação. O operador precisa registrar disponibilidade do veículo, categorias de rota com prioridade, a publicação de origem e destino em cima dessa disponibilidade, e o itinerário ordenado na mesma tela.

Cinco histórias, com dependência entre elas. Sem um corte, o trabalho cai num único PR ou fica sem dono. O README já reparte papéis: Fabio (`frfjunior`) na arquitetura e no MVT, Igor (`ignisolus`) no critério verificável, Geise (`silvageisedell-debug`) nas telas que o operador vê. Kaique permanece no apoio de documentação física do caderno.

As issues da operação já estão abertas: [#20](https://github.com/silvageisedell-debug/RotaSaude/issues/20), [#21](https://github.com/silvageisedell-debug/RotaSaude/issues/21), [#22](https://github.com/silvageisedell-debug/RotaSaude/issues/22), [#23](https://github.com/silvageisedell-debug/RotaSaude/issues/23) e [#24](https://github.com/silvageisedell-debug/RotaSaude/issues/24).

## Decisão

A operação anda em cinco entregas, nesta ordem. Cada entrega é uma issue, um ADR próprio e um pull request. O responsável da issue redige o ADR daquela atividade e assina o commit com a identidade Git dele.

O ADR de cada atividade entra na mesma branch do código, quando a atividade evolui. Há um commit com a implementação e o ADR, e um segundo commit na mesma branch só com o hash curto no campo Commit. O PR fecha a issue (`Fecha #<número>`). A branch sai de `main` atualizada. O desenvolvimento só começa quando a dependência já está em `main`. Não se usa `git add .`.

Este ADR 015 é a exceção dessa cadência: ele registra o corte e a ordem antes das cinco implementações. Os ADRs 016 a 020 continuam viajando com o código de cada issue.

Distribuição:

1. **#20 — Geise** (`silvageisedell-debug`). Protótipo da tela de disponibilidade. ADR 016, `docs/design/ADR-016-prototipo-disponibilidade.md`. Sem dependência. HTML estático, três estados (formulário, erro, sucesso), seletor de veículos já cadastrados, regras anotadas: data não anterior à atual e horário obrigatório. Sem model e sem view.
2. **#21 — Fabio** (`frfjunior`). Formulário real de disponibilidade. ADR 017, `docs/design/ADR-017-disponibilidade.md`. Depende da #20. Nasce o app `Rota`. A view valida data e horário; o template só exibe as mensagens. O veículo entra por FK, com `PROTECT`.
3. **#22 — Igor** (`ignisolus`). Categorias de rota com prioridade. ADR 018, `docs/design/ADR-018-categoria-rota.md`. Depende da #21, porque o app `Rota` passa a existir ali. Admin lista nome e prioridade, nome único, seed Urgente (1), Prioritária (2) e Eletiva (3).
4. **#23 — Geise** (`silvageisedell-debug`). Publicar rota. ADR 019, `docs/design/ADR-019-publicar-rota.md`. Depende da #21 e da #22. Origem e destino em cima de uma disponibilidade, classificada por categoria. Model `Viagem` no código; a interface diz rota.
5. **#24 — Fabio** (`frfjunior`). Itinerário ordenado. ADR 020, `docs/design/ADR-020-itinerario.md`. Depende da #23. Paradas com ordem única na mesma tela da rota.

Geise e Fabio ficam com duas entregas. Igor fica com a #22, cujo aceite é lista no admin, unicidade e seed.

```text
#20 Geise protótipo (ADR 016)
        |
        v
#21 Fabio disponibilidade (ADR 017, cria o app Rota)
        |
        +-----> #22 Igor categorias (ADR 018)
        |              |
        v              v
        #23 Geise publica a rota (ADR 019)
                |
                v
        #24 Fabio itinerário (ADR 020)
```

## Alternativa descartada

Numerar este corte como ADR 013. Esse número já documenta a não adoção de MVVM. Reusar o 013, ou o 014 do Adapter, misturaria duas decisões no mesmo arquivo.

Um PR só de documentação, com os cinco ADRs antecipados, e o código numa leva seguinte. O roteiro das aulas 00 a 06 fazia o ADR entrar antes da feature. Nesta operação a decisão de cada tela se confirma no momento em que a tela existe. Antecipar os cinco textos deixaria o caderno descrevendo model, URL e mensagem que ainda podem mudar no PR.

Repartir as cinco histórias em partes iguais, ou concentrar model, view e ADR em Fabio porque o README o aponta como autor do caderno. O corte segue o papel: tela com Geise, MVT com Fabio, critério de admin e seed com Igor. Quem implementa escreve o ADR da sua issue.

## Consequência

A ordem de merge é a ordem das dependências. Categoria não entra antes do app `Rota`. Publicar rota espera disponibilidade e categoria. Itinerário espera a tela de publicar. O protótipo da #20 é o contrato visual da #21.

O app `Rota` e as regras de data, horário, nome único e ordem de parada ficam nos ADRs 017 a 020, cada um no PR da sua issue. Este registro não cria model, URL nem migration.

Fora das cinco issues: editar e apagar disponibilidade, categoria pela porta da frente, e limite de vagas pela capacidade do veículo.

## Desafios

A `main` local precisa ser atualizada antes de cada branch (`git pull origin main`). O hash do ADR só existe depois do primeiro commit, por isso o segundo commit é só essa linha. As issues #14 a #19 são pull requests antigos; a numeração nova começa na #20. Os arquivos de ADR seguem outra sequência: 013 e 014 já estão na `main`, e a operação começa no 015.

## Status

Adotado. Issues #20 a #24 abertas, com assignee e dependência no corpo.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência).

## Commit

A preencher no commit que versionar este arquivo.
