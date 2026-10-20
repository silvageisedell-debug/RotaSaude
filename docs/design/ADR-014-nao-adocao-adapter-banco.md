# ADR 014 — Adapter não entra no acesso ao banco

## Contexto

O rascunho circulado como “ADR 007 — Não adoção do padrão Adapter após a migração para Neon” dizia que o RotaSaúde já tinha saído do SQLite para PostgreSQL/Neon e que a equipe não achou `psycopg`, `connection.cursor` nem `.raw()`. O número 007 já está ocupado pela decisão de não aplicar Strategy. A migração para Neon também não está neste repositório.

Configuração vigente em `Portal/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

`requirements.txt` declara só `Django==5.2.17`. Não há `psycopg`, `DATABASE_URL` nem host de Neon.

O acesso aos dados passa pelo ORM. Em `Veiculo/views.py`: `Veiculo.objects.all()`, `form.save()`, `get_object_or_404(Veiculo, pk=pk)` e `veiculo.delete()`. Não há `cursor`, `.raw()` nem `execute` nas views, forms ou models.

## Decisão

**Não aplicar Adapter no acesso ao banco. Não criar `NeonAdapter` nem repositório paralelo ao ORM.**

A conexão continua em `DATABASES`. As operações de negócio continuam em `Model.objects` e `ModelForm.save()`.

Trocar SQLite por PostgreSQL, se e quando acontecer, é mudança de `ENGINE` (e credenciais fora do código) mais `migrate`. As views não mudam. O backend do Django já traduz a mesma API do ORM para o driver. Um Adapter por cima disso repetiria essa tradução.

O Adapter passa a ser candidato quando o código chamar uma biblioteca ou API de terceiro cuja interface a aplicação não controla e que precise ser traduzida para a nossa — por exemplo geocodificação, CEP ou notificação. A troca de banco, sozinha, não é esse caso.

## Alternativa descartada

Criar uma classe Adapter em volta de `Veiculo.objects` para “isolar” SQLite de um Postgres futuro.

O problema que o padrão resolve não aparece: não há chamada direta a driver com `execute` / `fetchone` para adaptar. A alternativa acrescentaria um módulo sem consumidor e um segundo lugar para errar a mesma operação que o ORM já faz.

## Consequência

Nenhum módulo Adapter neste ciclo. Testes, quando existirem, usam o banco de teste do Django, sem repositório em memória feito para contornar o driver.

O custo é não ter uma camada própria caso alguém passe a abrir `cursor()` espalhado. O ganho é manter um só caminho de persistência, o que já permite trocar o backend na configuração.

## Desafios

Não confundir “não agora” com “nunca”. Este ADR se revisita se:

- views, forms, models ou serviços passarem a chamar o driver direto (`cursor`, `.raw()`, `execute`);
- uma biblioteca externa oferecer uma interface incompatível com a que a aplicação espera;
- trocar uma integração exigir a mesma tradução em vários pontos do código.

Enquanto o acesso for `Veiculo.objects` e `form.save()`, a migração de banco não reabre esta decisão.

## Status

Adotado como decisão negativa em 2026-10-20. Não altera `settings.py` e não implementa código.

## Redação

Texto redigido com apoio de IA, em tom formal e informativo, seguindo as boas práticas de Architecture Decision Record (contexto, decisão, alternativa descartada, consequência). A evidência foi conferida no código do repositório: o rascunho anterior afirmava migração para Neon que o `DATABASES` atual não contém.
