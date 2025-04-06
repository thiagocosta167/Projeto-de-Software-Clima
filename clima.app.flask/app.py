from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Flask com caminho absoluto para templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv('SECRET_KEY')

# Configuração do Banco de Dados
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        flash('Erro ao conectar ao banco de dados', 'error')
        app.logger.error(f"Erro MySQL: {err}")
        return None

# Rotas de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('pagina_clima'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT id, senha FROM usuarios WHERE email = %s", (email,))
                    user = cursor.fetchone()

                    if user and check_password_hash(user['senha'], senha):
                        session['usuario_id'] = user['id']
                        return redirect(url_for('pagina_clima'))

                    flash('E-mail ou senha incorretos', 'error')
            finally:
                conn.close()

    return render_template('login.html')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    if 'usuario_id' in session:
        return redirect(url_for('pagina_clima'))

    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')

    if senha != confirmar_senha:
        flash('As senhas não coincidem', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Verifica se email já existe
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('E-mail já cadastrado', 'error')
                    return redirect(url_for('login'))

                # Cria novo usuário
                hashed_pw = generate_password_hash(senha)
                cursor.execute(
                    "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
                    (nome, email, hashed_pw)
                )
                conn.commit()
                flash('Cadastro realizado com sucesso! Faça login.', 'success')
        except mysql.connector.Error as err:
            app.logger.error(f"Erro no cadastro: {err}")
            flash('Erro no cadastro', 'error')
        finally:
            conn.close()

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rotas Principais
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/clima')
def pagina_clima():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
