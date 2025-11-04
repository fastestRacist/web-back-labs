from flask import Blueprint, render_template, request, make_response, redirect, session
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')


@lab4.route('/lab4/div-form/')
def div_form():
    return render_template('lab4/div-form.html')


@lab4.route('/lab4/div/', methods = ['POST'])
def div():
    x1=request.form.get('x1')
    x2=request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error = ' Оба поля должны быть заполнены!')
    if x2 == '0':
        return render_template('lab4/div.html', ZeroDivError = 'На ноль делить нельзя!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/sum-form/')
def sum_form():
    return render_template('lab4/sum-form.html')


@lab4.route('/lab4/sum/', methods = ['POST'])
def sum():
    x1=request.form.get('x1')
    x2=request.form.get('x2')
    if x1 == '':
        x1 = '0'
    if x2 == '':
        x2 = '0'
    x1 = int(x1)
    x2 = int(x2)
    result = x1 + x2
    return render_template('lab4/sum.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/mult-form/')
def mult_form():
    return render_template('lab4/mult-form.html')


@lab4.route('/lab4/mult/', methods = ['POST'])
def mult():
    x1=request.form.get('x1')
    x2=request.form.get('x2')
    if x1 == '':
        x1 = '1'
    if x2 == '':
        x2 = '1'
    x1 = int(x1)
    x2 = int(x2)
    result = x1 * x2
    return render_template('lab4/mult.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/sub-form/')
def sub_form():
    return render_template('lab4/sub-form.html')


@lab4.route('/lab4/sub/', methods = ['POST'])
def sub():
    x1=request.form.get('x1')
    x2=request.form.get('x2')
    if  x1 == '' or x2 == '':
        return render_template('lab4/sub.html', error = ' Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/deg-form/')
def deg_form():
    return render_template('lab4/deg-form.html')


