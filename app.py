from flask import Flask
from flask import render_template
from flask import request
from json import dumps as json
app = Flask(__name__)



def addcrowdposttodb(name:str, description:str, amounttoget:float, urgency:int):
    '''
    Добавляет краудфанд в базу с нулевым балансом
    '''
    post = {'name':name, 'description': description, 'amounttoget': amounttoget, 'wegot':0, 'urgency':urgency, 'iscomplete':False}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    post_id = collection.insert_one(post)
    return post_id

def modcrowdpost(post_id, update_money):
    '''
    Изменяет кол-во полученных сейчас денег
    '''
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    collection.update_one(post_id, {'wegot':update_money})

def registerUser(email:str, pwhash:str, fio:str):
    '''
    регистрация пользователя
    '''
    post = {'email': email, 'pwhash': pwhash, 'fio' : fio}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    post_id = collection.insert_one(post)
    return post_id

def checkUser(email:str, pwhash:str):
    '''
    проверка сущ пользьзователя
    '''
    post = {'email': email, 'pwhash': pwhash}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    finded = collection.find_one(post)
    if  finded is None:
        return False
    else:
        if finded['pwhash'] != pwhash:
            return False
        return True

@app.route('/api/user/register')
def userRegister():
    # url /user/register?email=example@example.com&pwhash=AAAAAAAAAA&fio=ArthurKhakimovMarathovich
    email = request.args.get('email')
    pwhash = request.args.get('pwhash')
    fio = request.args.get('fio')
    try:
        registerUser(email, pwhash, fio)
    except Exception:
        return json({'Result' : False, 'What' : 'Пользователь уже существуют'})
    return json({'Result' : True, 'What' : None})
@app.route('/api/user/login')
def userLogin():
    # url /user/login?email=example@example.com&pwhash=AAAAAAAAAA
    email = request.args.get('email')
    pwhash = request.args.get('pwhash')
    if checkUser(email, pwhash):
        return True
    return False

# @app.route()
app.run()