from flask import Blueprint, render_template, request, make_response, redirect
import datetime
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name', 'аноним')
    name_color = request.cookies.get('name_color')
    age = request.cookies.get('age', 'неизвестно')
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name','Alex', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color','magenta')
    return resp


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp


@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'
    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'
    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)


@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')


@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')
    #Пусть кофе стоит 120 рублей, черный чай - 80 рублей, зеленый - 70 рублей.
    if drink == 'cofee':
        price = 120
    elif drink == 'black-tea':
        price = 80
    else:
        price = 70
    #Добавка молока удорожает напиток на 30 рублей, а сахара - на 10.
    if request.args.get('milk') == 'on':
        price += 30
    if request.args.get('sugar') == 'on':
        price +=10

    return render_template('lab3/pay.html', price=price)


@lab3.route('/lab3/success', methods=['GET', 'POST'])
def success():
    price = request.values.get('price', type=int)
    return render_template('lab3/success.html', price=price)


@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bgcolor = request.args.get('bgcolor')
    fontsize = request.args.get('fontsize')
    fontfamily = request.args.get('fontfamily')
    if any([color, bgcolor, fontsize, fontfamily]):
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bgcolor:
            resp.set_cookie('bgcolor', bgcolor)
        if fontsize:
            resp.set_cookie('fontsize', fontsize)
        if fontfamily:
            resp.set_cookie('fontfamily', fontfamily)
        return resp
    color = request.cookies.get('color')
    bgcolor = request.cookies.get('bgcolor')
    fontsize = request.cookies.get('fontsize')
    fontfamily = request.cookies.get('fontfamily')
    resp = make_response(render_template('lab3/settings.html',color=color, bgcolor=bgcolor, fontsize=fontsize, fontfamily=fontfamily))
    return resp


from flask import request, render_template, redirect
import datetime

@lab3.route('/lab3/ticket', methods=['GET', 'POST'])
def ticket():
    if request.method == 'GET':
        return render_template('lab3/ticket_form.html')
    fio = request.form.get('fio')
    shelf = request.form.get('shelf')
    linen = request.form.get('linen') == 'on'
    luggage = request.form.get('luggage') == 'on'
    age = request.form.get('age')
    departure = request.form.get('departure')
    destination = request.form.get('destination')
    date = request.form.get('date')
    insurance = request.form.get('insurance') == 'on'
    errors = []
    if not fio or not fio.strip():
        errors.append("ФИО пассажира обязательно")
    if not shelf:
        errors.append("Выберите полку")
    if not age:
        errors.append("Возраст обязателен")
    elif not age.isdigit() or int(age) < 1 or int(age) > 120:
        errors.append("Возраст должен быть от 1 до 120 лет")
    if not departure or not departure.strip():
        errors.append("Пункт выезда обязателен")
    if not destination or not destination.strip():
        errors.append("Пункт назначения обязателен")
    if not date:
        errors.append("Дата поездки обязательна")
    if errors:
        return render_template('lab3/ticket_form.html', 
                             errors=errors, fio=fio, shelf=shelf, 
                             linen=linen, luggage=luggage, age=age,
                             departure=departure, destination=destination, 
                             date=date, insurance=insurance)
    age_int = int(age)
    is_child = age_int < 18
    if is_child:
        price = 700
    else:
        price = 1000
    if shelf in ['lower', 'lower_side']:
        price += 100
    if linen:
        price += 75
    if luggage:
        price += 250
    if insurance:
        price += 150
    return render_template('lab3/ticket_result.html',
                         fio=fio, shelf=shelf, linen=linen,
                         luggage=luggage, age=age, is_child=is_child,
                         departure=departure, destination=destination,
                         date=date, insurance=insurance, price=price,
                         timestamp=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))

@lab3.route('/lab3/clear_cookies')
def clear_cookies():
    """Очистка всех куки настроек"""
    resp = redirect('/lab3/settings')
    resp.set_cookie('color', '', expires=0)
    resp.set_cookie('bgcolor', '', expires=0)
    resp.set_cookie('fontsize', '', expires=0)
    resp.set_cookie('fontfamily', '', expires=0)
    return resp