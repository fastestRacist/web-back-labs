from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return '''
<!doctype html>
<html>
<head>
    <style>
        body {text-align: center;}
        h1 {color: red;}
        h2 {color: grey;}
    </style>
</head>
<body>
    <h1>404</h1>
    <h2>Страница не найдена</h2>
    <img src="/static/404.jpg" width="500">
</body>
</html>
''', 404


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
    <img src="{path}" alt="oak">
</body>
</html>
'''

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