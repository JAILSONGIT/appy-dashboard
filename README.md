# APPY Dashboard — versão revisada

Aplicação de inventário de equipamentos usando Python/Flask, SQLAlchemy, MySQL, HTML/Bootstrap e Gunicorn. Inclui dashboard, cadastro/exclusão, busca por nome/código, filtro por setor, importação Excel, API de produtos, health check, login administrativo simples e proteção CSRF.


## Executar localmente (Windows)
1. Copie `.env.example` para `.env` e configure `SECRET_KEY`, `APPY_ADMIN_USER` e `APPY_ADMIN_PASSWORD`. Não compartilhe nem envie o `.env` ao GitHub.
2. No CMD, na pasta do projeto:
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python app.py
   ```
3. Acesse `http://127.0.0.1:5000/login` e entre usando as credenciais configuradas.
4. Teste `/health`. A API `/api/produtos` exige login.

Por padrão, sem `DATABASE_URL`, usa SQLite local. Para MySQL, consulte scripts em `database/`.

## Docker
Copie `.env.docker.example` para `.env`, altere as senhas e chaves, e execute:
```bash
docker compose up --build -d
```
Acesse `http://localhost:5000/login`. Logs: `docker compose logs -f web`. Parar: `docker compose down`. Não use `down -v` se quiser manter o volume de dados.

## Importar planilha
```bash
python importar_planilha.py inventario.xlsx
```
O padrão acrescenta registros. `--limpar` apaga registros existentes antes da importação; faça backup e valide o arquivo antes.

## Publicar na internet
Consulte `PUBLICAR_GITHUB_RAILWAY.md` para instruções GitHub + Railway + MySQL + domínio HTTPS. O guia detalhado está disponível separadamente como `GUIA_COMPLETO_APPY_Dashboard_Internet.docx`.

## Segurança
Este login é um bloqueio administrativo único, não um sistema corporativo de identidade. Antes de dados reais, implemente usuários e perfis, limite tentativas de login, auditoria, backups e teste de restauração; avalie autorização e LGPD. Não exponha o MySQL publicamente. Configure `COOKIE_SECURE=1` em produção HTTPS e use `SECRET_KEY` forte e exclusiva.
