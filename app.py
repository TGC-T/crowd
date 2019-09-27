from flask import Flask
from flask import render_template
from flask import request
from json import dumps as json
app = Flask(__name__)


def addcrowdposttodb(name: str, description: str, amounttoget: float, urgency: int):
    '''
    Добавляет краудфанд в базу с нулевым балансом
    '''
    post = {'name': name, 'description': description, 'amounttoget': amounttoget,
            'wegot': 0, 'urgency': urgency, 'iscomplete': False}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    post_id = collection.insert_one(post)
    return post_id


def registerUser(email: str, pwhash: str, fio: str):
    '''
    регистрация пользователя
    '''
    post = {'email': email, 'pwhash': pwhash, 'fio': fio}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    post_id = collection.insert_one(post)
    return post_id


def checkUser(email: str, pwhash: str):
    '''
    проверка сущ пользьзователя
    '''
    post = {'email': email, 'pwhash': pwhash}
    from pymongo import MongoClient
    print(post)
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    finded = collection.find_one(post)
    if finded is None:
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
        return json({'Result': False, 'What': 'Пользователь уже существуют'})
    return json({'Result': True, 'What': None})


@app.route('/api/user/login')
def userLogin():
    # url /user/login?email=example@example.com&pwhash=AAAAAAAAAA
    email = request.args.get('email')
    pwhash = request.args.get('pwhash')
    if checkUser(email, pwhash):
        return json({'Result': True, 'What': None})
    return json({'Result': False, 'What': 'Неверный пароль'})


@app.route('/api/crowd/add')
def addCrowd():
    #post = {'name':name, 'description': description, 'amounttoget': amounttoget, 'wegot':0, 'urgency':urgency, 'iscomplete':False}
    name = request.args.get('name')
    description = request.args.get('description')
    amounttoget = request.args.get('amounttoget')
    urgency = request.args.get('amounttoget')
    addcrowdposttodb(name, description, int(amounttoget), int(urgency))
    return json({"Result": True, "What": None})


@app.route('/api/crowd/modify/<field>')
def modCrowd(field):
    # /api/crowd/modify/name?old=Test&new=Test1
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    find = {field: request.args.get('old')}
    newvalue = {"$set": {field: request.args.get('new')}}
    collection.update_one(find, newvalue)
    return json({"Result": True, "What": None})

# @app.route('/api/crowd/get/<field>')
# def getCrowd(field):
#     from pymongo import MongoClient
#     client = MongoClient('localhost', 27017)
#     db = client.posts
#     collection = db.tasks


app.run(debug=True, host="0.0.0.0")
