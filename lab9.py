from flask import Blueprint, render_template, jsonify, session
from flask_login import current_user, login_required
from db import db
from db.models import GiftBox

lab9 = Blueprint('lab9', __name__)

CONGRATS = {
    1: "Пусть все у вас получится!",
    2: "Да прибудет с вами сила!",
    3: "С Новым Годом!",
    4: "Цените близких!",
    5: "Праздник к нам приходит!",
    6: "С Новым Счастьем!",
    7: "Еще один год позади!",
    8: "Расскажи дедушке стишок!",
    9: "Веди себя хорошо!",
    10: "Ледники растают!"
}

#коробки, доступные только тем кто вошел
LOGIN_ONLY = {8, 9, 10}


@lab9.route('/lab9/')
def index():
    boxes = GiftBox.query.order_by(GiftBox.id).all()
    opened_left = sum(1 for b in boxes if not b.opened)
    return render_template(
        'lab9/index.html',
        boxes=boxes,
        opened_left=opened_left,
        user=current_user
    )


@lab9.route('/lab9/open/<int:box_id>', methods=['POST'])
def open_box(box_id):
    box = GiftBox.query.get_or_404(box_id)

    #Проверка авторизации для специальных коробок
    if box_id in LOGIN_ONLY and not current_user.is_authenticated:
        return jsonify({'status': 'auth_required'})
    #Список открытых коробок для текущего пользователя
    user_key = f"opened_boxes_user_{current_user.get_id() if current_user.is_authenticated else 'guest'}"
    opened = session.get(user_key, [])
    if box_id in opened:
        return jsonify({'status': 'already_opened'})
    #Лимит 3 коробки на пользователя
    if len(opened) >= 3:
        return jsonify({'status': 'limit'})
    #Если коробка уже глобально открыта, показываем содержимое
    status = 'ok' if not box.opened else 'empty'

    return jsonify({
        'status': status,
        'gift_img': f'/static/lab9/gift{box.id}.png',
        'text': CONGRATS.get(box.id, 'Поздравление!')
    })


@lab9.route('/lab9/take/<int:box_id>', methods=['POST'])
def take_gift(box_id):
    box = GiftBox.query.get_or_404(box_id)
    #Если коробка ещё не открыта глобально, помечаем её как открытую
    if not box.opened:
        box.opened = True
        db.session.commit()

    user_key = f"opened_boxes_user_{current_user.get_id() if current_user.is_authenticated else 'guest'}"
    opened = session.get(user_key, [])
    if box_id not in opened:
        opened.append(box_id)
        session[user_key] = opened

    return jsonify({'status': 'taken'})


@lab9.route('/lab9/reset', methods=['POST'])
def reset_boxes():
    #Только для авторизованных пользователей
    if not current_user.is_authenticated:
        return jsonify({'status': 'auth_required'}), 401
    #Сбрасываем глобальный статус коробок
    GiftBox.query.update({GiftBox.opened: False})
    db.session.commit()
    #Сбрасываем индивидуальные открытые коробки для текущего пользователя
    user_key = f"opened_boxes_user_{current_user.get_id()}"
    session[user_key] = []

    return jsonify({'status': 'reset'})