@lab4.route('/lab4/deg/', methods = ['POST'])
def deg():
    x1=request.form.get('x1')
    x2=request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/deg.html', error = ' Оба поля должны быть заполнены!')
    if x2 == '0' and x1 == '0':
        return render_template('lab4/deg.html', ZeroDegError = 'Хотя бы одно поле не должно быть равно нулю!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 ** x2
    return render_template('lab4/deg.html', x1=x1, x2=x2, result=result)


tree_count = 0

@lab4.route('/lab4/tree/', methods=['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template("lab4/tree.html", tree_count=tree_count)
    
    operation = request.form.get('operation')

    if operation == 'cut' and tree_count > 0:
        tree_count -= 1
    elif operation == 'plant' and tree_count < 10:
        tree_count +=1
    
    return redirect('/lab4/tree')


# @lab4.route('/lab4/login/', methods = ['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return render_template("lab4/login.html", authorized = False)
#     login = request.form.get('login')
#     password = request.form.get('password')

#     if login == 'alex' and password == '123':
#         return render_template('/lab4/login.html/', error = 'Успешная авторизация')
    
#     error = "Неверный логин и/или пароль"
#     return render_template('/lab4/login.html/', error=error, authorized = False)


users = [
    {'login': 'alex', 'password': '123', 'name': 'Алекс', 'sex': 'М'},
    {'login': 'bob', 'password': '555', 'name': 'Роберт', 'sex': 'М'},
    {'login': 'egor', 'password': '321', 'name': 'Егор', 'sex': 'М'},
    {'login': 'marina', 'password': '121', 'name': 'Марина', 'sex': 'Ж'}
]

@lab4.route('/lab4/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorized = True
            login = session['login']
        else:
            authorized = False
            login = ''
        return render_template("lab4/login.html", authorized = authorized, login = login, users=users)
    login = request.form.get('login')
    password = request.form.get('password')

    if not login and not password:
        return render_template("lab4/login.html", error='Введите логин и пароль!', authorized=False, login = login)
    elif not login:
        return render_template("lab4/login.html", error='Введите логин!', authorized=False, login = login)
    elif not password:
        return render_template("lab4/login.html", error='Введите пароль!', authorized=False, login = login)

    for user in users:
        if login == user['login'] and password == user['password']:
            session['login'] = login
            return redirect('/lab4/login')
    
    error = "Неверный логин и/или пароль"
    return render_template('/lab4/login.html/', error=error, authorized = False, login = login)


@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')


@lab4.route('/lab4/fridge', methods = ['GET', 'POST'])
def fridge():
    message = None
    snowflakes = 0
    temp = request.form.get('temperature')

    if request.method == 'POST':
        if temp == '' or temp is None:
            message = "Ошибка: не задана температура"
        else:
            try:
                temp = int(temp)
                if temp < -12:
                    message = "Не удалось установить температуру — слишком низкое значение"
                elif temp > -1:
                    message = "Не удалось установить температуру — слишком высокое значение"
                elif -12 <= temp <= -9:
                    message = f"Установлена температура: {temp}°C"
                    snowflakes = 3
                elif -8 <= temp <= -5:
                    message = f"Установлена температура: {temp}°C"
                    snowflakes = 2
                elif -4 <= temp <= -1:
                    message = f"Установлена температура: {temp}°C"
                    snowflakes = 1
            except ValueError:
                message = "Ошибка: введите число"
    return render_template("lab4/fridge.html", message=message, snowflakes=snowflakes, temp=temp or '')


@lab4.route('/lab4/grain/', methods=['GET', 'POST'])
def grain():
    prices = {'ячмень': 12000, 'овёс': 8500, 'пшеница': 9000, 'рожь': 15000}
    message = None
    discount_msg = None
    total = None

    if request.method == 'POST':
        grain_type = request.form.get('grain')
        weight_str = request.form.get('weight')

        if not weight_str:
            message = "Ошибка: не указан вес"
        else:
            try:
                weight = float(weight_str)
                if weight <= 0:
                    message = "Ошибка: вес должен быть больше 0"
                elif weight > 100:
                    message = "Такого объёма сейчас нет в наличии"
                else:
                    price = prices.get(grain_type, 0)
                    total = price * weight
                    if weight > 10:
                        discount = total * 0.1
                        total -= discount
                        discount_msg = f"Применена скидка 10% за большой объём (-{int(discount)} руб.)"
                    message = f"Заказ успешно сформирован. Вы заказали {grain_type}. Вес: {weight} т. Сумма к оплате: {int(total)} руб."
            except ValueError:
                message = "Ошибка: введите корректное число веса"

    return render_template("lab4/grain.html", message=message, discount_msg=discount_msg)


# Страница регистрации
@lab4.route('/lab4/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab4/register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    name = request.form.get('name')

    # Проверки на заполненность полей
    if not login or not password or not confirm or not name:
        return render_template('lab4/register.html', error='Все поля должны быть заполнены!')

    # Проверка совпадения паролей
    if password != confirm:
        return render_template('lab4/register.html', error='Пароль и подтверждение не совпадают!')

    # Проверка, что логин уникален
    for user in users:
        if user['login'] == login:
            return render_template('lab4/register.html', error='Такой логин уже существует!')

    # Добавляем пользователя
    users.append({
        'login': login,
        'password': password,
        'name': name
    })

    return redirect('/lab4/login')


# Страница со списком пользователей
@lab4.route('/lab4/users/')
def users_list():
    if 'login' not in session:
        return redirect('/lab4/login')
    return render_template('lab4/users.html', users=users, login=session['login'])


# Удаление себя
@lab4.route('/lab4/delete_user/', methods=['POST'])
def delete_user():
    if 'login' not in session:
        return redirect('/lab4/login')

    global users
    login = session['login']
    users = [u for u in users if u['login'] != login]
    session.pop('login', None)
    return redirect('/lab4/login')


# Редактирование своих данных
@lab4.route('/lab4/edit_user/', methods=['GET', 'POST'])
def edit_user():
    if 'login' not in session:
        return redirect('/lab4/login')

    login = session['login']
    user = next((u for u in users if u['login'] == login), None)
    if not user:
        return redirect('/lab4/login')

    if request.method == 'GET':
        return render_template('lab4/edit_user.html', user=user)

    new_login = request.form.get('login')
    new_name = request.form.get('name')
    new_password = request.form.get('password')
    confirm = request.form.get('confirm')

    # Проверки
    if not new_login or not new_name:
        return render_template('lab4/edit_user.html', user=user, error='Имя и логин должны быть заполнены!')

    if new_password or confirm:
        if new_password != confirm:
            return render_template('lab4/edit_user.html', user=user, error='Пароль и подтверждение не совпадают!')
        else:
            user['password'] = new_password  # обновляем только если пароль указан и совпадает

    user['login'] = new_login
    user['name'] = new_name
    session['login'] = new_login

    return redirect('/lab4/users')
