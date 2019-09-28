from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import make_response
from json import dumps as json
from datetime import datetime
app = Flask(__name__)



def addcrowdposttodb(name: str, description: str, org: str, amounttoget: float, donate:str):
    '''
    Добавляет краудфанд в базу с нулевым балансом
    '''
    post = {'name': name, 'description': description, 'donate':donate , 'amounttoget': amounttoget, 'org': org,
            'wegot': 0, 'iscomplete': False}
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    post_id = collection.insert_one(post)
    return post_id


@app.route('/register',methods=['GET', 'POST'])
def userRegister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fio = request.form['fio']
        post = {'usermail': username, 'fio': fio, 'password': password, 'isadmin':False}
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017)
        db = client.webusers
        collection = db.users
        collection.insert_one(post)
        return redirect('/login')
    return render_template('register.html', title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017)
        db = client.webusers
        post = {'username' : request.form['username']}
        collection = db.users
        finded = collection.find_one(post)
        resp = make_response(redirect(url_for('personal')))
        resp.set_cookie('str_id', str(finded['_id']), max_age=60)
        return resp
    return render_template('login.html',title = 'Вход', error=error, year=datetime.now().year)

@app.route('/personal')
def personal():
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    str_id = request.cookies.get('str_id')
    finded = collection.find_one({'_id': ObjectId(str_id)})
    return render_template('personal_account.html', username = str(finded['fio']))


def addCrowd(name,description,amounttoget,org,donate):
    addcrowdposttodb(name, description, org, int(amounttoget),donate)
    


@app.route('/crowd/add', methods=['GET', 'POST'])
def crowdForm():
    if request.method == 'POST':
        addCrowd(request.form['name'], request.form['description'],
                 request.form['amounttoget'], request.form['org'], request.form['donate'])
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

@app.route('/api/crowd/inc/<object_id>')
def incMoney(object_id):
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    # /api/crowd/set/object_id?more=Example
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.tasks
    more = request.args.get('more')
    collection.find_one_and_update({'_id': ObjectId(object_id)}, {'$inc': {'wegot': more}})
    finded = collection.find_one({'_id': ObjectId(object_id)})
    if finded['wegot'] >= finded['amounttoget']:
        collection.update_one({'_id': ObjectId(object_id)}, {'$set': {'iscomplete': True}})
    


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
                'amounttoget': i['amounttoget'], 'wegot': i['wegot'], '_id': i['_id'], 'org': i['org'], 'persent':int(i['wegot']/i['amounttoget'] * 100)}
        result.append(post)
    return render_template('getall.html', year=datetime.now().year, posts=result, title="Список всех краудов")


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

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        from bson.objectid import ObjectId
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017)
        db = client.posts
        collection = db.tasks
        name = request.form['search']
        result = []
        for i in collection.find({}):
            post = {'name': i['name'], 'description': i['description'],
                'amounttoget': i['amounttoget'], 'wegot': i['wegot'], '_id': i['_id'], 'org': i['org'], 'persent':int(i['wegot']/i['amounttoget'] * 100)}
            if name in post['name']:
                result.append(post)
        return render_template('search.html', posts = result,
                               title='Поиск', year=datetime.now().year)
    return render_template('search.html', title='Поиск', year=datetime.now().year)
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
    return render_template('crowd.html', importance=finded['importance'], donate=finded['donate'], 
    year=datetime.now().year, comments=showComments(crowd_id), title=finded['name'], name=finded['name'], 
    description=finded['description'], need=finded['amounttoget'], wegot=finded['wegot'], 
    persent=int(finded['wegot']/finded['amounttoget'] * 100)
    )

@app.route('/api/payments/')
def setPayments():
    #/app/payments/<id_str>?crowd_id=example_id
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.payments
    crowd_id = request.args.get('crowd_id')
    user_id = request.args.get('user_id')
    amount = float(request.args.get('payment'))
    post = {'crowd_id':crowd_id, 'user_id':user_id, 'payment':amount}
    return str(collection.insert_one(post).inserted_id)

@app.route('/api/crowd/<crowd_id_str>')
def getPayments(crowd_id_str):
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.posts
    collection = db.payments
    link = []
    for i in collection.find({'crowd_id':crowd_id_str}):
        link.append(i)
    return render_template('payments.html', )
    
@app.route('/api/account/<id_str>')
def getAccount(id_str):
    from bson.objectid import ObjectId
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.webusers
    collection = db.users
    _id = ObjectId(id_str)
    person = collection.find_one({'_id':_id})
    return render_template('account.html', username = person['fio'], isAdmin = person['isadmin'])



app.run(debug=True, host="0.0.0.0")
