from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class RegisterForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])

    username = StringField('用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名必须只有字母, '
 '数字, 点或下划线')])

    password = PasswordField('密码', validators=[Required(), EqualTo('password2', message='密码必须匹配.')])

    password2 = PasswordField('再次输入密码', validators=[Required()])

    submit = SubmitField('注 册')


    def validate_email(self, field):
    	if User.query.filter_by(email=field.data).first():
    		raise ValidationError('邮箱已经被注册了.')

    def validate_username(self, field):
    	if User.query.filter_by(username=field.data).first():
    		raise ValidationError('用户名已经被使用了.')


class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('保持登录状态')
    submit = SubmitField('登 录')

