"""Testa a conexão configurada em DATABASE_URL/.env sem alterar dados."""
from sqlalchemy import text
from app import app, db

with app.app_context():
    try:
        db.session.execute(text("SELECT 1"))
        print("Conexão com o banco: OK")
        print(f"Dialect SQLAlchemy: {db.engine.dialect.name}")
        print(f"Banco/servidor: {db.engine.url.host or 'arquivo local'} / {db.engine.url.database}")
        if db.engine.dialect.name == "sqlite":
            print("ATENÇÃO: a aplicação está usando SQLite, não MySQL. Confira o arquivo .env e DATABASE_URL.")
        elif db.engine.dialect.name == "mysql":
            print("A aplicação está conectada ao MySQL.")
    except Exception as exc:
        db.session.rollback()
        print("Falha ao conectar com o banco.")
        print("Confira o serviço MySQL, banco, usuário, senha, porta e DATABASE_URL no .env.")
        print(f"Detalhe técnico: {exc}")
        raise SystemExit(1)
