from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# Configuração inicial
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Banco de dados
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        flash('Erro ao conectar ao banco de dados', 'error')
        app.logger.error(f"Erro MySQL: {err}")
        return None

# Rotas de autenticação
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
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('E-mail já cadastrado', 'error')
                    return redirect(url_for('login'))

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

# Rotas principais
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/clima')
def pagina_clima():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Rotas de favoritos
@app.route('/favoritar', methods=['POST'])
def favoritar():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Não logado'}), 401

    cidade = request.json.get('cidade')
    if not cidade or cidade == "São Paulo":
        return jsonify({'erro': 'Cidade inválida'}), 400

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM favoritos WHERE usuario_id = %s AND cidade = %s",
                    (session['usuario_id'], cidade)
                )
                if cursor.fetchone():
                    return jsonify({'erro': 'Cidade já favoritada'}), 400

                cursor.execute(
                    "INSERT INTO favoritos (usuario_id, cidade) VALUES (%s, %s)",
                    (session['usuario_id'], cidade)
                )
                conn.commit()
                return jsonify({'sucesso': True}), 200
        finally:
            conn.close()
    return jsonify({'erro': 'Erro no servidor'}), 500

@app.route('/remover_favorito', methods=['POST'])
def remover_favorito():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    cidade = request.form.get('cidade')
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM favoritos WHERE usuario_id = %s AND cidade = %s",
                    (session['usuario_id'], cidade)
                )
                conn.commit()
                flash('Cidade removida dos favoritos!', 'success')
        finally:
            conn.close()
    return redirect(url_for('listar_favoritos'))

@app.route('/favoritos')
def listar_favoritos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT cidade FROM favoritos WHERE usuario_id = %s",
                    (session['usuario_id'],)
                )
                favoritos = cursor.fetchall()
                return render_template('favoritos.html', favoritos=favoritos)
        finally:
            conn.close()
    flash('Erro ao carregar favoritos', 'error')
    return redirect(url_for('pagina_clima'))

if __name__ == '__main__':
    app.run(debug=True)
