from flask import Blueprint, render_template, request, make_response, redirect, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path
lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login = session.get('login'))
def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host = '127.0.0.1',
            database = 'egor_khobenkov_knowledge_base',
            user = 'egor_khobenkov_knowledge_base',
            password = '123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    return conn, cur


def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    
    login = request.form.get('login')
    password = request.form.get('password')
    full_name = request.form.get('full_name', '')

    if not (login and password):
        return render_template('lab5/register.html', error='Заполните все поля')
    
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html',
                               error = "Такой пользователь уже существует")
    
    password_hash = generate_password_hash(password)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password, full_name) VALUES (%s, %s, %s);", 
                    (login, password_hash, full_name))
    else:
        cur.execute("INSERT INTO users (login, password, full_name) VALUES (?, ?, ?);", 
                    (login, password_hash, full_name))

    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)


@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('/lab5/login.html', error = 'Заполните поля')
    
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login =%s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login =?;", (login,))
    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error = 'Логин и/или пароль неверны')
    
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error = 'Логин и/или пароль неверны')

    session['login'] = login
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login = login)


@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    is_favorite = request.form.get('is_favorite') == 'on'

    if not title or not article_text:
        error_msg = ""
        if not title and not article_text:
            error_msg = "Заполните название и текст статьи"
        elif not title:
            error_msg = "Заполните название статьи"
        elif not article_text:
            error_msg = "Заполните текст статьи"
        
        return render_template('lab5/create_article.html', error=error_msg, title=title, article_text=article_text)

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login,))
    login_id = cur.fetchone()["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO articles(user_id, title, article_text) \
                VALUES (%s, %s, %s);", (login_id, title, article_text))
    else:
        cur.execute("INSERT INTO articles(user_id, title, article_text) \
                VALUES (?, ?, ?);", (login_id, title, article_text))
    
    db_close(conn, cur)
    return redirect('/lab5')


@lab5.route('/lab5/list')
def list_articles():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    if not user:
        db_close(conn, cur)
        return redirect('/lab5/login')
    
    user_id = user["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE user_id=%s ORDER BY is_favorite DESC, id DESC;", (user_id,))
    else:
        cur.execute("SELECT * FROM articles WHERE user_id=? ORDER BY is_favorite DESC, id DESC;", (user_id,))

    articles = cur.fetchall()
    db_close(conn, cur)
    return render_template('/lab5/articles.html', articles=articles)


@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab5')


@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    if not user:
        db_close(conn, cur)
        return redirect('/lab5/login')
    
    user_id = user["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE id=%s AND user_id=%s;", (article_id, user_id))
    else:
        cur.execute("SELECT * FROM articles WHERE id=? AND user_id=?;", (article_id, user_id))
    
    article = cur.fetchone()
    
    if not article:
        db_close(conn, cur)
        return redirect('/lab5/list')

    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article)

    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    is_favorite = request.form.get('is_favorite') == 'on'

    if not title or not article_text:
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article, error='Заполните название и текст статьи')

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE articles SET title=%s, article_text=%s, is_public=%s, is_favorite=%s WHERE id=%s AND user_id=%s;",
                    (title, article_text, is_public, is_favorite, article_id, user_id))
    else:
        cur.execute("UPDATE articles SET title=?, article_text=?, is_public=?, is_favorite=? WHERE id=? AND user_id=?;",
                    (title, article_text, is_public, is_favorite, article_id, user_id))

    db_close(conn, cur)
    return redirect('/lab5/list')


@lab5.route('/lab5/public')
def public_articles():
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT a.*, u.login as author FROM articles a JOIN users u ON a.user_id = u.id WHERE a.is_public = true ORDER BY a.is_favorite DESC, a.id DESC;")
    else:
        cur.execute("SELECT a.*, u.login as author FROM articles a JOIN users u ON a.user_id = u.id WHERE a.is_public = 1 ORDER BY a.is_favorite DESC, a.id DESC;")

    articles = cur.fetchall()
    db_close(conn, cur)
    
    login = session.get('login')
    return render_template('lab5/public_articles.html', articles=articles, login=login)


@lab5.route('/lab5/delete/<int:article_id>')
def delete_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    
    user = cur.fetchone()
    if not user:
        db_close(conn, cur)
        return redirect('/lab5/login')
    
    user_id = user["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id=%s AND user_id=%s;", (article_id, user_id))
    else:
        cur.execute("DELETE FROM articles WHERE id=? AND user_id=?;", (article_id, user_id))

    db_close(conn, cur)
    return redirect('/lab5/list')


@lab5.route('/lab5/users')
def users_list():
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login, full_name FROM users ORDER BY login;")
    else:
        cur.execute("SELECT login, full_name FROM users ORDER BY login;")
    
    users = cur.fetchall()
    db_close(conn, cur)
    
    login = session.get('login')
    return render_template('lab5/users.html', users=users, login=login)


@lab5.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if request.method == 'GET':
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT full_name FROM users WHERE login=%s;", (login,))
        else:
            cur.execute("SELECT full_name FROM users WHERE login=?;", (login,))
        
        user = cur.fetchone()
        db_close(conn, cur)

        user_data = {'full_name': user['full_name'] if user and user['full_name'] else ''}
        return render_template('lab5/profile.html', user=user_data)

    full_name = request.form.get('full_name')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if new_password and new_password != confirm_password:
        db_close(conn, cur)
        return render_template('lab5/profile.html', 
                               user={'full_name': full_name}, 
                               error='Пароли не совпадают')

    if new_password:
        password_hash = generate_password_hash(new_password)
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET full_name=%s, password=%s WHERE login=%s;",
                        (full_name, password_hash, login))
        else:
            cur.execute("UPDATE users SET full_name=?, password=? WHERE login=?;",
                        (full_name, password_hash, login))
    else:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET full_name=%s WHERE login=%s;",
                        (full_name, login))
        else:
            cur.execute("UPDATE users SET full_name=? WHERE login=?;",
                        (full_name, login))
    
    session['full_name'] = full_name
    db_close(conn, cur)
    return redirect('/lab5/list')