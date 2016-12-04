from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


# 个人资料表格
class EditProfileForm(Form):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('修改')


# 管理员个人资料表格
class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^(?!_)(?!.*?_$)[a-zA-Z0-9_'
                                                                                    '\u4e00-\u9fa5]+$', 0,
                                                                                    message='非法用户名')])
    confirmed = BooleanField('邮箱认证')
    role = SelectField('权限', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('修改')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    # 邮箱验证，validate方法自动调用
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册')

    # 用户名验证，validate方法自动调用
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在')


# 发表文章
class PostForm(Form):
    body = PageDownField('内容', validators=[DataRequired()])
    submit = SubmitField('发表')


# 发表评论
class CommentForm(Form):
    body = StringField(' ', validators=[DataRequired()])
    submit = SubmitField('发表')


