from flask import Blueprint, render_template, request, redirect, session, current_app
import re
from lab5 import db_connect, db_close
from werkzeug.security import generate_password_hash, check_password_hash

rgz = Blueprint('rgz', __name__)


@rgz.route('/rgz/')
def main():
    """Главная страница РГЗ"""
    return render_template('rgz/books.html', login=session.get('login'))

@rgz.route('/rgz/json-rpc-api/', methods=['POST'])
def api():
    """JSON-RPC API"""
    data = request.json
    id = data.get('id')
    method = data.get('method')
    
    if method == 'get_books':
        conn, cur = db_connect()
        
        # Получаем параметры
        params_data = data.get('params', {})
        title = params_data.get('title', '').strip()
        author = params_data.get('author', '').strip()
        publisher = params_data.get('publisher', '').strip()
        min_pages = params_data.get('min_pages')
        max_pages = params_data.get('max_pages')
        sort_by = params_data.get('sort_by', 'id')
        sort_order = params_data.get('sort_order', 'asc')
        page = params_data.get('page', 1)
        limit = 20
        
        # Строим базовый запрос
        if current_app.config['DB_TYPE'] == 'postgres':
            query = "SELECT * FROM rgz_books WHERE 1=1"
        else:
            query = "SELECT * FROM rgz_books WHERE 1=1"
        
        params = []
        
        # Фильтрация по названию
        if title:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND title ILIKE %s"
            else:
                query += " AND title LIKE ?"
            params.append(f"%{title}%")
        
        # Фильтрация по автору
        if author:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND author ILIKE %s"
            else:
                query += " AND author LIKE ?"
            params.append(f"%{author}%")
        
        # Фильтрация по издательству
        if publisher:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND publisher ILIKE %s"
            else:
                query += " AND publisher LIKE ?"
            params.append(f"%{publisher}%")
        
        # Фильтрация по количеству страниц
        if min_pages:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND pages >= %s"
            else:
                query += " AND pages >= ?"
            params.append(int(min_pages))
        
        if max_pages:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND pages <= %s"
            else:
                query += " AND pages <= ?"
            params.append(int(max_pages))
        
        # Проверяем и валидируем параметры сортировки
        allowed_sort_fields = ['id', 'title', 'author', 'pages', 'publisher']
        if sort_by not in allowed_sort_fields:
            sort_by = 'id'  # значение по умолчанию
        
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'  # значение по умолчанию
        
        # Для PostgreSQL нужно экранировать имя поля
        if current_app.config['DB_TYPE'] == 'postgres':
            # Экранируем имя поля для безопасности
            if sort_by == 'id':
                query += f" ORDER BY id {sort_order}"
            elif sort_by == 'title':
                query += f" ORDER BY title {sort_order}"
            elif sort_by == 'author':
                query += f" ORDER BY author {sort_order}"
            elif sort_by == 'pages':
                query += f" ORDER BY pages {sort_order}"
            elif sort_by == 'publisher':
                query += f" ORDER BY publisher {sort_order}"
        else:
            # Для SQLite используем параметризованный запрос
            query += f" ORDER BY {sort_by} {sort_order}"
        
        # Пагинация
        offset = (page - 1) * limit
        if current_app.config['DB_TYPE'] == 'postgres':
            query += " LIMIT %s OFFSET %s"
        else:
            query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        print(f"SQL запрос: {query}")
        print(f"Параметры: {params}")
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        books = []
        for row in rows:
            books.append({
                'id': row['id'],
                'title': row['title'],
                'author': row['author'],
                'pages': row['pages'],
                'publisher': row['publisher'],
                'image': f"/static/rgz/{row['id']}.jpg"
            })
        
        # Получаем общее количество для пагинации
        count_query = "SELECT COUNT(*) AS cnt FROM rgz_books WHERE 1=1"
        count_params = []
        
        if title:
            if current_app.config['DB_TYPE'] == 'postgres':
                count_query += " AND title ILIKE %s"
            else:
                count_query += " AND title LIKE ?"
            count_params.append(f"%{title}%")
        
        if author:
            if current_app.config['DB_TYPE'] == 'postgres':
                count_query += " AND author ILIKE %s"
            else:
                count_query += " AND author LIKE ?"
            count_params.append(f"%{author}%")
        
        if publisher:
            if current_app.config['DB_TYPE'] == 'postgres':
                count_query += " AND publisher ILIKE %s"
            else:
                count_query += " AND publisher LIKE ?"
            count_params.append(f"%{publisher}%")
        
        if min_pages:
            if current_app.config['DB_TYPE'] == 'postgres':
                count_query += " AND pages >= %s"
            else:
                count_query += " AND pages >= ?"
            count_params.append(int(min_pages))
        
        if max_pages:
            if current_app.config['DB_TYPE'] == 'postgres':
                count_query += " AND pages <= %s"
            else:
                count_query += " AND pages <= ?"
            count_params.append(int(max_pages))
        
        cur.execute(count_query, count_params)
        count_row = cur.fetchone()
        total = count_row['cnt'] if count_row else 0
        
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': {
                'books': books,
                'total': total,
                'page': page,
                'total_pages': (total + limit - 1) // limit
            },
            'id': id
        }
    
    #вход
    if method == 'login':
        login = data['params']['login']
        password = data['params']['password']
        
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM rgz_users WHERE login = %s AND password = %s", (login, password))
        else:
            cur.execute("SELECT * FROM rgz_users WHERE login = ? AND password = ?", (login, password))
        
        row = cur.fetchone()
        db_close(conn, cur)
        
        if row:
            session['login'] = row['login']
            session['is_admin'] = bool(row['is_admin'])
            return {
                'jsonrpc': '2.0',
                'result': {
                    'login': row['login'],
                    'is_admin': bool(row['is_admin'])
                },
                'id': id
            }
        else:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 1,
                    'message': 'Неверный логин или пароль'
                },
                'id': id
            }
    
    #регистрация
    if method == 'register':
        login = data['params']['login']
        password = data['params']['password']
        
        #валидация логина
        if not re.match(r'^[a-zA-Z0-9._-]+$', login):
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Логин должен содержать только латинские буквы, цифры и знаки ._-'
                },
                'id': id
            }
        
        if len(login) < 3 or len(login) > 50:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Логин должен быть от 3 до 50 символов'
                },
                'id': id
            }
        
        #валидация пароля
        if len(password) < 6:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 5,
                    'message': 'Пароль должен быть не менее 6 символов'
                },
                'id': id
            }
        
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$', password):
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 6,
                    'message': 'Пароль содержит недопустимые символы'
                },
                'id': id
            }
        
        conn, cur = db_connect()
        
        # Проверяем, есть ли уже такой пользователь
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id FROM rgz_users WHERE login = %s", (login,))
        else:
            cur.execute("SELECT id FROM rgz_users WHERE login = ?", (login,))
        
        if cur.fetchone():
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 7,
                    'message': 'Пользователь с таким логином уже существует'
                },
                'id': id
            }
        
        # Создаем пользователя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "INSERT INTO rgz_users (login, password, is_admin) VALUES (%s, %s, %s)",
                (login, password, False)
            )
        else:
            cur.execute(
                "INSERT INTO rgz_users (login, password, is_admin) VALUES (?, ?, ?)",
                (login, password, 0)
            )
        
        conn.commit()
        db_close(conn, cur)
        
        # Автоматически входим
        session['login'] = login
        session['is_admin'] = False
        
        return {
            'jsonrpc': '2.0',
            'result': {
                'login': login,
                'is_admin': False
            },
            'id': id
        }
    
    #выход
    if method == 'logout':
        session.pop('login', None)
        session.pop('is_admin', None)
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    #удаление аккаунта
    if method == 'delete_account':
        login = session.get('login')
        if not login:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 8,
                    'message': 'Не авторизован'
                },
                'id': id
            }
        
        conn, cur = db_connect()
        
        #админа удалить нельзя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT is_admin FROM rgz_users WHERE login = %s", (login,))
        else:
            cur.execute("SELECT is_admin FROM rgz_users WHERE login = ?", (login,))
        
        row = cur.fetchone()
        if row and bool(row['is_admin']):
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 9,
                    'message': 'Нельзя удалить администратора'
                },
                'id': id
            }
        
        #удаление пользователя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("DELETE FROM rgz_users WHERE login = %s", (login,))
        else:
            cur.execute("DELETE FROM rgz_users WHERE login = ?", (login,))
        
        conn.commit()
        db_close(conn, cur)
        
        session.pop('login', None)
        session.pop('is_admin', None)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    #информация о пользователе
    if method == 'get_user_info':
        login = session.get('login')
        is_admin = session.get('is_admin', False)
        
        return {
            'jsonrpc': '2.0',
            'result': {
                'is_authenticated': bool(login),
                'login': login,
                'is_admin': is_admin
            },
            'id': id
        }
    
    #админ добавляет книги
    if method == 'add_book':
        login = session.get('login')
        is_admin = session.get('is_admin', False)
        
        if not login:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 10,
                    'message': 'Не авторизован'
                },
                'id': id
            }
        
        if not is_admin:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 11,
                    'message': 'Только для администратора'
                },
                'id': id
            }
        
        title = data['params']['title']
        author = data['params']['author']
        pages = int(data['params']['pages'])
        publisher = data['params']['publisher']
        
        if pages <= 0:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 12,
                    'message': 'Количество страниц должно быть положительным'
                },
                'id': id
            }
        
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "INSERT INTO rgz_books (title, author, pages, publisher) VALUES (%s, %s, %s, %s)",
                (title, author, pages, publisher)
            )
        else:
            cur.execute(
                "INSERT INTO rgz_books (title, author, pages, publisher) VALUES (?, ?, ?, ?)",
                (title, author, pages, publisher)
            )
        
        conn.commit()
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    #админ удаляет книги
    if method == 'delete_book':
        login = session.get('login')
        is_admin = session.get('is_admin', False)
        
        if not login:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 10,
                    'message': 'Не авторизован'
                },
                'id': id
            }
        
        if not is_admin:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 11,
                    'message': 'Только для администратора'
                },
                'id': id
            }
        
        book_id = data['params']
        
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("DELETE FROM rgz_books WHERE id = %s", (book_id,))
        else:
            cur.execute("DELETE FROM rgz_books WHERE id = ?", (book_id,))
        
        conn.commit()
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    #админ редактирует книги
    if method == 'update_book':
        login = session.get('login')
        is_admin = session.get('is_admin', False)
        
        if not login:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 10,
                    'message': 'Не авторизован'
                },
                'id': id
            }
        
        if not is_admin:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 11,
                    'message': 'Только для администратора'
                },
                'id': id
            }
        
        book_id = data['params']['id']
        title = data['params']['title']
        author = data['params']['author']
        pages = int(data['params']['pages'])
        publisher = data['params']['publisher']
        
        if pages <= 0:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 12,
                    'message': 'Количество страниц должно быть положительным'
                },
                'id': id
            }
        
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "UPDATE rgz_books SET title = %s, author = %s, pages = %s, publisher = %s WHERE id = %s",
                (title, author, pages, publisher, book_id)
            )
        else:
            cur.execute(
                "UPDATE rgz_books SET title = ?, author = ?, pages = ?, publisher = ? WHERE id = ?",
                (title, author, pages, publisher, book_id)
            )
        
        conn.commit()
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    #метод не найден
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }


