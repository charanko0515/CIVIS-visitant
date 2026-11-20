from flask import Flask, request, render_template, redirect, session as sessao, jsonify, flash
import os

import adm_db as db

app = Flask(__name__)
app.secret_key = "civis_chave_secreta"

MODO_SOMENTE_LEITURA = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.context_processor
def injetar_usuario():
    return {
        "nome_usuario": sessao.get("nome_usuario"),
        "modo_somente_leitura": MODO_SOMENTE_LEITURA,
    }


# =========================
# PÁGINAS
# =========================
@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/denuncia")
def denuncia():
    ocorrencias = db.buscar_ocorrencias()
    return render_template("denuncia.html", ocorrencias=ocorrencias)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/feed")
def feed():
    if not sessao.get("usuario_id"):
        return redirect("/login")

    denuncias, ups_dados = db.buscar_feed_dados(sessao["usuario_id"])
    return render_template("feed.html", denuncias=denuncias, ups_dados=ups_dados)


@app.route("/perfil")
def perfil():
    if not sessao.get("usuario_id"):
        return redirect("/login")

    usuario, denuncias = db.buscar_perfil_dados(sessao["usuario_id"])
    if not usuario:
        sessao.clear()
        return redirect("/login")
    return render_template("perfil.html", usuario=usuario, denuncias=denuncias)


# =========================
# CADASTRO DE USUÁRIO (BLOQUEADO)
# =========================
@app.route("/cadastro", methods=["POST"])
def cadastrar_usuario_rota():
    flash("O cadastro de novos usuários está desabilitado nesta versão.", "warning")
    return redirect("/cadastro")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def fazer_login():
    cpf = request.form.get("cpf", "").replace(".", "").replace("-", "").strip()
    senha = request.form.get("senha")

    usuario = db.verificar_login(cpf, senha)
    if usuario:
        sessao["nome_usuario"] = usuario[2]
        sessao["usuario_id"] = usuario[0]
        return redirect("/feed")
    flash("CPF ou senha inválidos.", "danger")
    return redirect("/login")


# =========================
# RECEBER DENÚNCIA / UPLOAD (BLOQUEADO)
# =========================
@app.route("/receber_denuncia", methods=["POST"])
def receber_denuncia():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "ok": False,
            "erro": "Envio de novas denúncias e uploads desabilitado."
        }), 403

    flash("O envio de novas denúncias e uploads está desabilitado nesta versão.", "warning")
    return redirect("/denuncia")


# =========================
# UP EM DENÚNCIA (BLOQUEADO)
# =========================
@app.route("/up/<int:denuncia_id>", methods=["POST"])
def dar_up(denuncia_id):
    if not sessao.get("usuario_id"):
        return redirect("/login")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "ok": False,
            "bloqueado": True,
            "mensagem": "Função de up desabilitada nesta versão."
        }), 403

    flash("A função de up está desabilitada nesta versão.", "warning")
    return redirect("/feed")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    sessao.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)