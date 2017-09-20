from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                    TextAreaField, SelectField,IntegerField,DateField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User,Role
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField,FileAllowed


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('保持登入状态')
    submit = SubmitField('登入')

class LoginFormE(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me log in')
    submit = SubmitField('Log in')

class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.]*$', 0,
                                          '名字只能是中文、英文、数字、下划线或点组成！')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='两次输入的密码不一致')])
    password2 = PasswordField('再次输入密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被人注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被人注册')

class RegistrationFormE(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.]*$', 0,
                                          'Name can be in compositon of Chinese, English, numbers, underline.')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='The two inputs are differenct!')])
    password2 = PasswordField('Password again', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The Email has been occupied!')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username has been occupied!')



class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('再次输入密码', validators=[Required()])
    submit = SubmitField('更新密码')

class ChangePasswordFormE(FlaskForm):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='The two inputs are different!')])
    password2 = PasswordField('Password again', validators=[Required()])
    submit = SubmitField('Update password')



class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重设密码')

class PasswordResetRequestFormE(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset password')


class PasswordResetForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='两次输入的密码必须一致')])
    password2 = PasswordField('再次输入密码', validators=[Required()])
    submit = SubmitField('重设密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未知邮箱')


class PasswordResetFormE(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='The two inputs are different!')])
    password2 = PasswordField('Password again', validators=[Required()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown Email')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('更新邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

class ChangeEmailFormE(FlaskForm):
    email = StringField('New Email', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('password', validators=[Required()])
    submit = SubmitField('Reset Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The Email has been occupied!')

class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Required(),Length(0, 64)])
    student_no = StringField('学号或工号', validators=[Required(),Length(0, 64)])
    tel = StringField('手机', validators=[Required(),Length(0, 64)])
    location = StringField('地址', validators=[Required(),Length(0, 64)])
    about_me = PageDownField('关于我', validators=[Required(),Length(0, 64)])
    submit = SubmitField('提交')



class EditProfileFormE(FlaskForm):
    name = StringField('Real name', validators=[Required(),Length(0, 64)])
    student_no = StringField('Student number or work number', validators=[Required(),Length(0, 64)])
    tel = StringField('Telephone', validators=[Required(),Length(0, 64)])
    location = StringField('Address', validators=[Required(),Length(0, 64)])
    about_me = PageDownField('About me', validators=[Required(),Length(0, 64)])
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('电邮', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.]*$', 0,
                                          '名字只能是中文、英文、数字、下划线或点组成！')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('工作', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('地区', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经存在了。')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在了。')


class EditProfileAdminFormE(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[\u4e00-\u9fa5A-Za-z0-9_.]*$', 0,
                                          'Name can be in compositon of Chinese, English, numbers, underline.')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('The Email has been occupied!')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('The username has been occupied!')



class AddTeacherForm(FlaskForm):
    school = StringField('学校', validators=[Required(), Length(1, 64)])
    field = StringField('研究领域',validators=[Required(), Length(1, 64)])
    about_teacher = PageDownField('申请老师描述', validators=[Required()])
    submit = SubmitField('提交')

class AddTeacherFormE(FlaskForm):
    school = StringField('School', validators=[Required(), Length(1, 64)])
    field = StringField('Research areas',validators=[Required(), Length(1, 64)])
    about_teacher = PageDownField('About teacher', validators=[Required()])
    submit = SubmitField('Submit')
    
    
class NameForm(FlaskForm):
    name = StringField('你的名字是什么？', validators=[Required()])
    submit = SubmitField('提交')

class NameFormE(FlaskForm):
    name = StringField('Your name?', validators=[Required()])
    submit = SubmitField('Submit')



class PostForm(FlaskForm):
    topic = StringField("标题",validators=[Required(),Length(0, 64)])
    pic = FileField(label='图片',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    body = PageDownField("内容")
    private = BooleanField("私有")
    submit = SubmitField('提交想法')

class PostFormE(FlaskForm):
    topic = StringField("Topic",validators=[Required(),Length(0, 64)])
    pic = FileField(label='Pic',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    body = PageDownField("Content")
    private = BooleanField("Private")
    submit = SubmitField('Submit')


class PostForm2(FlaskForm):
    topic = StringField("标题",validators=[Required(),Length(0, 64)])
    body = PageDownField("内容")
    file3 = FileField(label='音频',validators=[
        FileAllowed(['wav','mp4','mp3','ogg','Wav','Mp3','Mp4','Ogg','WAV','MP3','MP4','OGG'],message='可以上传小于50M的mp3/mp4/ogg/wav等音频。')])            
    file4 = FileField(label='视频',validators=[
        FileAllowed(['Mp4','Ogg','Mpeg4','WebM','mp4','ogg','mpeg4','webm','MP4','OGG','MPEG4','WEBM'],message='可以上传小于50M的ogg/MPEG4/WebM等视频。')])
    file1 = FileField(label='文件',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    pic = FileField(label='图片1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    pic1 = FileField(label='图片2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    pic2 = FileField(label='图片3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    pic3 = FileField(label='图片4',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    file2 = FileField(label='文件2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file5 = FileField(label='文件3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    private = BooleanField("私有")
    submit = SubmitField('提交想法')

class PostFormE2(FlaskForm):
    topic = StringField("Topic",validators=[Required(),Length(0, 64)])
    body = PageDownField("Content")
    file3 = FileField(label='Audio',validators=[
        FileAllowed(['wav','mp3','ogg','Wav','Mp3','Ogg','WAV','MP3','OGG'],message='You can upload audio files less than 50M such as mp3/ogg/wav.')])            
    file4 = FileField(label='Video',validators=[
        FileAllowed(['Mp4','Ogg','Mpeg4','WebM','mp4','ogg','mpeg4','webm','MP4','OGG','MPEG4','WEBM','mov','MOV','Mov','avi','AVI','Avi','mpg','MPG','Mpg'],message='You can upload video files less than 50M such as mp4/mov/ogg/mpe4/webm.')])
    file1 = FileField(label='File 1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='You can upload txt\pdf\word\excel\ppt\zip\rar or pictures')])
    pic = FileField(label='Pic 1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='You can upload bmp/jpg/jpeg/png/bmp/jif')])
    pic1 = FileField(label='Pic 2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='You can upload bmp/jpg/jpeg/png/bmp/jif')])
    pic2 = FileField(label='Pic 3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='You can upload bmp/jpg/jpeg/png/bmp/jif')])
    pic3 = FileField(label='Pic 4',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='You can upload bmp/jpg/jpeg/png/bmp/jif')])
    file2 = FileField(label='File 2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='You can upload txt\pdf\word\excel\ppt\zip\rar or pictures')])
    file5 = FileField(label='File 3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='You can upload txt\pdf\word\excel\ppt\zip\rar or pictures')])
    private = BooleanField("Private")
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = PageDownField('输入评论', validators=[Required()])
    submit = SubmitField('提交')

class CommentFormE(FlaskForm):
    body = PageDownField('Comment', validators=[Required()])
    submit = SubmitField('Submit')


class AddLessonForm(FlaskForm):
    lesson_name = StringField("课程名",validators=[Required(),Length(0, 64)])
    pic = FileField(label='课程封面',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    about_lesson = PageDownField("课程简介", validators=[Required()])

    file1 = FileField(label='参考资料1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])            
    file2 = FileField(label='参考资料2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file3 = FileField(label='参考资料3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file4 = FileField(label='参考资料4',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file5 = FileField(label='参考资料5',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file6 = FileField(label='参考资料6',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file7 = FileField(label='参考资料7',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file8 = FileField(label='参考资料8',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    submit = SubmitField('提交课程')

class AddLessonFormE(FlaskForm):
    lesson_name = StringField("Name of the lesson",validators=[Required(),Length(0, 64)])
    pic = FileField(label='Picture',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png'],message='可以上传bmp/jpg/jpeg/png/bmp/jif')])
    about_lesson = PageDownField("Syllabus", validators=[Required()])

    file1 = FileField(label='Related file 1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])            
    file2 = FileField(label='Related file 2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file3 = FileField(label='Related file 3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file4 = FileField(label='Related file 4',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file5 = FileField(label='Related file 5',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file6 = FileField(label='Related file 6',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file7 = FileField(label='Related file 7',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    file8 = FileField(label='Related file 8',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR'],message='可以上传txt\pdf\word\excel\ppt\zip\rar或图片')])
    submit = SubmitField('Submit')


class NewLessonForm(FlaskForm):
    year = SelectField('学年',choices=[('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022')],validators=[Required()])
    season = SelectField('学期',choices=[('春','春'), ('夏','夏'), ('秋','秋'), ('冬','冬')],validators=[Required()])
    room_row = IntegerField('教室座位行数')
    room_column = IntegerField('教室座位列数')
    about = StringField("简短说明",validators=[Required(),Length(0, 64)])
#    start_date = DateField('开始日')
#    end_date = DateField('结束日')
#    weekday1 = SelectField('第一次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
#    start_hour1 = IntegerField("小时",validators=[Length(0, 2)])
#    start_minute1 = IntegerField("分钟",validators=[Length(0, 2)])
#    end_hour1 = IntegerField("小时",validators=[Length(0, 2)])
#    end_minute1 = IntegerField("分钟",validators=[Length(0, 2)])
#    weekday2 = SelectField('第二次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
#    start_hour2 = IntegerField("小时",validators=[Length(0, 2)])
#    start_minute2 = IntegerField("分钟",validators=[Length(0, 2)])
#    end_hour2 = IntegerField("小时",validators=[Length(0, 2)])
#    end_minute2 = IntegerField("分钟",validators=[Length(0, 2)])
    submit = SubmitField('提交')

class NewLessonFormE(FlaskForm):
    year = SelectField('Year',choices=[('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022')],validators=[Required()])
    season = SelectField('Season',choices=[('Spring','Spring'), ('Summer','Summer'), ('Autumn','Autumn'), ('Winter','Winter')],validators=[Required()])
    room_row = IntegerField('Rows of the classroom')
    room_column = IntegerField('Columns of the classroom')
    about = StringField("About the class",validators=[Required(),Length(0, 64)])
#    start_date = DateField('Start date')
#    end_date = DateField('End date')
#    weekday1 = SelectField('First lecture',choices=[('Monday','Monday'), ('Monday','Monday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
#    start_hour1 = IntegerField("Houre",validators=[Length(0, 2)])
#    start_minute1 = IntegerField("Munite",validators=[Length(0, 2)])
#    end_hour1 = IntegerField("Houre",validators=[Length(0, 2)])
#    end_minute1 = IntegerField("Munite",validators=[Length(0, 2)])
#    weekday2 = SelectField('Second lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
#    start_hour2 = IntegerField("Hour",validators=[Length(0, 2)])
#    start_minute2 = IntegerField("Munite",validators=[Length(0, 2)])
#    end_hour2 = IntegerField("Hour",validators=[Length(0, 2)])
#    end_minute2 = IntegerField("Munite",validators=[Length(0, 2)])
    submit = SubmitField('Submit')


class NewLessonForm2(FlaskForm):
    year = SelectField('学年',choices=[('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022')],validators=[Required()])
    season = SelectField('学期',choices=[('春','春'), ('夏','夏'), ('秋','秋'), ('冬','冬')],validators=[Required()])
    room_row = IntegerField('教室座位行数')
    room_column = IntegerField('教室座位列数')
    about = StringField("简短说明",validators=[Required(),Length(0, 64)])
    start_date = DateField('开始日')
    end_date = DateField('结束日')
    weekday1 = SelectField('第一次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour1 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute1 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour1 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute1 = IntegerField("分钟",validators=[Length(0, 2)])
    weekday2 = SelectField('第二次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour2 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute2 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour2 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute2 = IntegerField("分钟",validators=[Length(0, 2)])
    weekday3 = SelectField('第三次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour3 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute3 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour3 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute3 = IntegerField("分钟",validators=[Length(0, 2)])
    weekday4 = SelectField('第四次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour4 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute4 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour4 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute4 = IntegerField("分钟",validators=[Length(0, 2)])
    weekday5 = SelectField('第五次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour5 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute5 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour5 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute5 = IntegerField("分钟",validators=[Length(0, 2)])
    weekday6 = SelectField('第六次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour6 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute6 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour6 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute6 = IntegerField("分钟",validators=[Length(0, 2)])
    weekday7 = SelectField('第七次课',choices=[('Monday','周一'), ('Tuesday','周二'), ('Wednesday','周三'), ('Thursday','周四'),('Friday','周五'),('Saturday','周六'),('Sunday','周日')])
    start_hour7 = IntegerField("小时",validators=[Length(0, 2)])
    start_minute7 = IntegerField("分钟",validators=[Length(0, 2)])
    end_hour7 = IntegerField("小时",validators=[Length(0, 2)])
    end_minute7 = IntegerField("分钟",validators=[Length(0, 2)])
    submit = SubmitField('提交')

class NewLessonFormE2(FlaskForm):
    year = SelectField('Year',choices=[('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022')],validators=[Required()])
    season = SelectField('Season',choices=[('Spring','Spring'), ('Summer','Summer'), ('Autumn','Autumn'), ('Winter','Winter')],validators=[Required()])
    room_row = IntegerField('Rows of the classroom')
    room_column = IntegerField('Columns of the classroom')
    about = StringField("About the class",validators=[Required(),Length(0, 64)])
    start_date = DateField('Start date')
    end_date = DateField('End date')
    weekday1 = SelectField('First lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour1 = IntegerField(" Hour",validators=[Length(0, 2)])
    start_minute1 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour1 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute1 = IntegerField(" Munite",validators=[Length(0, 2)])
    weekday2 = SelectField('Second lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour2 = IntegerField(" Hour",validators=[Length(0, 2)])
    start_minute2 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour2 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute2 = IntegerField(" Munite",validators=[Length(0, 2)])
    weekday3 = SelectField('Third lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour3 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute3 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour3 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute3 = IntegerField(" Munite",validators=[Length(0, 2)])
    weekday4 = SelectField('Forth lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour4 = IntegerField(" Hour",validators=[Length(0, 2)])
    start_minute4 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour4 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute4 = IntegerField(" Munite",validators=[Length(0, 2)])
    weekday5 = SelectField('Fifth lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour5 = IntegerField(" Hour",validators=[Length(0, 2)])
    start_minute5 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour5 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute5 = IntegerField(" Munite",validators=[Length(0, 2)])
    weekday6 = SelectField('Sixth lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour6 = IntegerField(" Hour",validators=[Length(0, 2)])
    start_minute6 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour6 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute6 = IntegerField(" Munite",validators=[Length(0, 2)])
    weekday7 = SelectField('Seventh lecture',choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')])
    start_hour7 = IntegerField(" Hour",validators=[Length(0, 2)])
    start_minute7 = IntegerField(" Munite",validators=[Length(0, 2)])
    end_hour7 = IntegerField(" Hour",validators=[Length(0, 2)])
    end_minute7 = IntegerField(" Munite",validators=[Length(0, 2)])
    submit = SubmitField('Submit')



class UpdateTopicForm(FlaskForm):
    topic = StringField("选题",validators=[Required(),Length(0, 64)])
    body = PageDownField("说明",validators=[Required()])

    file1 = FileField(label='汇报幻灯片',validators=[
        FileAllowed(['ppt','PPT','pptx','PPTX','pdf','PDF','key','KEY'],message='可以上传ppt/pptx/pdf/key')])            
    file2 = FileField(label='期末论文',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    file3 = FileField(label='相关资料1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    file4 = FileField(label='相关资料2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    file5 = FileField(label='相关资料3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    submit = SubmitField('提交')
    
    
class UpdateTopicFormE(FlaskForm):
    topic = StringField("Topic",validators=[Required(),Length(0, 64)])
    body = PageDownField("Remark",validators=[Required()])

    file1 = FileField(label='PPT',validators=[
        FileAllowed(['ppt','PPT','pptx','PPTX','pdf','PDF','key','KEY'],message='可以上传ppt/pptx/pdf/key')])            
    file2 = FileField(label='Paper',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    file3 = FileField(label='Related file 1',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    file4 = FileField(label='Related file 2',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    file5 = FileField(label='Related file 3',validators=[
        FileAllowed(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','key','KEY'],message='可以上传txt\pdf\word\excel\ppt\zip\rar\key或图片')])
    submit = SubmitField('Submit')    
        
    



class LessonFileForm(FlaskForm):
    filetype = SelectField('文件类型',choices=[('document','文档'),('audio','音频'),('video','视频'),('picture','图片')],validators=[Required()])
    visibility = SelectField('可见范围',choices=[('public','全网公开'),('student','选修学生可见'),('private','个人')],validators=[Required()])
    file = FileField(label='上传文件')               
    about = StringField("简短描述",validators=[Length(0, 128)])   
    submit = SubmitField('提交')

class LessonFileFormE(FlaskForm):
    filetype = SelectField('Type of the file',choices=[('document','Ducument'),('audio','Audio'),('video','Video'),('picture','Picture')],validators=[Required()])
    visibility = SelectField('Who can see',choices=[('public','Public'),('student','All student'),('private','Private')],validators=[Required()])
    file = FileField(label='Update a file')            
    about = StringField("Brief description",validators=[Length(0, 128)])
    submit = SubmitField('Submit')


class LetterForm(FlaskForm):
    receiver = StringField("收信人",validators=[Required(),Length(0, 64)])
    topic = StringField("标题",validators=[Required(),Length(0, 64)])
    body = PageDownField("内容")
    submit = SubmitField('发送')


class CriticismForm(FlaskForm):
    score = IntegerField("得分",validators=[Required()])
    criticism = TextAreaField("评语",validators=[Required(),Length(0, 256)])
    submit = SubmitField('提交')


class CriticismFormE(FlaskForm):
    score = IntegerField("Score",validators=[Required()])
    criticism = TextAreaField("Criticism",validators=[Required(),Length(0, 256)])
    submit = SubmitField('Submit')

