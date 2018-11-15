# 导入了 Flask 类。这个类的实例将会是我们的 WSGI 应用程序。
from flask import Flask,render_template,session,redirect,url_for,flash, current_app
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.163.com'            	        # 邮件服务器
app.config['MAIL_PORT'] = 25			                   		# 发送邮件的端口
app.config['MAIL_USE_TLS'] = True								# 安全传输协议开关
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')	# 邮件用户名
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')	# 邮件用户密码
app.config['SQLALCHEMY_DATABASE_URI'] =\
 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY']=os.urandom(20)							# 用户会话的密钥
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')		# 程序管理员邮箱地址
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'			# 邮件主题前缀
app.config['FLASKY_MAIL_SENDER'] = '15112788190@163.com'		# 发件人，可与邮件用户名相同
# app.config['SECRECT_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)


class NameForm(FlaskForm):
	"""docstring for NameForm"""
	name = StringField('What is your name?', validators=[Required()])
	submit = SubmitField('Submit')


class Role(db.Model):
	"""docstring for Role"""
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role', lazy='dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	"""docstring for User"""
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username
				

@app.route('/',methods=['GET','POST'])
def index():
	#name = None
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username = form.name.data)
			db.session.add(user)
			session['known'] = False
			if app.config['FLASKY_ADMIN']:
				send_email(app.config['FLASKY_ADMIN'], 'New User',
 'mail/new_user', user=user)
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('index'))
	return render_template('index.html',form=form,name=session.get('name'),known=session.get('known',False))
		# old_name = session.get('name')
		# if old_name is not None and old_name != form.name.data:
		# 	flash('看起来你应该改变了你的名字!')
		# session['name'] = form.name.data
		# return redirect(url_for('index'))
		#name = form.name.data
		#form.name.data = ''
	#return '<h1>Hello World!!</h1>'
	#return render_template('index.html',current_time=datetime.utcnow())
	#return render_template('index.html',form=form,name=session.get('name'))

@app.route('/user/<name>')
def user(name):
	return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'),500




def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))


def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr





if __name__ == '__main__':
	manager.run()
