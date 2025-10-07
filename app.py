from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
app = Flask(__name__)

# @app.errorhandler(404)
# def not_found(err):
#     return '''
# <!doctype html>
# <html>
# <head>
#     <style>
#         body {text-align: center;}
#         h1 {color: red;}
#         h2 {color: grey;}
#     </style>
# </head>
# <body>
#     <h1>404</h1>
#     <h2>Страница не найдена</h2>
#     <img src="/static/404.jpg" width="500">
# </body>
# </html>
# ''', 404

log_404 = []

@app.errorhandler(404)
def not_found(err):
    client_ip = request.remote_addr
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = request.url
    log_entry = f"[{time}, пользователь {client_ip}] зашел на адрес: {url}"
    log_404.append(log_entry)
    page = f'''
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{text-align: center;}}
        h1 {{color: red;}}
        h2 {{color: grey;}}
    </style>
</head>
<body>
    <h1>404</h1>
    <h2>Страница не найдена</h2>
    <img src="/static/404.jpg" width="500">
    <p>IP пользователя: {client_ip}</p>
    <p>Дата и время: {time}</p>
    <p>Вы пытались открыть: {url}</p>
    <p><a href="/">Перейти на главную страницу</a></p>

    <div class="log">
        <h2>Журнал</h2>
        <ul>
            {''.join(f"<li>{entry}</li>" for entry in log_404)}
        </ul>
    </div>
</body>
</html>
'''
    return page, 404


@app.route("/lab1/web")
def web():
    return """<!doctype html>
        <html>
           <body>
               <h1>web-сервер на flask</h1>
           </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/lab1/author")
def author ():
    name = "Хобенков Егор Алексеевич"
    group = "ФБИ-32"
    faculty = "ФБ"

    return """ <!doctype html>
        <html>
            <body>  
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href="/lab1/web">web</a>
            </body>
        </html>"""   

@app.route("/lab1/image")
def image():
    path = url_for('static', filename='oak.jpg')
    css = url_for('static', filename='lab1.css')
    return f'''
<!doctype html>
<html>
<head>
    <link rel="stylesheet" href="{css}">
</head>
<body>
    <h1>Дуб</h1>
    <img src="{path}">
</body>
</html>
''', 200, {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Language": "ru",
        "X-Author": "Khobenkov",
        "X-Lab": "Lab1"
    }

count = 0
@app.route('/lab1/counter')
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return '''
<!doctype html>
<html>
    <body>
        Сколько раз вы сюда заходили: ''' + str(count) + '''<br>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + url + '''<br>
        Ваш IP-адрес: ''' + client_ip + '''<br>
        <a href="/lab1/clear_counter">Сбросить счётчик</a>
    </body>
</html>
'''
@app.route('/lab1/clear_counter')
def clear_counter():
    global count
    count = 0
    return redirect('/lab1/counter')

@app.route('/lab1/info')
def info():
    return redirect('/lab1/author')

@app.route('/lab1/created')
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i> что-то создано...</i></div>
    </body>
</html>
''', 201    

@app.route('/')
@app.route('/index')
def index():
    return '''
<!doctype html>
<html>
<head>
    <title>НГТУ, ФБ, Лабораторные работы</title>
</head>
<body>
    <header>
        НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных
    </header>
    <ul>
        <li><a href="/lab1">Первая лабораторная</a></li>
    </ul>
    <footer>
        <p>Хобенков Егор Алексеевич, ФБИ-32, 3 курс, 2025 год</p>
    </footer>
</body>
</html>
'''

@app.route('/lab1')
def lab1():
    return '''
<!doctype html>
<html>
<head>
    <title>Лабораторная 1</title>
</head>
<body>
    <p>Flask — фреймворк для создания веб-приложений на языке
    программирования Python, использующий набор инструментов
    Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
    называемых микрофреймворков — минималистичных каркасов
    веб-приложений, сознательно предоставляющих лишь самые базовые возможности.</p>
    <a href="/">На главную</a>
        <h2>Список роутов</h2>
    <ul>
        <li><a href="/lab1/web">/lab1/web</a></li>
        <li><a href="/lab1/author">/lab1/author</a></li>
        <li><a href="/lab1/image">/lab1/image</a></li>
        <li><a href="/lab1/counter">/lab1/counter</a></li>
        <li><a href="/lab1/info">/lab1/info</a></li>
        <li><a href="/lab1/created">/lab1/created</a></li>
        <li><a href="/lab1/error">/lab1/error</a></li>
        <li><a href="/lab1/400">/lab1/400</a></li>
        <li><a href="/lab1/401">/lab1/401</a></li>
        <li><a href="/lab1/402">/lab1/402</a></li>
        <li><a href="/lab1/403">/lab1/403</a></li>
        <li><a href="/lab1/404">/lab1/404</a></li>
        <li><a href="/lab1/405">/lab1/405</a></li>
        <li><a href="/lab1/418">/lab1/418</a></li>
    </ul>
</body>
</html>
'''

@app.route('/lab1/400')
def err400():
    return "Неверный запрос", 400

@app.route('/lab1/401')
def err401():
    return "Необходимо авторизироваться", 401

@app.route('/lab1/402')
def err402():
    return "Требуется оплата", 402

@app.route('/lab1/403')
def err403():
    return "Доступ запрещён", 403

@app.route('/lab1/405')
def err405():
    return "Метод не поддерживается", 405

@app.route('/lab1/418')
def err418():
    return "Я - чайник", 418

@app.route('/lab1/error')
def error500():
    return 1/0 

@app.errorhandler(500)
def server_error(err):
    return '''
        <!doctype html>
        <html>
        <body>
            <h1>Ошибка 500: внутренняя ошибка сервера</h1>
            <p>Произошла непредвиденная ошибка.</p>
        </body>
        </html>
        ''', 500

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = ['роза', 'тюльпан', 'незабудка', 'ромашка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        return "цветок: " + flower_list[flower_id]

@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''
<!doctype html>
<html>
    <body>
    <h1>Добавлен новый цветов</h1>
    <p>Название нового цветка: {name} </p>
    <p>Всего цветов: {len(flower_list)}</p>
    <p>Полный список: {flower_list}</p>
    </body>
</html>
'''

@app.route('/lab2/example')
def example():
    lab_num = 'Лабораторная работа 2'
    name = 'Хобенков Егор'
    group = 'ФБИ-32'
    course = '3 курс'
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321},
        ]
    return render_template('example.html', name = name, group = group, course = course, lab_num = lab_num, fruits = fruits)
@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = "О сколько нам открытий чудных..."
    return render_template('filter.html', phrase=phrase)