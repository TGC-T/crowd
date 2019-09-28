from flask import Flask
from flask import render_template
from flask import request
from json import dumps as json
from datetime import datetime
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


def addcrowdposttodb(name: str, description: str, amounttoget: float):
    '''
    Добавляет краудфанд в базу с нулевым балансом
    '''
    post = {'name': name, 'description': description, 'amounttoget': amounttoget,
            'wegot': 0, 'iscomplete': False}
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
    #post = {'name':name, 'description': description, 'amounttoget': amounttoget, 'wegot':0, 'iscomplete':False, my_id: 4}
    name = request.args.get('name')
    description = request.args.get('description')
    amounttoget = request.args.get('amounttoget')
    addcrowdposttodb(name, description, int(amounttoget))
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
                'amounttoget': i['amounttoget'], 'wegot': i['wegot']}
        result.append(post)
    return 
def getTop3Crowd():
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    posts = []
    count = 2
    for i in collection.find({}):
        posts.append({'name': i['name'], 'description': i['description'], '_id': i['_id']})
        if count == 0:
            break
        count -= 1
    return posts


@app.route('/')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Домашняя страница',
        year=datetime.now().year,
        posts = getTop3Crowd()
    )
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Контакты',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='О нас',
        year=datetime.now().year,
        message='Описание страницы'
    )
def showComments(crowdObject_id):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    collection = client.comments.forum
    comments = []
    for i in collection.find({'crowdid':crowdObject_id}):
        comments.append(i)
    return comments

@app.route('/crowd/<id_str>')
def showCrowd(id_str):
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    crowd_id = ObjectId(id_str)
    finded = collection.find_one({"_id": crowd_id})
    return render_template('crowd.html',comments = showComments(crowd_id),title = finded['name'], name=finded['name'], description=finded['description'], need=finded['amounttoget'], wegot=finded['wegot'], persent = int(finded['wegot']/finded['amounttoget'] * 100))

    


app.run(debug=True, host="0.0.0.0")
