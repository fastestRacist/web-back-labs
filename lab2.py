from flask import Blueprint, url_for, request, redirect, render_template, abort
import datetime
lab2 = Blueprint('lab2', __name__)


@lab2.route('/lab2/a')
def a():
    return 'без слэша'

@lab2.route('/lab2/a/')
def a2():
    return 'со слэшем'

# flower_list = ['роза', 'тюльпан', 'незабудка', 'ромашка']

# @lab2.route('/lab2/flowers/<int:flower_id>')
# def flowers(flower_id):
#     if flower_id >= len(flower_list):
#         abort(404)
#     else:
#         return f'''
# <!doctype html>
# <html>
#     <head>
#         <title>Цветок #{flower_id}</title>
#     </head>
#     <body>
#         <h1>Информация о цветке</h1>
#         <p><strong>Название цветка:</strong> {flower_list[flower_id]}</p>
#         <p><strong>ID цветка:</strong> {flower_id}</p>
#         <p><strong>Всего цветов в базе:</strong> {len(flower_list)}</p>
#         <a href="/lab2/all_flowers">Посмотреть все цветы</a>
#     </body>
# </html>
# '''

# @lab2.route('/lab2/add_flower/<name>')
# def add_flower(name):
#     flower_list.append(name)
#     return f'''
# <!doctype html>
# <html>
#     <body>
#     <h1>Добавлен новый цветов</h1>
#     <p>Название нового цветка: {name} </p>
#     <p>Всего цветов: {len(flower_list)}</p>
#     <p>Полный список: {flower_list}</p>
#     </body>
# </html>
# '''
# @lab2.route('/lab2/add_flower/')
# def no_flower():
#     abort(400, "вы не задали имя цветка")

# @lab2.route('/lab2/all_flowers/')
# def all_flowers():
#     return f'''
# <!doctype html>
# <html>
#     <head>
#         <title>Все цветы</title>
#     </head>
#     <body>
#         <h1>Список всех цветов</h1>
#         <p><strong>Общее количество цветов:</strong> {len(flower_list)}</p>
#         <h2>Список цветов:</h2>
#         <ul>
#             {"".join(f'<li>{i}: {flower}</li>' for i, flower in enumerate(flower_list))}
#         </ul>
#         <a href="/lab2/clear_flowers">Очистить список цветов</a>
#     </body>
# </html>
# '''

# @lab2.route('/lab2/clear_flowers/')
# def clear_flowers():
#     flower_list.clear()
#     return f'''
# <!doctype html>
# <html>
#     <body>
#         <h1>Список цветов очищен</h1>
#         <p>Все цветы были удалены из списка.</p>
#         <p><strong>Текущее количество цветов:</strong> {len(flower_list)}</p>
#         <a href="/lab2/all_flowers">Посмотреть все цветы</a>
#     </body>
# </html>
# '''

flower_list = [
    {'flower': 'роза', 'price': 300},
    {'flower': 'тюльпан', 'price': 310},
    {'flower': 'незабудка', 'price': 320},
    {'flower': 'ромашка', 'price': 330},
    ]

@lab2.route('/lab2/flowers/')
def all_flowers():
    return render_template('flowers.html', flower=flower_list)

@lab2.route('/lab2/add_flower/', methods=['POST'])
def add_flower():
    name = request.form.get('name')
    price = request.form.get('price')
    if name and price:
        flower_list.append({"flower": name, "price": int(price)})
    return redirect('/lab2/flowers/')

@lab2.route('/lab2/del_flowers/')
def del_flowers():
    if len(flower_list) == 0:
        abort(404)
    flower_list.clear()
    return '''<h1>Цветов нет</h1>
    <p><a href="/lab2/flowers/">Список цветов</a></p>'''

@lab2.route('/lab2/del_flowers/<int:idx>/')
def delete_flower(idx):
    if idx < 0 or idx >= len(flower_list):
        abort(404)
    flower_list.pop(idx)
    return redirect('/lab2/flowers/')

@lab2.route('/lab2/example')
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
@lab2.route('/lab2/')
def lab():
    return render_template('lab2.html')

