from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegistrationForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^(?!_)(?!.*?_$)[a-zA-Z0-9_'
                                                                                    '\u4e00-\u9fa5]+$', 0,
                                                                                    message='非法用户名')])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('cfm_password', message='密码必须一致')])
    cfm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在')


class ChangePasswordForm(Form):
    old_password = StringField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('cfm_new_password', message='密码必须一致')])
    cfm_new_password = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('保存')


class ChangeEmailForm(Form):
    password = PasswordField('密码', validators=[DataRequired()])
    new_email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('保存')

    def validate_new_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')


class ResetPasswordForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),Email()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('cfm_new_password', message='密码必须一致')])
    cfm_password = PasswordField('确认新密码', validators=[DataRequired])
    submit = SubmitField('确认')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class PasswordResetRequestForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('重置密码')


class ChangeUsernameForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^(?!_)(?!.*?_$)[a-zA-Z0-9_'
                                                                                    '\u4e00-\u9fa5]+$', 0,
                                                                                    message='非法用户名')])
    submit = SubmitField('保存')

