# Publicar o APPY Dashboard revisado (GitHub + Railway)

> Antes de publicar: esta versão inclui login de administrador único e CSRF. Ainda não tem gestão de múltiplos usuários, limitação de tentativas de login, auditoria de alterações nem recuperação de senha.

## 1. Preparar o projeto
- Extraia o ZIP revisado para uma pasta local.
- Copie `.env.example` para `.env` somente para desenvolvimento local. Não suba o `.env`.
- Defina `SECRET_KEY` como chave longa e aleatória, `APPY_ADMIN_USER` e `APPY_ADMIN_PASSWORD` como credenciais fortes.
- Confira `.gitignore` e a lista do Git antes de publicar.

## 2. Criar o repositório GitHub
1. Entre em https://github.com e crie um repositório novo, preferencialmente privado.
2. Não inicialize com README se já estiver enviando este projeto.
3. Instale Git for Windows, abra terminal dentro da pasta extraída e execute:
   ```bash
   git init
   git add .
   git status
   ```
4. Confirme que `.env`, planilhas com dados e arquivos de banco não aparecem. Se aparecerem, pare e remova do staging.
5. Faça commit e conecte ao repositório (substitua a URL):
   ```bash
   git commit -m "APPY Dashboard revisado"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/appy-dashboard.git
   git push -u origin main
   ```

## 3. Criar projeto na Railway e banco MySQL
1. Crie uma conta em https://railway.com e conecte ao GitHub.
2. Crie um novo projeto.
3. Adicione um serviço MySQL pelo botão `New`/`Database`/`MySQL`.
4. Aguarde o provisionamento. Não habilite acesso público ao banco.

## 4. Criar serviço web
1. No mesmo projeto Railway, crie um serviço a partir do GitHub Repository.
2. Escolha o repositório `appy-dashboard` e branch `main`.
3. A Railway detecta o `Dockerfile` na raiz e constrói a aplicação. A configuração atual usa Gunicorn.
4. Se necessário, confirme a raiz do projeto: o `Dockerfile`, `requirements.txt` e `app.py` devem estar na raiz de origem selecionada.

## 5. Configurar variáveis (serviço web)
No serviço APPY, abra `Variables` e adicione:
- `DATABASE_URL`: use a referência interna para a URL de conexão do serviço MySQL (escolha a variável de conexão MySQL que a Railway oferece; não cole URL externa e não exponha o banco).
- `SECRET_KEY`: valor aleatório grande, exclusivo para produção.
- `APPY_ADMIN_USER`: usuário administrativo (não use `admin` se possível).
- `APPY_ADMIN_PASSWORD`: senha forte e exclusiva.
- `COOKIE_SECURE`: `1` (o domínio público da Railway usa HTTPS).

Confira as variáveis e aplique/redeploy. Nunca coloque essas credenciais em código, README, GitHub ou mensagens.

## 6. Publicar URL
1. Abra Settings/Networking do serviço web.
2. Gere um domínio público.
3. Aguarde o deploy ficar saudável e abra `https://SEU-DOMINIO/login`.
4. Entre com as credenciais configuradas nas Variables.
5. Teste: dashboard, adicionar produto, buscar, filtrar setor, excluir registro, `/api/produtos` (deve exigir login) e `/health`.

## 7. Dados existentes
O MySQL da Railway começa separado do banco local. Faça exportação/backup do banco de origem e importação para o banco hospedado apenas se tiver autorização para transportar os dados. Teste o importador Excel em uma cópia antes de usar `--limpar`.


## 8. Atualizar a aplicação
Após alterações locais e testes:
```bash
git add .
git commit -m "Descreva a atualização"
git push
```
O serviço conectado ao repositório pode disparar novo deploy automaticamente. Verifique logs e teste novamente.

## 9. Segurança antes de usar com dados reais
- Não usar dados pessoais, de pacientes ou dados institucionais sensíveis sem autorização, avaliação LGPD e controles de acesso apropriados.
- Login simples de administrador único é um primeiro bloqueio, não um sistema corporativo de identidade.
- Implementar controle de tentativas de login, usuários e perfis, auditoria, backup e restauração.
- O MySQL deve ser privado e nunca deve ser exposto diretamente à internet.
- Mantenha segredos exclusivamente nas variáveis do serviço.
