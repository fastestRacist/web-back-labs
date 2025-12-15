from flask import Blueprint, render_template, request, make_response, redirect, session, current_app, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path
from db import db
from db.models import users, articles

from datetime import datetime
from lab5 import db_close, db_connect

lab8 = Blueprint('lab8', __name__)


@lab8.route('/lab8/')
def lab():
    return render_template('lab8/lab8.html', login = session.get('login'))


@lab8.route('/lab8/register/', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')

    login_exists = users.query.filter_by(login = login_form).first()
    
    if login_form:
        login_form = login_form.strip()
    if password_form:
        password_form = password_form.strip()
    #проверка на пустоту в логине и пароле
    if not login_form or not password_form:
        return render_template('lab8/register.html',
                               error = 'Введите логин и пароль')
    if login_exists:
        return render_template('lab8/register.html',
                               error = 'Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login = login_form, password = password_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/lab8')