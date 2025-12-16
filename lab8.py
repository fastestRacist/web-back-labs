from flask import Blueprint, render_template, request, make_response, redirect, session, current_app, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import func

from datetime import datetime

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
    #сразу вход после регистрации
    login_user(new_user, remember=False)

    return redirect('/lab8')


@lab8.route('/lab8/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember_form = request.form.get('remember')

    if login_form:
        login_form = login_form.strip()
    if password_form:
        password_form = password_form.strip()
    #проверка на пустоту в логине и пароле
    if not login_form or not password_form:
        return render_template('lab8/login.html',
                               error = 'Введите логин и пароль')

    user = users.query.filter_by(login = login_form).first()

    if user:
        if check_password_hash(user.password, password_form):
            if remember_form == 'on':
                login_user(user, remember = True)
            else:
                login_user(user, remember = False)
            return redirect('/lab8/')
        
    return render_template('/lab8/login.html',
                           error = 'Ошибка входа: логин и/или пароль неверны')



@lab8.route('/lab8/list')
@login_required
def article_list():
    all_articles = articles.query.filter_by(login_id=current_user.id).order_by(articles.id.desc()).all()
    return render_template('/lab8/articles.html', articles=all_articles)


@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')


@lab8.route('/lab8/create', methods = ['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('lab8/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'

    if not title or not article_text:
        error_msg = ""
        if not title and not article_text:
            error_msg = "Заполните название и текст статьи"
        elif not title:
            error_msg = "Заполните название статьи"
        elif not article_text:
            error_msg = "Заполните текст статьи"
        
        return render_template('lab8/create_article.html', error=error_msg, title=title, article_text=article_text)

    user = current_user
        
        # Создаем новую статью
    new_article = articles(login_id=user.id, 
                           title=title,
                           article_text=article_text, 
                           is_public=is_public)
    
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8')


@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    #поиск статьи
    article = articles.query.filter_by(id=article_id,login_id=current_user.id).first()
    
    if request.method == 'GET':
        return render_template('lab8/edit_article.html', article=article)
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    #проверка
    if not title or not article_text:
        return render_template('lab8/edit_article.html', 
                              article=article, 
                              error='Заполните название и текст статьи')
    #обновление статьи
    article.title = title
    article.article_text = article_text
    article.is_public = is_public

    db.session.commit()
    
    return redirect('/lab8/list')


@lab8.route('/lab8/delete/<int:article_id>')
@login_required
def delete_article(article_id):

    article = articles.query.filter_by(id=article_id,login_id=current_user.id).first()
    
    db.session.delete(article)
    db.session.commit()
    
    return redirect('/lab8/list')


@lab8.route('/lab8/public')
def public_articles():
    public_articles = articles.query.filter_by(is_public=True).join(
        users, articles.login_id == users.id).add_columns(articles.id, articles.title, articles.article_text,
        articles.is_public, users.login.label('author')).order_by(articles.id.desc()).all()
    
    return render_template('lab8/public_articles.html', articles=public_articles, login=session.get('login'))


@lab8.route('/lab8/search')
@login_required
def search_my_articles():
    search = request.args.get('search', '').strip()

    #если строка поиска пустая — возвращаемся к списку
    if not search:
        return redirect('/lab8/list')

    found_articles = articles.query.filter(
    articles.login_id == current_user.id,
    articles.title.ilike(f'%{search}%')
    ).order_by(articles.id.desc()).all()

    return render_template(
        'lab8/search_results.html',
        search=search,
        articles=found_articles
    )


@lab8.route('/lab8/public_search')
def search_public_articles():
    search = request.args.get('search', '').strip()

    if not search:
        return redirect('/lab8/public')

    found_articles = articles.query.filter(
    articles.is_public == True,
    articles.title.ilike(f'%{search}%')
    ).join(users, articles.login_id == users.id).add_columns(
        articles.id,
        articles.title,
        articles.article_text,
        articles.is_public,
        users.login.label('author')
    ).order_by(articles.id.desc()).all()

    return render_template(
        'lab8/public_search_results.html',
        search=search,
        articles=found_articles
    )