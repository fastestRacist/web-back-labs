from flask import Blueprint, render_template, request, make_response, redirect, session, current_app, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

from datetime import datetime
from lab5 import db_close, db_connect

lab7 = Blueprint('lab7', __name__)

# @lab7.route('/lab7/')
# def main():
#     return render_template('lab7/index.html')


# films = [
#     {
#         "title": "Intouchables",
#         "title_ru": "1+1",
#         "year": 2011,
#         "description": "Пострадав в результате несчастного случая, богатый аристократ Филипп нанимает в помощники человека, "
#         "который менее всего подходит для этой работы, – молодого жителя предместья Дрисса, только что освободившегося из тюрьмы. "
#         "Несмотря на то, что Филипп прикован к инвалидному креслу, Дриссу удается привнести в размеренную жизнь аристократа дух приключений."
#     },
#     {
#         "title": "Interstellar",
#         "title_ru": "Интерстеллар",
#         "year": 2014,
#         "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, "
#         "коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области "
#         "пространства-времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических "
#         "путешествий человека и найти планету с подходящими для человечества условиями."
#     },
#     {
#         "title": "The Shawshank Redemption",
#         "title_ru": "Побег из Шоушенка",
#         "year": 1994,
#         "description": "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, "
#         "он сталкивается с жестокостью и беззаконием, царящими по обе стороны решётки. Каждый, кто попадает в эти стены, становится их рабом до конца жизни. "
#         "Но Энди, обладающий живым умом и доброй душой, находит подход как к заключённым, так и к охранникам, добиваясь их особого к себе расположения."
#     },
#     {
#         "title": "The Gentlemen",
#         "title_ru": "Джентльмены",
#         "year": 2019,
#         "description": "Один ушлый американец ещё со студенческих лет приторговывал наркотиками, а теперь придумал схему нелегального "
#         "обогащения с использованием поместий обедневшей английской аристократии и очень неплохо на этом разбогател. Другой пронырливый "
#         "журналист приходит к Рэю, правой руке американца, и предлагает тому купить киносценарий, в котором подробно описаны преступления "
#         "его босса при участии других представителей лондонского криминального мира — партнёра-еврея, китайской диаспоры, чернокожих спортсменов "
#         "и даже русского олигарха."
#     },
#     {
#         "title": "The Green Mile",
#         "title_ru": "Зеленая миля",
#         "year": 1999,
#         "description": "Пол Эджкомб — начальник блока смертников в тюрьме «Холодная гора», каждый из узников которого однажды "
#         "проходит «зеленую милю» по пути к месту казни. Пол повидал много заключённых и надзирателей за время работы. Однако гигант Джон Коффи, "
#         "обвинённый в страшном преступлении, стал одним из самых необычных обитателей блока."
#     },
# ]


# @lab7.route('/lab7/rest-api/films/', methods = ['GET'])
# def get_films():
#     return films


# @lab7.route('/lab7/rest-api/films/<int:id>', methods = ['GET'])
# def get_film(id):
#     if id < 0 or id >= len(films):
#         abort(404)
#     return films[id]


# @lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
# def del_film(id):
#     if id < 0 or id >= len(films):
#         abort(404)
#     del films[id]
#     return '', 204


# @lab7.route('/lab7/rest-api/films/<int:id>', methods = ['PUT'])
# def put_film(id):
#     if id < 0 or id >= len(films):
#         abort(404)
#     film = request.get_json()
#     if film['title_ru'] == '' and film['title'] == '':
#         return {'title': 'Введите название (на русском обязательно)'}, 400
#     elif film['title_ru'] == '':
#         return {'title_ru': 'Введите название (обязательное поле)'}, 400
#     if int(film['year']) < 1895 or int(film['year']) > datetime.now().year:
#         return {'year': 'Не раньше 1895 г. и не позднее текущего года'}, 400
#     if film['description'] == '' or len(film['description']) > 2000:
#         return {'description': 'Заполните описание до 2000 символов'}, 400
#     if film['title'] == '':
#         film['title'] = film['title_ru']
#     films[id] = film
#     return films[id]


