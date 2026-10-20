# ADR 013 — MVVM não entra no embarque nem no CRUD atual

## Contexto

O rascunho circulado como “ADR 006 — Não adoção de MVVM” descrevia uma tela de ponto de embarque: endereço do paciente, condição de mobilidade, raio permitido e uma classe `EmbarqueViewModel` com `embarque_label`, `dentro_do_raio` e `aviso_raio`. Esse número já está ocupado pela decisão de polimorfismo. A tela também não existe neste repositório.

Busca no código e na documentação: zero ocorrências de embarque, paciente, endereço, raio, coleta ou ViewModel. O app instalado é só `Veiculo`. A apresentação segue o MVT da ADR 003: a view monta um contexto curto e o template Bootstrap só exibe.

Evidência em `Veiculo/views.py`:

```python
def lista_veiculos(request):
    veiculos = Veiculo.objects.all()
    return render(request, "Veiculo/lista.html", {"veiculos": veiculos})
```

O mesmo desenho vale para criar, editar e apagar: `VeiculoForm` e `render` com `{"form": form}` ou `{"veiculo": veiculo}`. Não há camada entre a view e o template.

A história de disponibilidade do veículo (data, horário, vagas) também não está implementada. `capacidade` é um campo do model, não uma agenda.

## Decisão

**Não aplicar MVVM agora. Não criar `EmbarqueViewModel`.**

Seguimos o MVT do Django já adotado na ADR 003. A view prepara o contexto. O template apresenta. Regra de negócio não vai para o HTML.

Quando a preparação de uma tela crescer — rótulos, avisos, o mesmo bloco em mais de uma view — o primeiro passo é uma função que devolve o dicionário de contexto, testável sem `render`. Isso continua MVT. Vira ViewModel só se essa preparação for estado de tela reutilizado e a view ficar difícil de testar.

Disponibilidade (data, horário, vagas), quando for construída, entra como model, `ModelForm` e view, no mesmo desenho do cadastro de veículo. Não como ViewModel.

## Alternativa descartada

Criar `EmbarqueViewModel` “para ter o padrão”, ou forçar MVVM na lista e no formulário de veículo.

Sem a tela de embarque, a classe não teria consumidor. No Django com template no servidor, o papel do ViewModel já é o contexto que a view passa ao `render`. Uma classe extra só aumentaria um conceito para a equipe manter, em troca de um benefício que o código atual não pede.

## Consequência

Nenhum módulo de ViewModel neste ciclo. `Veiculo/views.py` continua montando o contexto. Os templates em `Veiculo/templates/Veiculo/` continuam sem validar embarque, raio ou mobilidade — porque essa regra ainda não existe.

O custo é que rótulos de tela, quando surgirem, nascem na view. O ganho é não abrir uma camada que a ADR 012 já recusou para Service enquanto as views forem CRUD simples.

## Desafios

Não confundir “não agora” com “nunca”. Este ADR se revisita se:

- a preparação dos dados de uma tela ficar extensa ou difícil de testar sem renderizar HTML;
- a mesma lógica de apresentação precisar ser compartilhada por várias views;
- a view passar a misturar regra de negócio e rótulo de tela.

O sinal de alerta antes disso é condicional de negócio dentro do template. Nesse caso, a correção é trazer a regra para a view ou para uma função, não adotar MVVM no mesmo dia.

## Status

Adotado como decisão negativa em 2026-10-20. Não implementa código.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência). A evidência foi conferida no código do repositório: o rascunho anterior citava uma view de embarque que não existe.
