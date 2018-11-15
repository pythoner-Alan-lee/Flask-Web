from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):
	"""docstring for NameForm"""
	name = StringField('你的名字是?', validators=[Required()])
	submit = SubmitField('提交')


class EditProfileForm(FlaskForm):
	name = StringField('昵 称', validators=[Length(0,64)])
	location = StringField('地 址', validators=[Length(0,64)])
	about_me = TextAreaField('简 介')
	submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	username = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, ''numbers, dots or underscores')])
	confirmed = BooleanField('Comfirmed')
	role = SelectField('Role', coerce=int)
	name = StringField('Real name', validators=[Length(0,64)])
	location = StringField('Location', validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')


	def __init__(self, user, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Roel.name).all()]

		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and \
				User.query.filter_by(email=field.data).first():
			raise ValidationError('邮箱已经被注册了.')


	def validate_username(self, field):
		if field.data != self.user.username and \
				User.query.filter_by(username=field.data).first():
			raise ValidationError('用户名已经被使用了.')


class PostForm(FlaskForm):
	body = PageDownField("请输入您的文章", validators=[Required()])
	submit = SubmitField('提交')


class CommentForm(FlaskForm):
	body = StringField('', validators=[Required()])
	submit = SubmitField('提交')
		