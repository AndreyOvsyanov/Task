from flask import Flask, render_template, request, redirect, flash, g
from forms import LoginForm, RegistryForm
from flask_login import LoginManager, logout_user, current_user, login_user
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

role = ["Пользователь", "Админинстратор"]

bid_user = db.Table('bid_user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('bid_id', db.Integer, db.ForeignKey('bid.id'))
)
'''
Таблицы из базы данных: заявка - bid, пользователь - user - остальные смежные
'''
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(120), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    login = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=role[0])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<user {self.id}>"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=False)

    def __repr__(self):
        return f"<categories {self.id}{self.name}>"

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    category = db.Column(db.String(120), index=True, unique=True)
    photo = db.Column(db.String(120), index=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    category_id = db.relationship('Category', backref='bid', lazy=True)
    user = db.relationship('User', secondary=bid_user, backref=db.backref('bid', lazy='dynamic'))

    def __repr__(self):
        return f"<bid {self.id}>"

'''
Логика работы с пользователем
'''

login = LoginManager(app)
record = Bid.query.order_by(Bid.created_on.desc()).limit(8).all()
cur_user: User = None

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

'''
Пользователь вышел, текущий меняется на None, осущ. переход на главную страницу, с неппереданным пользователем
'''
@app.route('/logout')
def logout():
    global cur_user
    cur_user = None
    logout_user()
    return redirect('/index')

'''
Главная страница
'''
@app.route('/')
@app.route('/index')
def index():
    title = "Главная страницы"
    global cur_user
    if cur_user is None:
        return render_template('index.html', title=title, record=record)
    else:
        return render_template('index.html', title=title, record=record, user=cur_user)

'''
Пользователь
'''
@app.route('/signin<string:user>')
def signin(user):
    print(user)
    return render_template('signin.html', user=user, record=record)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            message = 'Invalid username or password'
            flash(message)
            return render_template('login.html', message=message, title='Sign In', form=form)
        
        global cur_user
        cur_user = user

        #login_user(user, remember=form.remember_me.data)
        return redirect('/signin{}'.format(user.username))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/registry', methods=['POST', 'GET'])
def registry():
    form = RegistryForm()
    message = ""
    user: User
    if request.method == 'POST':
        print("test")
        user = User()
        username = [form.firstname.data, form.surname.data, form.lastname.data]
        user.username = " ".join(username)
        user.email = form.email.data
        user.login = form.login.data

        p = form.password.data
        pr = form.password_repeat.data
        print(form.remember_me.data)
        if p == pr and form.remember_me.data:
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            print(user.username, user.email, user.login, user.password_hash)

            flash('Login requested for user {}, '
                  'remember_me = {}'
                  .format(username, form.remember_me.data))
            
            global cur_user
            cur_user = user
  
            return redirect('/signin{}'.format(user.username))

        else:
            message = "Неверно введённые данные"



    return render_template('registry.html', title='Registration', message=message, form=form)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)