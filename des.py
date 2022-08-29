from crypt import methods
from sys import unraisablehook
from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect

from flask_login import (current_user, LoginManager,
                         login_user, logout_user,
                         login_required)

import hashlib


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://testeuser:Analog21@localhost:3306/desapegando3d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = 'Analog21@'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Usuario(db.Model):
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    rua = db.Column('usu_rua', db.String(256))
    cidade = db.Column('usu_cidade', db.String(256))
    estado = db.Column('usu_estado', db.String(256))
    cep = db.Column('usu_cep', db.String(256))

    def __init__(self, nome, email, senha, rua, cidade, estado, cep):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.rua = rua
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc


class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id


@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('paginanaoencontrada.html')


@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

# não é possível comparar a senha com
        # a do banco de deixar como era antes agora necessário
        # transformar a senha digitada em hash para comparar com o banco
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()  
        
        user = Usuario.query.filter_by(email=email, senha=senha).first()
        
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/cad/usuario")

def usuario():
    return render_template('usuario.html', usuarios=Usuario.query.all(), titulo="Usuario")


@app.route("/usuario/criar", methods=['POST'])
def novousuario():
    # transforma a senha em um hash com 128 caracteres,  # que guarda diretamente a senha no bancol se utiliza "hash,request.form.get('passwd')"  # que faz a conversão da senha em um hash
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get('nome'), request.form.get('email'), hash, request.form.get('rua'), request.form.get('cidade'), request.form.get('estado'), request.form.get('cep'))  # em vez de utilizar "request.form.get('passwd')"
    
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))


@app.route("/usuario/detalhar/<int:id>")
@login_required # comando para pedir login e senha
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome


@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
@login_required # comando para pedir login e senha
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()  # no alterar transformar em hash mas isso pode dar problema
        usuario.end = request.form.get('rua')
        usuario.end = request.form.get('cidade')
        usuario.end = request.form.get('estado')
        usuario.end = request.form.get('cep')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('eusuario.html', usuario=usuario, titulo="Usuario")


@app.route("/usuario/deletar/<int:id>")
@login_required # comando para pedir login e senha
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))


@app.route("/cad/anuncio")

def anuncio():
    return render_template('anuncio.html', anuncios=Anuncio.query.all(), categorias=Categoria.query.all(), titulo="Anuncio")


@app.route("/anuncio/novo", methods=['POST'])
@login_required # comando para pedir login e senha
def novoanuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'), request.form.get(
        'qtd'), request.form.get('preco'), request.form.get('cat'), request.form.get('uso'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))


@app.route("/anuncios/pergunta")
def pergunta():
    return render_template('pergunta.html')


@app.route("/anuncios/compra")
def compra():
    print("anuncio comprado")
    return ""


@app.route("/anuncio/favoritos")
def favoritos():
    print("favorito inserido")
    return f"<h4>Comprado</h4>"


@app.route("/categoria/novo")
def categoria():
    return render_template('categoria.html', categorias=Categoria.query.all(), titulo='Categoria')


@app.route("/config/novacategoria", methods=['POST'])
@login_required # comando para pedir login e senha
def novacategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))


@app.route("/relatorios/vendas")
def relVendas():
    return render_template('relVendas.html')


@app.route("/relatorios/compras")
def relCompras():
    return render_template('relCompras.html')


if __name__ == 'des':
    print("des")
    db.create_all()
