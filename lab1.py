from flask import Blueprint, url_for, request, redirect
import datetime
lab1 = Blueprint('lab1', __name__)


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author")
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


@lab1.route("/lab1/image")
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


@lab1.route('/lab1/counter')
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


@lab1.route('/lab1/clear_counter')
def clear_counter():
    global count
    count = 0
    return redirect('/lab1/counter')


@lab1.route('/lab1/info')
def info():
    return redirect('/lab1/author')


@lab1.route('/lab1/created')
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


@lab1.route('/lab1')
def lab():
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


@lab1.route('/lab1/400')
def err400():
    return "Неверный запрос", 400


@lab1.route('/lab1/401')
def err401():
    return "Необходимо авторизироваться", 401


@lab1.route('/lab1/402')
def err402():
    return "Требуется оплата", 402


@lab1.route('/lab1/403')
def err403():
    return "Доступ запрещён", 403


@lab1.route('/lab1/405')
def err405():
    return "Метод не поддерживается", 405


@lab1.route('/lab1/418')
def err418():
    return "Я - чайник", 418


@lab1.route('/lab1/error')
def error500():
    return 1/0 