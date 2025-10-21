from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
app = Flask(__name__)
app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)


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
        <li><a href="/lab2/">Вторая лабораторная</a></li>
        <li><a href="/lab3/">Третья лабораторная</a></li>
    </ul>
    <footer>
        <p>Хобенков Егор Алексеевич, ФБИ-32, 3 курс, 2025 год</p>
    </footer>
</body>
</html>
'''


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