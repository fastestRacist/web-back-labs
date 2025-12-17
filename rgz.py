from flask import Blueprint, render_template, request, redirect, session, current_app
import re
from lab5 import db_connect, db_close
from werkzeug.security import generate_password_hash, check_password_hash

rgz = Blueprint('rgz', __name__)

def create_rgz_tables():
    """Создание таблиц для РГЗ"""
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        # Таблица пользователей
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rgz_users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Таблица книг
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rgz_books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(300) NOT NULL,
                author VARCHAR(200) NOT NULL,
                pages INTEGER NOT NULL,
                publisher VARCHAR(200) NOT NULL,
                logo VARCHAR(300)
            )
        """)
        
        # Добавляем администратора
        admin_password_hashed = generate_password_hash('admin')

        cur.execute("""
            INSERT INTO rgz_users (login, password, is_admin) 
            VALUES ('admin', %s, TRUE)
            ON CONFLICT (login) DO NOTHING
        """, (admin_password_hashed,))

    else:  # SQLite
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rgz_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rgz_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                pages INTEGER NOT NULL,
                publisher TEXT NOT NULL,
                logo TEXT
            )
        """)
        
        admin_password_hashed = generate_password_hash('admin')

        cur.execute("""
            INSERT INTO rgz_users (login, password, is_admin) 
            VALUES ('admin', ?, 1)
        """, (admin_password_hashed,))
        
    
    conn.commit()
    db_close(conn, cur)