# @lab7.route('/lab7/rest-api/films/', methods=['POST'])
# def add_film():
#     film = request.get_json()
#     if film['title_ru'] == '' and film['title'] == '':
#         return {'title': 'Введите название (на русском обязательно)'}, 400
#     elif film['title_ru'] == '':
#         return {'title_ru': 'Введите название (обязательное поле)'}, 400
#     if int(film['year']) < 1895 or int(film['year']) > datetime.now().year:
#         return {'year': 'Не раньше 1895 г. и не позднее текущего года'}, 400
#     if film['description'] == '' or len(film['description']) > 2000:
#         return {'description': 'Заполните описание до 2000 символов'}, 400
#     if film['title'] == '':
#         film['title'] = film['title_ru']
#     films.append(film)
#     return films



@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    
    cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id")
    
    films = cur.fetchall()
    
    #нужно в список словарей преобразовать
    result = []
    for film in films:
        film_dict = {
            'id': film['id'],
            'title': film['title'],
            'title_ru': film['title_ru'],
            'year': film['year'],
            'description': film['description']
        }
        result.append(film_dict)
    db_close(conn, cur)
    return jsonify(result)
#вывод таблицы
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s", (id,))
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (id,))
    film = cur.fetchone()
    
    db_close(conn, cur)
    return {
        'id': film['id'],
        'title': film['title'],
        'title_ru': film['title_ru'],
        'year': film['year'],
        'description': film['description']
    }

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM films WHERE id = %s", (id,))
    else:
        cur.execute("DELETE FROM films WHERE id = ?", (id,))
    db_close(conn, cur)
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film = request.get_json()
    
    #проверочка данных
    if film['title_ru'] == '' and film['title'] == '':
        return {'title': 'Введите название (на русском обязательно)'}, 400
    elif film['title_ru'] == '':
        return {'title_ru': 'Введите название (обязательное поле)'}, 400
    
    year = int(film['year'])
    if year < 1895 or year > datetime.now().year:
        return {'year': 'Не раньше 1895 г. и не позднее текущего года'}, 400
    
    if film['description'] == '' or len(film['description']) > 2000:
        return {'description': 'Заполните описание до 2000 символов'}, 400
    
    if film['title'] == '':
        film['title'] = film['title_ru']
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE films SET title = %s, title_ru = %s, year = %s, description = %s WHERE id = %s", (film['title'], film['title_ru'], film['year'], film['description'], id))
    else:
        cur.execute("UPDATE films SET title = ?, title_ru = ?, year = ?, description = ? WHERE id = ?", (film['title'], film['title_ru'], film['year'], film['description'], id))
    
    # Возвращаем обновленный фильм
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s", (id,))
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (id,))
    
    updated_film = cur.fetchone()
    db_close(conn, cur)
    return {
        'id': updated_film['id'],
        'title': updated_film['title'],
        'title_ru': updated_film['title_ru'],
        'year': updated_film['year'],
        'description': updated_film['description']
    }

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    
    #проверка
    if film['title_ru'] == '' and film['title'] == '':
        return {'title': 'Введите название (на русском обязательно)'}, 400
    elif film['title_ru'] == '':
        return {'title_ru': 'Введите название (обязательное поле)'}, 400
    
    year = int(film['year'])
    if year < 1895 or year > datetime.now().year:
        return {'year': 'Не раньше 1895 г. и не позднее текущего года'}, 400
    
    if film['description'] == '' or len(film['description']) > 2000:
        return {'description': 'Заполните описание до 2000 символов'}, 400
    
    if film['title'] == '':
        film['title'] = film['title_ru']
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO films (title, title_ru, year, description) VALUES (%s, %s, %s, %s) RETURNING id", (film['title'], film['title_ru'], film['year'], film['description']))
        
        new_id = cur.fetchone()['id']
    else:
        cur.execute("INSERT INTO films (title, title_ru, year, description) VALUES (?, ?, ?, ?)", (film['title'], film['title_ru'], film['year'], film['description']))
        
        new_id = cur.lastrowid
    
    # Возвращаем созданный фильм
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s", (new_id,))
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (new_id,))
    
    new_film = cur.fetchone()
    db_close(conn, cur)
    return {
        'id': new_film['id'],
        'title': new_film['title'],
        'title_ru': new_film['title_ru'],
        'year': new_film['year'],
        'description': new_film['description']
    }, 201