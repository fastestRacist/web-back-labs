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
    resp.delete_cookie('color')
    resp.delete_cookie('bgcolor')
    resp.delete_cookie('fontsize')
    resp.delete_cookie('fontfamily')
    return resp


@lab3.route('/lab3/car')
def car():
    cars = [
        {"name": "Camry", "brand": "Toyota", "price": 2500000, "country": "Япония", "body_type": "Седан"},
        {"name": "Corolla", "brand": "Toyota", "price": 1800000, "country": "Япония", "body_type": "Седан"},
        {"name": "RAV4", "brand": "Toyota", "price": 2800000, "country": "Япония", "body_type": "Кроссовер"},
        {"name": "3 Series", "brand": "BMW", "price": 3500000, "country": "Германия", "body_type": "Седан"},
        {"name": "X5", "brand": "BMW", "price": 5500000, "country": "Германия", "body_type": "Внедорожник"},
        {"name": "A4", "brand": "Audi", "price": 3200000, "country": "Германия", "body_type": "Седан"},
        {"name": "Q7", "brand": "Audi", "price": 5200000, "country": "Германия", "body_type": "Внедорожник"},
        {"name": "Civic", "brand": "Honda", "price": 1900000, "country": "Япония", "body_type": "Седан"},
        {"name": "CR-V", "brand": "Honda", "price": 2600000, "country": "Япония", "body_type": "Кроссовер"},
        {"name": "Solaris", "brand": "Hyundai", "price": 1200000, "country": "Южная Корея", "body_type": "Седан"},
        {"name": "Creta", "brand": "Hyundai", "price": 1600000, "country": "Южная Корея", "body_type": "Кроссовер"},
        {"name": "Logan", "brand": "Renault", "price": 900000, "country": "Франция", "body_type": "Седан"},
        {"name": "Duster", "brand": "Renault", "price": 1400000, "country": "Франция", "body_type": "Внедорожник"},
        {"name": "Focus", "brand": "Ford", "price": 1500000, "country": "США", "body_type": "Седан"},
        {"name": "Kuga", "brand": "Ford", "price": 2200000, "country": "США", "body_type": "Кроссовер"},
        {"name": "Vesta", "brand": "Lada", "price": 800000, "country": "Россия", "body_type": "Седан"},
        {"name": "XRAY", "brand": "Lada", "price": 950000, "country": "Россия", "body_type": "Кроссовер"},
        {"name": "Octavia", "brand": "Skoda", "price": 1700000, "country": "Чехия", "body_type": "Седан"},
        {"name": "Kodiaq", "brand": "Skoda", "price": 2400000, "country": "Чехия", "body_type": "Внедорожник"},
        {"name": "Model 3", "brand": "Tesla", "price": 4200000, "country": "США", "body_type": "Седан"},
        {"name": "Model Y", "brand": "Tesla", "price": 4800000, "country": "США", "body_type": "Кроссовер"},
        {"name": "Rio", "brand": "Kia", "price": 1300000, "country": "Южная Корея", "body_type": "Седан"},
        {"name": "Sportage", "brand": "Kia", "price": 2300000, "country": "Южная Корея", "body_type": "Кроссовер"},
        {"name": "Polo", "brand": "Volkswagen", "price": 1400000, "country": "Германия", "body_type": "Седан"},
        {"name": "Tiguan", "brand": "Volkswagen", "price": 2700000, "country": "Германия", "body_type": "Кроссовер"}
    ]

    # --- Кнопка сброса: очищаем куки и возвращаем все автомобили
    if request.args.get('clear'):
        resp = make_response(redirect('/lab3/car'))
        resp.delete_cookie('car_min_price')
        resp.delete_cookie('car_max_price')
        return resp

    # --- Получаем значения из формы или куки
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    # Если поля пустые — не сохраняем в куки, просто очищаем их
    if request.args.get('min_price') is not None or request.args.get('max_price') is not None:
        resp = make_response(redirect('/lab3/car'))
        if min_price:
            resp.set_cookie('car_min_price', min_price)
        else:
            resp.delete_cookie('car_min_price')
        if max_price:
            resp.set_cookie('car_max_price', max_price)
        else:
            resp.delete_cookie('car_max_price')
        return resp

    # --- Если пользователь не отправил форму, подставляем значения из куки
    if not min_price:
        min_price = request.cookies.get('car_min_price')
    if not max_price:
        max_price = request.cookies.get('car_max_price')

    # --- Определяем диапазон цен для плейсхолдеров
    min_possible_price = min(car['price'] for car in cars)
    max_possible_price = max(car['price'] for car in cars)

    # --- Преобразуем введённые значения в числа
    def to_int_or_none(val):
        try:
            return int(val) if val not in (None, '') else None
        except ValueError:
            return None

    min_val = to_int_or_none(min_price)
    max_val = to_int_or_none(max_price)

    # --- Если значения перепутаны — поменяем местами и отобразим корректно в форме
    if min_val is not None and max_val is not None and min_val > max_val:
        min_val, max_val = max_val, min_val
        min_price, max_price = str(min_val), str(max_val)

    # --- Фильтрация списка
    if min_val is None and max_val is None:
        filtered_cars = cars
    else:
        filtered_cars = [
            car for car in cars
            if (min_val is None or car['price'] >= min_val)
            and (max_val is None or car['price'] <= max_val)
        ]

    # --- Если ничего не найдено — сообщение
    message = None
    if not filtered_cars:
        message = "Не найдено ни одного автомобиля"

    return render_template('lab3/car.html', cars=filtered_cars, min_price=min_price or '', max_price=max_price or '',
        min_possible_price=min_possible_price, max_possible_price=max_possible_price, message=message, count=len(filtered_cars))
