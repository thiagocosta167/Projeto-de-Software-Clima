from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

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
        app.logger.error(f"Erro MySQL: {err}")
        return None

@app.route('/login', methods=['GET','POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('pagina_clima'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
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
        else:
            flash('Erro ao conectar ao banco de dados', 'error')
    return render_template('login.html')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    if 'usuario_id' in session:
        return redirect(url_for('pagina_clima'))
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    confirmar_senha = request.form['confirmar_senha']
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
    else:
        flash('Erro ao conectar ao banco de dados', 'error')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/clima')
def pagina_clima():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/favoritar', methods=['POST'])
def favoritar():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Não logado'}), 401

    cidade = request.json.get('cidade')
    if not cidade:
        return jsonify({'erro': 'Cidade inválida'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'erro': 'Erro de conexão com o banco de dados'}), 500

    try:
        with conn.cursor() as cursor:
            
            cursor.execute(
                "SELECT id FROM favoritos WHERE usuario_id = %s AND cidade = %s",
                (session['usuario_id'], cidade)
            )
            if cursor.fetchone():
                return jsonify({'erro': f'"{cidade}" já está favoritada.'}), 409

            
            cursor.execute(
                "INSERT INTO favoritos (usuario_id, cidade) VALUES (%s, %s)",
                (session['usuario_id'], cidade)
            )
            conn.commit()
            return jsonify({'sucesso': True, 'mensagem': f'"{cidade}" foi adicionada aos favoritos!'}), 201
    except mysql.connector.Error as err:
        app.logger.error(f"Erro ao favoritar: {err}")
        return jsonify({'erro': 'Erro interno do servidor ao favoritar.'}), 500
    finally:
        conn.close()

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
        except mysql.connector.Error as err:
            app.logger.error(f"Erro ao remover favorito: {err}")
            flash('Erro ao remover favorito', 'error')
        finally:
            conn.close()
    else:
        flash('Erro ao conectar ao banco de dados', 'error')
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
        except mysql.connector.Error as err:
            app.logger.error(f"Erro ao carregar favoritos: {err}")
            flash('Erro ao carregar favoritos', 'error')
        finally:
            conn.close()
    else:
        flash('Erro ao conectar ao banco de dados', 'error')
    return redirect(url_for('pagina_clima'))

@app.route('/historico', methods=['GET', 'POST'])
def historico():
    if 'usuario_id' not in session:
        if request.method == 'POST':
            return jsonify({'erro': 'Não logado'}), 401
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        if request.method == 'POST':
            return jsonify({'erro': 'Erro de conexão com o banco de dados'}), 500
        flash('Erro ao conectar ao banco de dados', 'error')
        return redirect(url_for('pagina_clima'))

    try:
        with conn.cursor(dictionary=True) as cursor:
            if request.method == 'POST':
                cidade = request.json.get('cidade')
                if not cidade:
                    return jsonify({'erro': 'Cidade inválida'}), 400
                
           
                cursor.execute(
                    "SELECT id FROM historico_buscas WHERE usuario_id = %s AND cidade = %s ORDER BY data_busca DESC LIMIT 1",
                    (session['usuario_id'], cidade)
                )
                recent_search = cursor.fetchone()
                
             
                if recent_search:
                    return jsonify({'sucesso': True, 'mensagem': 'Cidade já no histórico recente'}), 200 # Não insere novamente
                
                cursor.execute(
                    "INSERT INTO historico_buscas (usuario_id, cidade) VALUES (%s, %s)",
                    (session['usuario_id'], cidade)
                )
                conn.commit()
                return jsonify({'sucesso': True}), 200
            else: # GET request
                cursor.execute(
                    "SELECT id, cidade, data_busca FROM historico_buscas WHERE usuario_id = %s ORDER BY data_busca DESC",
                    (session['usuario_id'],)
                )
                historico_buscas = cursor.fetchall()
                return render_template('historico.html', historico=historico_buscas)
    except mysql.connector.Error as err:
        app.logger.error(f"Erro geral no histórico: {err}")
        flash('Erro ao carregar histórico', 'error')
        return redirect(url_for('pagina_clima'))
    finally:
        conn.close()

@app.route('/remover_historico', methods=['POST'])
def remover_historico():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    busca_id = request.form.get('id')
    if not busca_id:
        flash('ID da busca inválido', 'error')
        return redirect(url_for('historico'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM historico_buscas WHERE id = %s AND usuario_id = %s",
                    (busca_id, session['usuario_id'])
                )
                conn.commit()
                flash('Busca removida do histórico!', 'success')
        except mysql.connector.Error as err:
            app.logger.error(f"Erro ao remover do histórico: {err}")
            flash('Erro ao remover do histórico', 'error')
        finally:
            conn.close()
    else:
        flash('Erro ao conectar ao banco de dados', 'error')
    return redirect(url_for('historico'))


if __name__ == '__main__':
    app.run(debug=True)