@lab2.route('/lab2/filters/')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase=phrase)

@lab2.route('/lab2/calc/<int:num1>/<int:num2>')
def calc(num1, num2):
    return f'''<h1>Калькулятор:</h1>
    <p>{num1} + {num2} = {num1 + num2}<br>
    {num1} - {num2} = {num1 - num2}<br>
    {num1} x {num2} = {num1 * num2}<br>
    {num1}/{num2} = {num1/num2}<br>
    {num1}<sup>{num2}</sup> = {num1**num2}</p>'''

@lab2.route('/lab2/calc/')
def calc1():
    return redirect(url_for('calc', num1=1, num2=1))

@lab2.route('/lab2/calc/<int:num1>')
def calc_with_one(num1):
    return redirect(url_for('calc', num1=num1, num2=1))

books = [
    {"author": "Фёдор Достоевский", "title": "Преступление и наказание", "genre": "Роман", "pages": 671},
    {"author": "Лев Толстой", "title": "Война и мир", "genre": "Эпопея", "pages": 1225},
    {"author": "Михаил Булгаков", "title": "Мастер и Маргарита", "genre": "Фантастика", "pages": 480},
    {"author": "Антон Чехов", "title": "Рассказы", "genre": "Рассказы", "pages": 320},
    {"author": "Александр Пушкин", "title": "Евгений Онегин", "genre": "Роман в стихах", "pages": 240},
    {"author": "Николай Гоголь", "title": "Мёртвые души", "genre": "Поэма", "pages": 352},
    {"author": "Иван Тургенев", "title": "Отцы и дети", "genre": "Роман", "pages": 288},
    {"author": "Александр Солженицын", "title": "Архипелаг ГУЛАГ", "genre": "История", "pages": 1424},
    {"author": "Владимир Набоков", "title": "Лолита", "genre": "Роман", "pages": 336},
    {"author": "Михаил Лермонтов", "title": "Герой нашего времени", "genre": "Роман", "pages": 224},
    {"author": "Иван Бунин", "title": "Тёмные аллеи", "genre": "Рассказы", "pages": 192},
    {"author": "Борис Пастернак", "title": "Доктор Живаго", "genre": "Роман", "pages": 608}
]

@lab2.route('/lab2/books/')
def show_books():
    return render_template('books.html', books=books)

@lab2.route('/lab2/cars/')
def gallery():
    logos = [
        {"name": "Acura", "pic": "Acura", "country": "Япония"},
        {"name": "Audi", "pic": "Audi", "country": "Германия"},
        {"name": "Alpina", "pic": "Alpina", "country": "Германия"},
        {"name": "Aston Martin", "pic": "Aston Martin", "country": "Великобритания"},
        {"name": "BMW", "pic": "BMW", "country": "Германия"},
        {"name": "Bentley", "pic": "Bentley", "country": "Великобритания"},
        {"name": "Bugatti", "pic": "Bugatti", "country": "Франция"},
        {"name": "Cadillac", "pic": "Cadillac", "country": "СЩА"},
        {"name": "Chery", "pic": "Chery", "country": "Китай"},
        {"name": "Chevrolet", "pic": "Chevrolet", "country": "США"},
        {"name": "Citroen", "pic": "Citroen", "country": "Франция"},
        {"name": "Dodge", "pic": "Dodge", "country": "США"},
        {"name": "EXEED", "pic": "EXEED", "country": "Китай"},
        {"name": "Ferrari", "pic": "Ferrari", "country": "Италия"},
        {"name": "Geely", "pic": "Geely", "country": "Китай"},
        {"name": "Honda", "pic": "Honda", "country": "Япония"},
        {"name": "Hyundai", "pic": "Hyundai", "country": "Южная Корея"},
        {"name": "Infinity", "pic": "Infinity", "country": "Япония"},
        {"name": "Jaguar", "pic": "Jaguar", "country": "Великобритания"},
        {"name": "Jeep", "pic": "Jeep", "country": "США"},
    ]
    for item in logos:
        item["img_url"] = url_for('static',
                                  filename=f'{item["pic"]}.jpg')
    return render_template('cars.html', items=logos)