def check_and_init_rgz():
    """Проверяем и при необходимости заполняем таблицы РГЗ реальными книгами"""
    conn, cur = db_connect()
    
    # Проверяем, есть ли столбец logo
    try:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='rgz_books' AND column_name='logo'")
        else:
            cur.execute("PRAGMA table_info(rgz_books)")
            columns = [row[1] for row in cur.fetchall()]
            if 'logo' not in columns:
                cur.execute("ALTER TABLE rgz_books ADD COLUMN logo VARCHAR(300)")
    except:
        pass
    
    # Проверяем таблицу книг
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT COUNT(*) AS cnt FROM rgz_books")
    else:
        cur.execute("SELECT COUNT(*) AS cnt FROM rgz_books")
    
    row = cur.fetchone()
    count = row['cnt'] if row else 0

    # Если таблица пустая — заполняем 100 реальных книг
    if count == 0:
        print("Заполняем базу 100 реальными книгами...")
        
        real_books = [
            ("Война и мир", "Лев Толстой", 1225, "Эксмо", "/static/rgz/1.jpg"),
            ("Преступление и наказание", "Федор Достоевский", 672, "АСТ", "/static/rgz/2.jpg"),
            ("1984", "Джордж Оруэлл", 328, "Азбука", "/static/rgz/3.jpg"),
            ("Мастер и Маргарита", "Михаил Булгаков", 480, "Вагриус", "/static/rgz/4.jpg"),
            ("Гарри Поттер и философский камень", "Джоан Роулинг", 432, "Росмэн", "/static/rgz/5.jpg"),
            ("Три товарища", "Эрих Мария Ремарк", 384, "АСТ", "/static/rgz/6.jpg"),
            ("Убить пересмешника", "Харпер Ли", 416, "Азбука", "/static/rgz/7.jpg"),
            ("Властелин колец", "Джон Р.Р. Толкин", 1216, "АСТ", "/static/rgz/8.jpg"),
            ("Портрет Дориана Грея", "Оскар Уайльд", 320, "Эксмо", "/static/rgz/9.jpg"),
            ("Над пропастью во ржи", "Джером Сэлинджер", 288, "Эксмо", "/static/rgz/10.jpg"),
            ("Атлант расправил плечи", "Айн Рэнд", 1394, "Альпина Паблишер", "/static/rgz/11.jpg"),
            ("Тень горы", "Грегори Дэвид Робертс", 576, "АСТ", "/static/rgz/12.jpg"),
            ("Шантарам", "Грегори Дэвид Робертс", 864, "АСТ", "/static/rgz/13.jpg"),
            ("Зеленая миля", "Стивен Кинг", 416, "АСТ", "/static/rgz/14.jpg"),
            ("Побег из Шоушенка", "Стивен Кинг", 320, "АСТ", "/static/rgz/15.jpg"),
            ("Код да Винчи", "Дэн Браун", 544, "АСТ", "/static/rgz/16.jpg"),
            ("Ангелы и демоны", "Дэн Браун", 624, "АСТ", "/static/rgz/17.jpg"),
            ("Инферно", "Дэн Браун", 576, "АСТ", "/static/rgz/18.jpg"),
            ("Грозовой перевал", "Эмили Бронте", 416, "Эксмо", "/static/rgz/19.jpg"),
            ("Джейн Эйр", "Шарлотта Бронте", 608, "Эксмо", "/static/rgz/20.jpg"),
            ("Маленький принц", "Антуан де Сент-Экзюпери", 96, "Эксмо", "/static/rgz/21.jpg"),
            ("Алиса в Стране чудес", "Льюис Кэрролл", 224, "Эксмо", "/static/rgz/22.jpg"),
            ("Гордость и предубеждение", "Джейн Остин", 416, "Эксмо", "/static/rgz/23.jpg"),
            ("Великий Гэтсби", "Фрэнсис Скотт Фицджеральд", 256, "Эксмо", "/static/rgz/24.jpg"),
            ("Старик и море", "Эрнест Хемингуэй", 128, "АСТ", "/static/rgz/25.jpg"),
            ("По ком звонит колокол", "Эрнест Хемингуэй", 576, "АСТ", "/static/rgz/26.jpg"),
            ("Прощай, оружие!", "Эрнест Хемингуэй", 320, "АСТ", "/static/rgz/27.jpg"),
            ("Лолита", "Владимир Набоков", 448, "Азбука", "/static/rgz/28.jpg"),
            ("Мы", "Евгений Замятин", 288, "АСТ", "/static/rgz/29.jpg"),
            ("Скотный двор", "Джордж Оруэлл", 144, "Азбука", "/static/rgz/30.jpg"),
            ("Фауст", "Иоганн Вольфганг Гёте", 512, "Эксмо", "/static/rgz/31.jpg"),
            ("Братья Карамазовы", "Федор Достоевский", 1024, "АСТ", "/static/rgz/32.jpg"),
            ("Идиот", "Федор Достоевский", 640, "АСТ", "/static/rgz/33.jpg"),
            ("Бесы", "Федор Достоевский", 768, "АСТ", "/static/rgz/34.jpg"),
            ("Анна Каренина", "Лев Толстой", 864, "Эксмо", "/static/rgz/35.jpg"),
            ("Воскресение", "Лев Толстой", 576, "Эксмо", "/static/rgz/36.jpg"),
            ("Капитанская дочка", "Александр Пушкин", 224, "Эксмо", "/static/rgz/37.jpg"),
            ("Евгений Онегин", "Александр Пушкин", 288, "Эксмо", "/static/rgz/38.jpg"),
            ("Мертвые души", "Николай Гоголь", 352, "Эксмо", "/static/rgz/39.jpg"),
            ("Ревизор", "Николай Гоголь", 192, "Эксмо", "/static/rgz/40.jpg"),
            ("Отцы и дети", "Иван Тургенев", 320, "Эксмо", "/static/rgz/41.jpg"),
            ("Герой нашего времени", "Михаил Лермонтов", 256, "Эксмо", "/static/rgz/42.jpg"),
            ("Обломов", "Иван Гончаров", 544, "Эксмо", "/static/rgz/43.jpg"),
            ("Тихий Дон", "Михаил Шолохов", 1504, "Эксмо", "/static/rgz/44.jpg"),
            ("Доктор Живаго", "Борис Пастернак", 608, "Эксмо", "/static/rgz/45.jpg"),
            ("И дольше века длится день", "Чингиз Айтматов", 416, "АСТ", "/static/rgz/46.jpg"),
            ("Плаха", "Чингиз Айтматов", 384, "АСТ", "/static/rgz/47.jpg"),
            ("Белый Бим Черное ухо", "Гавриил Троепольский", 256, "АСТ", "/static/rgz/48.jpg"),
            ("Не стреляйте в белых лебедей", "Борис Васильев", 320, "Эксмо", "/static/rgz/49.jpg"),
            ("А зори здесь тихие", "Борис Васильев", 192, "Эксмо", "/static/rgz/50.jpg"),
            ("Два капитана", "Вениамин Каверин", 704, "АСТ", "/static/rgz/51.jpg"),
            ("Как закалялась сталь", "Николай Островский", 416, "Эксмо", "/static/rgz/52.jpg"),
            ("Двенадцать стульев", "Илья Ильф, Евгений Петров", 448, "АСТ", "/static/rgz/53.jpg"),
            ("Золотой теленок", "Илья Ильф, Евгений Петров", 480, "АСТ", "/static/rgz/54.jpg"),
            ("Дети капитана Гранта", "Жюль Верн", 640, "Эксмо", "/static/rgz/55.jpg"),
            ("Двадцать тысяч лье под водой", "Жюль Верн", 480, "Эксмо", "/static/rgz/56.jpg"),
            ("Таинственный остров", "Жюль Верн", 576, "Эксмо", "/static/rgz/57.jpg"),
            ("Граф Монте-Кристо", "Александр Дюма", 1248, "Эксмо", "/static/rgz/58.jpg"),
            ("Три мушкетера", "Александр Дюма", 736, "Эксмо", "/static/rgz/59.jpg"),
            ("Королева Марго", "Александр Дюма", 768, "Эксмо", "/static/rgz/60.jpg"),
            ("Приключения Шерлока Холмса", "Артур Конан Дойл", 512, "АСТ", "/static/rgz/61.jpg"),
            ("Собака Баскервилей", "Артур Конан Дойл", 256, "АСТ", "/static/rgz/62.jpg"),
            ("Затерянный мир", "Артур Конан Дойл", 320, "АСТ", "/static/rgz/63.jpg"),
            ("Путешествия Гулливера", "Джонатан Свифт", 384, "Эксмо", "/static/rgz/64.jpg"),
            ("Робинзон Крузо", "Даниель Дефо", 320, "Эксмо", "/static/rgz/65.jpg"),
            ("Остров сокровищ", "Роберт Льюис Стивенсон", 288, "Эксмо", "/static/rgz/66.jpg"),
            ("Страна Оз", "Лаймен Фрэнк Баум", 240, "Эксмо", "/static/rgz/67.jpg"),
            ("Питер Пэн", "Джеймс Мэтью Барри", 192, "Эксмо", "/static/rgz/68.jpg"),
            ("Ветер в ивах", "Кеннет Грэм", 256, "Эксмо", "/static/rgz/69.jpg"),
            ("Моби Дик", "Герман Мелвилл", 704, "АСТ", "/static/rgz/70.jpg"),
            ("Приключения Тома Сойера", "Марк Твен", 288, "Эксмо", "/static/rgz/71.jpg"),
            ("Приключения Гекльберри Финна", "Марк Твен", 384, "Эксмо", "/static/rgz/72.jpg"),
            ("Янки из Коннектикута при дворе короля Артура", "Марк Твен", 352, "Эксмо", "/static/rgz/73.jpg"),
            ("Приключения барона Мюнхгаузена", "Рудольф Эрих Распе", 160, "Эксмо", "/static/rgz/74.jpg"),
            ("Триумфальная арка", "Эрих Мария Ремарк", 576, "АСТ", "/static/rgz/75.jpg"),
            ("На Западном фронте без перемен", "Эрих Мария Ремарк", 288, "АСТ", "/static/rgz/76.jpg"),
            ("Черный обелиск", "Эрих Мария Ремарк", 448, "АСТ", "/static/rgz/77.jpg"),
            ("Степной волк", "Герман Гессе", 320, "АСТ", "/static/rgz/78.jpg"),
            ("Игра в бисер", "Герман Гессе", 544, "АСТ", "/static/rgz/79.jpg"),
            ("Сиддхартха", "Герман Гессе", 192, "АСТ", "/static/rgz/80.jpg"),
            ("Нарцисс и Златоуст", "Герман Гессе", 256, "АСТ", "/static/rgz/81.jpg"),
            ("Поющие в терновнике", "Колин Маккалоу", 736, "АСТ", "/static/rgz/82.jpg"),
            ("Унесенные ветром", "Маргарет Митчелл", 1024, "АСТ", "/static/rgz/83.jpg"),
            ("Женщина французского лейтенанта", "Джон Фаулз", 544, "АСТ", "/static/rgz/84.jpg"),
            ("Коллекционер", "Джон Фаулз", 352, "АСТ", "/static/rgz/85.jpg"),
            ("Волхв", "Джон Фаулз", 736, "АСТ", "/static/rgz/86.jpg"),
            ("Повелитель мух", "Уильям Голдинг", 320, "АСТ", "/static/rgz/87.jpg"),
            ("Сто лет одиночества", "Габриэль Гарсия Маркес", 544, "АСТ", "/static/rgz/88.jpg"),
            ("Любовь во время чумы", "Габриэль Гарсия Маркес", 480, "АСТ", "/static/rgz/89.jpg"),
            ("Полковнику никто не пишет", "Габриэль Гарсия Маркес", 128, "АСТ", "/static/rgz/90.jpg"),
            ("О дивный новый мир", "Олдос Хаксли", 320, "АСТ", "/static/rgz/91.jpg"),
            ("Остров", "Олдос Хаксли", 480, "АСТ", "/static/rgz/92.jpg"),
            ("Имя розы", "Умберто Эко", 672, "Симпозиум", "/static/rgz/93.jpg"),
            ("Парфюмер", "Патрик Зюскинд", 320, "Азбука", "/static/rgz/94.jpg"),
            ("Милые кости", "Элис Сиболд", 416, "Эксмо", "/static/rgz/95.jpg"),
            ("Дневник памяти", "Николас Спаркс", 320, "АСТ", "/static/rgz/96.jpg"),
            ("Спеши любить", "Николас Спаркс", 288, "АСТ", "/static/rgz/97.jpg"),
            ("Дорогой Джон", "Николас Спаркс", 304, "АСТ", "/static/rgz/98.jpg"),
            ("Женщина в белом", "Уилки Коллинз", 672, "Азбука", "/static/rgz/99.jpg"),
            ("Дракула", "Брэм Стокер", 448, "АСТ", "/static/rgz/100.jpg")
        ]
        
        # Добавляем книги в БД
        for title, author, pages, publisher, logo in real_books:
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute(
                    "INSERT INTO rgz_books (title, author, pages, publisher, logo) VALUES (%s, %s, %s, %s, %s)",
                    (title, author, pages, publisher, logo)
                )
            else:
                cur.execute(
                    "INSERT INTO rgz_books (title, author, pages, publisher, logo) VALUES (?, ?, ?, ?, ?)",
                    (title, author, pages, publisher, logo)
                )
        
        conn.commit()
        print(f"Добавлено {len(real_books)} книг в базу данных")
        print("Картинки: static/rgz/1.jpg ... static/rgz/100.jpg")
    
    db_close(conn, cur)

