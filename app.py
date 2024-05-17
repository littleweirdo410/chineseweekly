from flask import Flask, send_from_directory, Response
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from flask import render_template
from flask import request
from flask_admin import Admin, AdminIndexView, expose
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect

# create an app and define basic authentication
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'set anything you wish'
app.config['BASIC_AUTH_PASSWORD'] = 'set anything you wish'

basic_auth = BasicAuth(app)


# some classes to make BasicAuth work with flask-admin
class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "Не получилось авторизоваться. Обновите страницу и попробуйте ещё раз", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}))


class MyModelView(ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Вы не авторизованы')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('auth.html', db=db, Post=Post, Emails=Emails)

    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Вы не авторизованы')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


# initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = b'\x01\xabF\xc3\xa7s\xb2(g\x901\x0ch\xa3\x85\xbe'
db = SQLAlchemy(app)


# describe the posts model
class Post(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer(), primary_key=True)
    date = Column(String(100), nullable=False)
    title = Column(String(100), nullable=False)
    posttext = Column(String(65535), nullable=False)


posts = Post()


# describe the db with emails
class Emails(db.Model):
    __tablename__ = 'emails'
    id = Column(Integer(), primary_key=True)
    email_address = Column(String(65535), nullable=False)


email_addresses = Emails()

# initialize flask-admin
app.config['FLASK_ADMIN_SWATCH'] = 'slate'
admin = Admin(app, name='Китайская неделя', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(MyModelView(Post, db.session))
admin.add_view(MyModelView(Emails, db.session))


# place to serve static JS
@app.route('/static/vendor/<path:path>')
def send_js(path):
    return send_from_directory('static/vendor', path)


# main page with email subscription
@app.route('/')
def hi_page():
    if request.args.get('email') is None or request.args.get('email') in ['', ' ']:
        return render_template('email-form.html')
    else:
        mail = Emails(email_address=request.args.get('email'))
        db.session.add(mail)
        db.session.commit()
        return render_template('success.html')


# proceed to all posts
@app.route('/publications/')
def blog():
    return render_template('blog.html', db=db, Post=Post)


# show some particular post
@app.route('/publications/<int:post_id>/')
def show_post(post_id):
    if request.args.get('email') is None or request.args.get('email') in ['', ' ']:
        return render_template('article.html', db=db, Post=Post, post_id=post_id)
    else:
        mail = Emails(email_address=request.args.get('email'))
        db.session.add(mail)
        db.session.commit()
        return render_template('success.html')


# place to show off my bot
@app.route('/bot/')
def bot():
    return render_template('bot.html')


# about me
@app.route('/about_me/')
def contacts():
    return render_template('about.html')
    
# cookie policy
@app.route('/cookie-policy/')
def cookies():
    return render_template('cookie-policy.html')