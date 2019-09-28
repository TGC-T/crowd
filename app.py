from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
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


def addcrowdposttodb(name: str, description: str, org: str, amounttoget: float):
    '''
    Добавляет краудфанд в базу с нулевым балансом
    '''
    post = {'name': name, 'description': description, 'amounttoget': amounttoget, 'org': org,
            'wegot': 0, 'iscomplete': False}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    post_id = collection.insert_one(post)
    return post_id


def registerUser(email: str, password: str, fio: str):
    '''
    регистрация пользователя
    '''
    post = {'email': email, 'password': password, 'fio': fio}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    post_id = collection.insert_one(post)
    return post_id


def checkUser(email: str, password: str):
    '''
    проверка сущ пользьзователя
    '''
    post = {'email': email, 'password': password}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    finded = collection.find_one(post)
    if finded == None:
        return False
    if finded['password'] != password:
        return False
    return True


def findUser(email):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    name = {'email': email}
    return collection.find_one(name) is not None


@app.route('/api/user/register')
def userRegister():
    # url /user/register?email=example@example.com&password=AAAAAAAAAA&fio=ArthurKhakimovMarathovich
    email = request.args.get('email')
    password = request.args.get('password')
    fio = request.args.get('fio')
    if checkInput(fio.split()[0], fio.split()[1], email) != True:
        return json({'Result': False, 'What': 'Пользователь уже существуеют'})
    if findUser(email):
        return json({'Result': False, 'What': 'Пользователь уже существуеют'})
    try:
        registerUser(email, password, fio)
    except Exception:
        return json({'Result': False, 'What': 'Пользователь уже существуют'})
    return json({'Result': True, 'What': None})


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if checkUser(request.form['username'], request.form['password']) != True:
            error = 'Неверные авторизация.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error, year=datetime.now().year)

def addCrowd(name,description,amounttoget,org):
    #post = {'name':name, 'description': description, 'amounttoget': amounttoget, 'wegot':0, 'iscomplete':False, my_id: 4}
    name = request.args.get('name')
    description = request.args.get('description')
    amounttoget = request.args.get('amounttoget')
    org = request.args.get('obj')
    addcrowdposttodb(name, description, org, amounttoget)
    


@app.route('/crowd/add', methods=['GET', 'POST'])
def crowdForm():
    if request.method == 'POST':
        addCrowd(request.form['name'],request.form['description'],request.form['amounttoget'],request.form['org'])
        return redirect(url_for('home'))
    return render_template('crowdform.html', year=datetime.now().year)


@app.route('/api/crowd/set/<object_id>')
def modCrowd(object_id):
    # /api/crowd/set/name?field=name&new=Example
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    field = request.args.get('field')
    new = request.args.get('new')
    collection.find_one_and_update(
        {'_id': ObjectId(object_id)}, {'$set': {field: new}})


@app.route('/api/crowd/get/<object_id>')
def getCrowd(object_id):
    #/api/crowd/get/name?value=Test
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    finded = collection.find_one({'_id': ObjectId(object_id)})
    finded['_id'] = str(finded['_id'])
    return json(finded)


@app.route('/api/crowd/getall')
def getall():
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    result = []
    for i in collection.find({}):
        post = {'name': i['name'], 'description': i['description'],
                'amounttoget': i['amounttoget'], 'wegot': i['wegot'], '_id': i['_id'], 'org': i['org']}
        result.append(post)
    return render_template('getall.html', posts=result, title="Список всех краудов")


def getTop3Crowd():
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    posts = []
    count = 2
    for i in collection.find({}):
        posts.append(
            {'name': i['name'], 'description': i['description'], '_id': i['_id']})
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
        posts=getTop3Crowd()
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
    for i in collection.find({'crowdid': crowdObject_id}):
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
    return render_template('crowd.html', year=datetime.now().year, comments=showComments(crowd_id), title=finded['name'], name=finded['name'], description=finded['description'], need=finded['amounttoget'], wegot=finded['wegot'], persent=int(finded['wegot']/finded['amounttoget'] * 100))


app.run(debug=True, host="0.0.0.0")
