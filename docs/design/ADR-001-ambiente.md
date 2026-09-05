# ADR 001 — Ambiente de desenvolvimento: WSL2, Ubuntu, venv e Django

## Contexto

O RotaSaúde precisa de um ambiente reproduzível para a equipe (Web III / ILP). O exemplo da disciplina usa `portal` + `saudacao` no Ubuntu. Sem um padrão, cada integrante instala Python no Windows de um jeito diferente e o projeto deixa de rodar igual.

## Decisão

Desenvolver no **WSL2 com Ubuntu**, Python 3 em **venv** (`.venv`) e **Django 5.2**. O projeto Django é `Portal` (settings/urls) e a app do domínio é `Veiculo` — a mesma lógica do exemplo `startproject` / `startapp`, com os nomes do tema.

## Alternativa descartada

Instalar Django só no Windows (Python.org / Store) sem WSL.

O roteiro da disciplina, os caminhos (`~/`, `apt`) e o laboratório da FATEC assumem Ubuntu. Ambiente misto Windows/WSL quebra `venv`, permissão de arquivo e o “funciona na minha máquina”.

## Consequência

Todo mundo sobe o mesmo stack: `source .venv/bin/activate` → `python manage.py runserver`. O custo é depender do WSL no notebook. `.venv` não entra no Git (ver `.gitignore`).

## Desafios

Rede do `pip` no laboratório pode falhar; o roteiro prevê wheels no pendrive. Primeiro `runserver` no WSL às vezes não escuta se a porta já estiver ocupada.

## Commit

`<hash do commit desta branch — cole depois de commitar>`
