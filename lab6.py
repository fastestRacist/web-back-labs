from flask import Blueprint, render_template, request, make_response, redirect, session, current_app
import random
import sqlite3
from lab5 import db_close, db_connect
lab6 = Blueprint('lab6', __name__)
# offices = []
# for i in range(1,11):
#     offices.append({"number": i, "tenant": "", "price": random.randint(900,1000)})

# @lab6.route('/lab6/')
# def main():
#     return render_template('lab6/lab6.html')


# @lab6.route('/lab6/json-rpc-api/', methods = ['POST'])
# def api():
#     data = request.json
#     id = data['id']
#     if data['method'] == 'info':
#         return {
#             'jsonrpc': '2.0',
#             'result': offices,
#             'id': id
#         }
#     login = session.get('login')
#     if not login:
#         return {
#             'jsonrpc': '2.0',
#             'error': {
#                 'code': 1,
#                 'message': 'Unauthorized'
#             },
#             'id' : id
#         }
    
#     if data['method'] == 'booking':
#         office_number = data['params']
#         for office in offices:
#             if office['number'] == office_number:
#                 if office['tenant'] != '':
#                     return {
#                         'jsonrpc': '2.0',
#                         'error': {
#                             'code': 2,
#                             'message': 'Already booked'
#                         },
#                         'id' : id
#                     }
#                 office['tenant'] = login
#                 return {
#                     'jsonrpc': '2.0',
#                     'result': 'success',
#                     'id' : id
#                 }
#     elif data['method'] == 'booking':
#         return {
#             'jsonrpc': '2.0',
#             'error': {
#                 'code': -32601,
#                 'message': 'Method not found'
#             },
#             'id': id
#         }
#     if data['method'] == 'cancellation':
#         office_number = data['params']
#         for office in offices:
#             if office['number'] == office_number:
#                 if office['tenant'] == '':
#                     return {
#                         'jsonrpc': '2.0',
#                         'error': {
#                             'code': 3,
#                             'message': 'Office not booked'
#                         },
#                         'id': id
#                     }
#                 if office['tenant'] != login:
#                     return {
#                         'jsonrpc': '2.0',
#                         'error': {
#                             'code': 4,
#                             'message': 'You cant cancel this booking'
#                         },
#                         'id': id
#                     }
#                 office['tenant'] = ''
#                 return {
#                     'jsonrpc': '2.0',
#                     'result': 'success',
#                     'id': id
#                 }
#провера на то что таблица есть и если ее нет то вставлять туда данные
def check_and_init_offices():
    conn, cur = db_connect()
    cur.execute("SELECT COUNT(*) AS cnt FROM offices")
    row = cur.fetchone()
    count = row['cnt'] if row else 0
    if count == 0:
        for i in range(1, 11):
            price = random.randint(900, 1000)
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute(
                    "INSERT INTO offices (number, tenant, price) VALUES (%s, %s, %s)",
                    (i, '', price)
                )
            else:
                cur.execute(
                    "INSERT INTO offices (number, tenant, price) VALUES (?, ?, ?)",
                    (i, '', price)
                )
    db_close(conn, cur)


@lab6.route('/lab6/')
def main():    
    check_and_init_offices()    
    return render_template('lab6/lab6.html')


@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    check_and_init_offices()    
    data = request.json
    id = data.get('id')
    method = data.get('method')
#если пользователь на авториз то 
    if method == 'info':
        conn, cur = db_connect()
        cur.execute("SELECT number, tenant, price FROM offices ORDER BY number")
        
        rows = cur.fetchall()

        offices = []
        for row in rows:
            offices.append({
                'number': row['number'],
                'tenant': row['tenant'],
                'price': row['price']
            })
            
        db_close(conn, cur)

        return {
            'jsonrpc': '2.0',
            'result': offices,
            'id': id
        }

    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }
#бронирование
    if method == 'booking':
        office_number = data['params']
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?", (office_number,))
        
        row = cur.fetchone()

        tenant = row['tenant']
        if tenant != '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 2,
                    'message': 'Already booked'
                },
                'id': id
            }

        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "UPDATE offices SET tenant = %s WHERE number = %s",
                (login, office_number)
            )
        else:
            cur.execute(
                "UPDATE offices SET tenant = ? WHERE number = ?",
                (login, office_number)
            )

        db_close(conn, cur)
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
#отмена брони
    elif method == 'cancellation':
        office_number = data['params']
        conn, cur = db_connect()
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?", (office_number,))
        
        row = cur.fetchone()

        if not row:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                },
                'id': id
            }

        tenant = row['tenant']

        #если оофис не арендован
        if tenant == '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Office not booked'
                },
                'id': id
            }

        # Офис арендован другим пользователем
        if tenant != login:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'You cant cancel this booking'
                },
                'id': id
            }

        # Снимаем аренду
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "UPDATE offices SET tenant = %s WHERE number = %s",
                ('', office_number)
            )
        else:
            cur.execute(
                "UPDATE offices SET tenant = ? WHERE number = ?",
                ('', office_number)
            )

        db_close(conn, cur)
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }

    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }