from flask import Blueprint, request, session, current_app, render_template
import re
from lab5 import db_connect, db_close
from werkzeug.security import generate_password_hash, check_password_hash

rgz = Blueprint('rgz', __name__)

@rgz.route('/rgz/')
def main():
    """Главная страница — просто HTML, весь функционал через JSON-RPC"""
    return render_template('rgz/books.html', login=session.get('login'), is_admin=session.get('is_admin', False))

@rgz.route('/rgz/json-rpc-api/', methods=['POST'])
def api():
    """Полностью JSON-RPC API для всех действий"""
    data = request.json
    id_ = data.get('id')
    method = data.get('method')
    params = data.get('params', {})

    # ===== GET BOOKS =====
    if method == 'get_books':
        page = int(params.get('page', 1))
        limit = 20
        title = params.get('title','').strip()
        author = params.get('author','').strip()
        publisher = params.get('publisher','').strip()
        min_pages = params.get('min_pages')
        max_pages = params.get('max_pages')
        sort_by = params.get('sort_by','id')
        sort_order = params.get('sort_order','asc')

        allowed_fields = ['id','title','author','pages','publisher']
        if sort_by not in allowed_fields: sort_by='id'
        if sort_order not in ['asc','desc']: sort_order='asc'

        conn, cur = db_connect()
        query = "SELECT * FROM rgz_books WHERE 1=1"
        qparams = []

        if title:
            query += " AND title LIKE ?"
            qparams.append(f"%{title}%")
        if author:
            query += " AND author LIKE ?"
            qparams.append(f"%{author}%")
        if publisher:
            query += " AND publisher LIKE ?"
            qparams.append(f"%{publisher}%")
        if min_pages:
            query += " AND pages >= ?"
            qparams.append(int(min_pages))
        if max_pages:
            query += " AND pages <= ?"
            qparams.append(int(max_pages))

        query += f" ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        qparams.extend([limit, (page-1)*limit])
        cur.execute(query, qparams)
        rows = cur.fetchall()

        books = []
        for r in rows:
            books.append({
                'id': r['id'],
                'title': r['title'],
                'author': r['author'],
                'pages': r['pages'],
                'publisher': r['publisher'],
                'image': f"/static/rgz/{r['id']}.jpg"
            })

        # общее количество
        count_query = "SELECT COUNT(*) as cnt FROM rgz_books WHERE 1=1"
        count_params = []
        if title: count_query += " AND title LIKE ?"; count_params.append(f"%{title}%")
        if author: count_query += " AND author LIKE ?"; count_params.append(f"%{author}%")
        if publisher: count_query += " AND publisher LIKE ?"; count_params.append(f"%{publisher}%")
        if min_pages: count_query += " AND pages >= ?"; count_params.append(int(min_pages))
        if max_pages: count_query += " AND pages <= ?"; count_params.append(int(max_pages))
        cur.execute(count_query, count_params)
        total = cur.fetchone()['cnt']

        db_close(conn, cur)
        return {'jsonrpc':'2.0','result':{'books':books,'page':page,'total_pages':(total+limit-1)//limit},'id':id_}

    # ===== REGISTER =====
    if method == 'register':
        login = params.get('login','').strip()
        password = params.get('password','').strip()
        if not re.match(r'^[a-zA-Z0-9._-]{3,50}$', login):
            return {'jsonrpc':'2.0','error':{'code':1,'message':'Неверный логин'},'id':id_}
        if len(password)<6:
            return {'jsonrpc':'2.0','error':{'code':2,'message':'Пароль слишком короткий'},'id':id_}

        conn, cur = db_connect()
        cur.execute("SELECT id FROM rgz_users WHERE login=?", (login,))
        if cur.fetchone():
            db_close(conn, cur)
            return {'jsonrpc':'2.0','error':{'code':3,'message':'Пользователь существует'},'id':id_}
        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO rgz_users (login,password,is_admin) VALUES (?,?,?)",(login,hashed,0))
        conn.commit()
        db_close(conn, cur)
        session['login']=login
        session['is_admin']=False
        return {'jsonrpc':'2.0','result':{'login':login,'is_admin':False},'id':id_}

    # ===== LOGIN =====
    if method=='login':
        login=params.get('login','').strip()
        password=params.get('password','').strip()
        conn, cur=db_connect()
        cur.execute("SELECT * FROM rgz_users WHERE login=?",(login,))
        user = cur.fetchone()
        db_close(conn, cur)
        if not user or not check_password_hash(user['password'], password):
            return {'jsonrpc':'2.0','error':{'code':1,'message':'Неверный логин/пароль'},'id':id_}
        session['login']=login
        session['is_admin']=bool(user['is_admin'])
        return {'jsonrpc':'2.0','result':{'login':login,'is_admin':bool(user['is_admin'])},'id':id_}

    # ===== LOGOUT =====
    if method=='logout':
        session.pop('login',None)
        session.pop('is_admin',None)
        return {'jsonrpc':'2.0','result':'success','id':id_}

    # ===== DELETE ACCOUNT =====
    if method=='delete_account':
        login=session.get('login')
        if not login: return {'jsonrpc':'2.0','error':{'code':1,'message':'Не авторизован'},'id':id_}
        conn, cur=db_connect()
        cur.execute("SELECT is_admin FROM rgz_users WHERE login=?",(login,))
        user=cur.fetchone()
        if user['is_admin']:
            db_close(conn,cur)
            return {'jsonrpc':'2.0','error':{'code':2,'message':'Нельзя удалить админа'},'id':id_}
        cur.execute("DELETE FROM rgz_users WHERE login=?",(login,))
        conn.commit()
        db_close(conn,cur)
        session.pop('login',None)
        session.pop('is_admin',None)
        return {'jsonrpc':'2.0','result':'success','id':id_}

    # ===== USER INFO =====
    if method=='get_user_info':
        return {'jsonrpc':'2.0','result':{'is_authenticated':bool(session.get('login')),'login':session.get('login'),'is_admin':session.get('is_admin',False)},'id':id_}

    # ===== ADMIN CRUD =====
    if method in ['add_book','update_book','delete_book']:
        if not session.get('is_admin'): return {'jsonrpc':'2.0','error':{'code':1,'message':'Только для админа'},'id':id_}
        conn, cur = db_connect()
        if method=='add_book':
            title=params['title']; author=params['author']; pages=int(params['pages']); publisher=params['publisher']
            if pages<=0: return {'jsonrpc':'2.0','error':{'code':2,'message':'Страницы>0'},'id':id_}
            cur.execute("INSERT INTO rgz_books (title,author,pages,publisher) VALUES (?,?,?,?)",(title,author,pages,publisher))
        elif method=='update_book':
            book_id=int(params['id']); title=params['title']; author=params['author']; pages=int(params['pages']); publisher=params['publisher']
            if pages<=0: return {'jsonrpc':'2.0','error':{'code':2,'message':'Страницы>0'},'id':id_}
            cur.execute("UPDATE rgz_books SET title=?,author=?,pages=?,publisher=? WHERE id=?",(title,author,pages,publisher,book_id))
        else:  # delete_book
            book_id=int(params)
            cur.execute("DELETE FROM rgz_books WHERE id=?",(book_id,))
        conn.commit()
        db_close(conn,cur)
        return {'jsonrpc':'2.0','result':'success','id':id_}

    # ===== METHOD NOT FOUND =====
    return {'jsonrpc':'2.0','error':{'code':-32601,'message':'Method not found'},'id':id_}
