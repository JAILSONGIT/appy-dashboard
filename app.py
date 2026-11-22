"""APPY Dashboard: inventário de equipamentos com Flask e SQLAlchemy."""
import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import hmac

BASE_DIR = Path(__file__).resolve().parent
# Carrega variáveis do arquivo .env, sem substituir variáveis já definidas no sistema.
load_dotenv(BASE_DIR / ".env")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave-local-appy-trocar-em-producao")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0") == "1"
csrf = CSRFProtect(app)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = os.getenv("APPY_ADMIN_USER", "admin")
        password = os.getenv("APPY_ADMIN_PASSWORD", "")
        supplied_user = request.form.get("username", "")
        supplied_password = request.form.get("password", "")
        if password and hmac.compare_digest(supplied_user, user) and hmac.compare_digest(supplied_password, password):
            session.clear()
            session["authenticated"] = True
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("dashboard"))
        flash("Usuário ou senha inválidos. Configure APPY_ADMIN_USER e APPY_ADMIN_PASSWORD.", "danger")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))
db_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'appy.db'}").strip()
if db_url.startswith("mysql://"):
    # Garante o driver PyMySQL mesmo se a URL antiga começar apenas com mysql://.
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
app.config.update(
    SQLALCHEMY_DATABASE_URI=db_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
)
db = SQLAlchemy(app)


class Produto(db.Model):
    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.Integer, nullable=True, index=True)
    nome = db.Column(db.String(255), nullable=False, index=True)
    entradas = db.Column(db.Integer, default=0, nullable=False)
    devolvido = db.Column(db.Integer, default=0, nullable=False)
    nao_devolvido = db.Column(db.Integer, default=0, nullable=False)
    reformar = db.Column(db.Integer, default=0, nullable=False)
    estoque = db.Column(db.Integer, default=0, nullable=False)
    descarte = db.Column(db.Integer, default=0, nullable=False)
    setor = db.Column(db.String(120), default="INTERLAGOS", nullable=False)

    def to_dict(self):
        return {"id": self.id, "codigo": self.codigo, "nome": self.nome, "setor": self.setor,
                "entradas": self.entradas, "devolvido": self.devolvido,
                "nao_devolvido": self.nao_devolvido, "reformar": self.reformar,
                "estoque": self.estoque, "descarte": self.descarte}


def inteiro_formulario(campo, padrao=0):
    valor = request.form.get(campo, "")
    if valor.strip() == "":
        return padrao
    numero = int(valor)
    if numero < 0:
        raise ValueError(f"O campo {campo} não pode ser negativo.")
    return numero


@app.route("/")
@login_required
def dashboard():
    termo = request.args.get("q", "").strip()
    setor = request.args.get("setor", "").strip()
    query = Produto.query
    if termo:
        query = query.filter(or_(Produto.nome.ilike(f"%{termo}%"),
                                 db.cast(Produto.codigo, db.String).ilike(f"%{termo}%")))
    if setor:
        query = query.filter(Produto.setor == setor)
    produtos = query.order_by(Produto.nome).all()
    def total(campo):
        return db.session.query(func.coalesce(func.sum(campo), 0)).scalar() or 0
    setores = [r[0] for r in db.session.query(Produto.setor).distinct().order_by(Produto.setor).all()]
    totais = {"produtos": Produto.query.count(), "entradas": total(Produto.entradas),
              "devolvido": total(Produto.devolvido), "nao_devolvido": total(Produto.nao_devolvido),
              "reformar": total(Produto.reformar), "estoque": total(Produto.estoque),
              "descarte": total(Produto.descarte)}
    return render_template("dashboard.html", produtos=produtos, totais=totais,
                           setores=setores, termo=termo, setor_selecionado=setor)


@app.route("/produto/novo", methods=["POST"])
@login_required
def novo_produto():
    try:
        nome = request.form.get("nome", "").strip()
        if not nome:
            raise ValueError("Informe o nome do produto.")
        codigo = inteiro_formulario("codigo", None)
        p = Produto(codigo=codigo, nome=nome,
                    entradas=inteiro_formulario("entradas"),
                    devolvido=inteiro_formulario("devolvido"),
                    nao_devolvido=inteiro_formulario("nao_devolvido"),
                    reformar=inteiro_formulario("reformar"),
                    estoque=inteiro_formulario("estoque"),
                    descarte=inteiro_formulario("descarte"),
                    setor=request.form.get("setor", "INTERLAGOS").strip() or "INTERLAGOS")
        db.session.add(p)
        db.session.commit()
        flash("Produto cadastrado com sucesso.", "success")
    except (ValueError, TypeError):
        db.session.rollback()
        flash("Não foi possível cadastrar. Verifique se código e quantidades são inteiros não negativos e se o nome foi preenchido.", "danger")
    return redirect(url_for("dashboard"))


@app.route("/produto/<int:produto_id>/excluir", methods=["POST"])
@login_required
def excluir_produto(produto_id):
    p = db.session.get(Produto, produto_id)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash("Registro excluído.", "success")
    else:
        flash("Produto não encontrado.", "warning")
    return redirect(url_for("dashboard"))


@app.route("/api/produtos")
@login_required
def api_produtos():
    return jsonify([p.to_dict() for p in Produto.query.order_by(Produto.nome).all()])


@app.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify(status="ok", database="connected")
    except Exception:
        db.session.rollback()
        return jsonify(status="error", database="disconnected"), 503


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
