from flask import Flask
from flask import render_template
from flask import request
from json import dumps as json
app = Flask(__name__)


def checkInput(FirstName, LastName, Email):
    IncorrectInput = []

    if not FirstName.isalpha() or not 0 <= len(FirstName):
        IncorrectInput.append('FirstName')

    if 0 <= len(LastName):
        for LastNames in LastName.split('-', 1):
            if not LastNames.isalpha():
                IncorrectInput.append('LastName')
                break
    else:
        IncorrectInput.append('LastName')

    if not '@' in Email:
        IncorrectInput.append('Email')

    if (len(IncorrectInput) == 0):
        return True
    return IncorrectInput

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

def findUser(email):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    name = {'email' : email}
    return collection.find_one(name) is not None
        

@app.route('/api/user/register')
def userRegister():
    # url /user/register?email=example@example.com&pwhash=AAAAAAAAAA&fio=ArthurKhakimovMarathovich
    email = request.args.get('email')
    pwhash = request.args.get('pwhash')
    fio = request.args.get('fio')
    if checkInput(fio.split()[0],fio.split()[1], email) != True:
        return json({'Result': False, 'What':'Пользователь уже существуеют'})
    if findUser(email):
        return json({'Result': False, 'What':'Пользователь уже существуеют'})
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


@app.route('/api/crowd/set/<field>')
def modCrowd(field):
    # /api/crowd/set/name?old=Test&new=Test1
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    find = {field: request.args.get('old')}
    newvalue = {"$set": {field: request.args.get('new')}}
    collection.update_one(find, newvalue)
    return json({"Result": True, "What": None})


@app.route('/api/crowd/get/<field>')
def getCrowd(field):
    #/api/crowd/get/name?value=Test
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    post = {field: request.args.get('value')}
    collection.find_one()
    return str(collection.find_one(post))


@app.route('/api/crowd/getall')
def getall():
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    result = []
    for i in collection.find({}):
        post = {'name': i['name'], 'description': i['description'],
                'amounttoget': i['amounttoget'], 'wegot': i['wegot'], 'urgency': i['urgency']}
        result.append(post)
    return json(result)


app.run(debug=True, host="0.0.0.0")