@rgz.route('/rgz/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('rgz/register.html')  # твоя форма регистрации

    # POST: обработка формы
    login = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()

    # Простейшая валидация
    if not login or not password:
        return render_template('rgz/register.html', error='Заполните все поля')

    # Здесь можно вызвать ту же логику, что и в JSON-RPC методе 'register'
    from flask import current_app
    conn, cur = db_connect()
    
    # Проверяем, есть ли уже такой пользователь
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM rgz_users WHERE login = %s", (login,))
    else:
        cur.execute("SELECT id FROM rgz_users WHERE login = ?", (login,))
    
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('rgz/register.html', error='Пользователь с таким логином уже существует')
    
    # Хэшируем пароль
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(password)
    
    # Добавляем пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(
            "INSERT INTO rgz_users (login, password, is_admin) VALUES (%s, %s, %s)",
            (login, hashed_password, False)
        )
    else:
        cur.execute(
            "INSERT INTO rgz_users (login, password, is_admin) VALUES (?, ?, ?)",
            (login, hashed_password, 0)
        )
    conn.commit()
    db_close(conn, cur)

    # Авто-вход
    session['login'] = login
    session['is_admin'] = False
    return redirect('/rgz/')


#вход
@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('rgz/login.html')

    login = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()

    if not login or not password:
        return render_template('rgz/login.html', error='Заполните все поля')

    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM rgz_users WHERE login=%s", (login,))
    else:
        cur.execute("SELECT * FROM rgz_users WHERE login=?", (login,))
    user = cur.fetchone()
    db_close(conn, cur)

    if not user or not check_password_hash(user['password'], password):
        return render_template('rgz/login.html', error='Логин и/или пароль неверны')

    session['login'] = login
    session['is_admin'] = bool(user['is_admin'])
    return redirect('/rgz/')

@rgz.route('/rgz/logout')
def logout_page():
    session.pop('login', None)
    session.pop('is_admin', None)
    return redirect('/rgz/')


@rgz.route('/rgz/delete_account')
def delete_account_page():
    login = session.get('login')
    if not login:
        return redirect('/rgz/login')

    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT is_admin FROM rgz_users WHERE login=%s", (login,))
    else:
        cur.execute("SELECT is_admin FROM rgz_users WHERE login=?", (login,))
    user = cur.fetchone()
    if user and not bool(user['is_admin']):
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("DELETE FROM rgz_users WHERE login=%s", (login,))
        else:
            cur.execute("DELETE FROM rgz_users WHERE login=?", (login,))
        conn.commit()
    db_close(conn, cur)

    session.pop('login', None)
    session.pop('is_admin', None)
    return redirect('/rgz/')