# ============ ОСНОВНЫЕ МАРШРУТЫ ============

@rgz.route('/rgz/')
def main():
    """Главная страница РГЗ"""
    create_rgz_tables()
    check_and_init_rgz()
    return render_template('rgz/books.html', login=session.get('login'))

@rgz.route('/rgz/json-rpc-api/', methods=['POST'])
def api():
    """JSON-RPC API"""
    check_and_init_rgz()
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
        
        # Добавим отладочную печать
        print(f"=== ПАРАМЕТРЫ ЗАПРОСА ===")
        print(f"sort_by: {sort_by}")
        print(f"sort_order: {sort_order}")
        print(f"title: {title}")
        print(f"author: {author}")
        print(f"publisher: {publisher}")
        print(f"page: {page}")
        
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
        
        # Сортировка - ВАЖНОЕ ИСПРАВЛЕНИЕ
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
        # Строим запрос без LIMIT и OFFSET
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
        
        print(f"Count query: {count_query}")
        print(f"Count params: {count_params}")
        
        cur.execute(count_query, count_params)
        count_row = cur.fetchone()
        total = count_row['cnt'] if count_row else 0
        
        db_close(conn, cur)
        
        print(f"Найдено книг: {len(books)}")
        print(f"Всего книг: {total}")
        
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

@rgz.route('/rgz/recreate')
def recreate():
    """Пересоздание таблиц (для отладки)"""
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DROP TABLE IF EXISTS rgz_books CASCADE")
        cur.execute("DROP TABLE IF EXISTS rgz_users CASCADE")
    else:
        cur.execute("DROP TABLE IF EXISTS rgz_books")
        cur.execute("DROP TABLE IF EXISTS rgz_users")
    
    conn.commit()
    db_close(conn, cur)
    
    create_rgz_tables()
    check_and_init_rgz()
    
    return "Таблицы успешно пересозданы"