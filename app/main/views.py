from flask import render_template, redirect, request, url_for, flash,\
                    abort, current_app, make_response
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models import User,allowed_file,Teacher,Role,Lesson, Permission, Post, \
                    Comment,NewLesson,Student,CollectPost,Follow,LessonFile,\
                    AtMe
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm,AddTeacherForm,\
    EditProfileForm, EditProfileAdminForm, UpdateTopicForm,\
    PostForm, CommentForm, PostForm2,AddLessonForm,NewLessonForm,\
    LoginFormE, RegistrationFormE, ChangePasswordFormE,\
    PasswordResetRequestFormE, PasswordResetFormE, ChangeEmailFormE,AddTeacherFormE,\
    EditProfileFormE, EditProfileAdminFormE, UpdateTopicFormE,\
    PostFormE, CommentFormE, PostFormE2,AddLessonFormE,NewLessonFormE,\
    LessonFileForm,LessonFileFormE,CriticismForm,CriticismFormE
from ..decorators import admin_required
from PIL import Image
from flask_sqlalchemy import get_debug_queries
from . import main
from ..decorators import permission_required
from werkzeug import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import flask,os,random,time,datetime



@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'main.' \
                and request.endpoint != 'static':
            return redirect(url_for('main.unconfirmed'))


@main.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    english=request.cookies.get('english')
    if english == "yes":
        form = LoginFormE()
    else:
        form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        if english == "yes":
            flash('Invalid username or password.')
        else:
            flash('用户名或密码不准确。')
    return render_template('login.html', form=form, english=english)


@main.route('/logout')
@login_required
def logout():
    english=request.cookies.get('english')
    logout_user()
    if english == "yes":
        flash('You have logged out.')
    else:
        flash('您已经登出了。')
    return redirect(url_for('main.index'))

@main.route('/set-cookie-english')
def set_cookie_english():
    english=request.cookies.get('english')
    outdate=datetime.datetime.today() + datetime.timedelta(days=30)  
    resp = current_app.make_response(redirect(url_for('main.index')))
    if english == "yes":
        resp.set_cookie('english','no',expires=outdate)
    else:
        resp.set_cookie('english','yes',expires=outdate)
    return  resp

@main.route('/', methods=['GET', 'POST'])
def index():
    english=request.cookies.get('english',None)
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = PostFormE(values)
    else:
        form = PostForm(values)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.private == False).\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts = pagination.items
#    if current_user.is_anonymous:
#        return redirect(url_for('main.about'))
#    else:
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination,english=english)


@main.route('/homepage', methods=['GET', 'POST'])
def homepage():
    english=request.cookies.get('english',None)
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = PostFormE(values)
    else:
        form = PostForm(values)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.private == False).\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts = pagination.items
    return render_template('homepage.html', form=form, posts=posts,
                           pagination=pagination,english=english)

@main.route('/register', methods=['GET', 'POST'])
def register():
    english=request.cookies.get('english')
    if english == "yes":
        form = RegistrationFormE()
    else:
        form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(username=form.username.data).first()
        f = Follow.query.filter_by(followed_id=u.id).filter_by(follower_id=u.id).first()
        if f != None:
            db.session.delete(f)
            db.session.commit()
        token = user.generate_confirmation_token()
        if english == "yes":
            send_email(user.email, 'Please confirm your account.',
                   'email/confirm', user=user, token=token)
            flash('Registered. Please log in.')
        else:
            send_email(user.email, '请确认您的登陆帐户',
                   'email/confirm', user=user, token=token)
            flash('已经注册，请登录。')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form,english=english)


@main.route('/confirm/<token>')
@login_required
def confirm(token):
    english=request.cookies.get('english')
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if english == "yes":
        if current_user.confirm(token):
            flash('You have confirmed your account. Please update your profile before you can select any class.')
        else:
            flash('The link for confirmation has become invalid.')
    else:
        if current_user.confirm(token):
            flash('您已经确认了您的账户。谢谢！另外，完善资料后可以选课或登记为老师。')
        else:
            flash('确认链接已经失效或过期。')    
    return redirect(url_for('main.index'))


@main.route('/confirm')
@login_required
def resend_confirmation():
    english=request.cookies.get('english')
    token = current_user.generate_confirmation_token()
    if english == "yes":
        send_email(current_user.email, 'Please confirm your account.',
                   'email/confirm', user=current_user, token=token)
        flash('A new confirmaiton Email has sent to your mailbox.')
    else:
        send_email(current_user.email, '请确认您的登陆账户',
           'email/confirm', user=current_user, token=token)
        flash('一个新的确认邮件已经发送到您的邮箱。')

    return redirect(url_for('main.index'))

@main.route('/baidu_verify_6dD5VXSUuK.html')
def baidu_verify_6dD5VXSUuK():
    return render_template("baidu_verify_6dD5VXSUuK.html")

@main.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    english=request.cookies.get('english')
    if english == "yes":
        form = ChangePasswordFormE()
    else:
        form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            if english == "yes":
                flash('Your password has been updated.')
            else:
                flash('您的密码已经更新了。')
            return redirect(url_for('main.index'))
        else:
            if english == "yes":
                flash('Invalid password.')
            else:
                flash('密码无效。')
    return render_template("change_password.html", form=form,english=english)


@main.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    english=request.cookies.get('english')
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if english == "yes":
        form = PasswordResetRequestFormE()
    else:
        form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            if english == "yes":
                send_email(user.email, 'Please confirm your password resetting.',
                       'email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
                flash('The password resetting Email has been sent to your mailbox.')
            else:
                send_email(user.email, '请确认密码的重设',
                       'email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
                flash('重设密码的确认邮件已经发送到您的邮箱。')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form,english=english)


@main.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    english=request.cookies.get('english')
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if english == "yes":
        form = PasswordResetFormE()
    else:
        form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            if english == "yes":
                flash('The password has been updated.')
            else:
                flash('密码已经更新。')
            return redirect(url_for('main.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('reset_password.html', form=form,english=english)


@main.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    english=request.cookies.get('english')
    if english == "yes":
        form = ChangeEmailFormE()
    else:
        form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            if english == "yes":
                send_email(new_email, 'Please confirm your new Email.',
                           'email/change_email',
                           user=current_user, token=token)
                flash('A confirmation Email has been sent to you mailbox.')
            else:
                send_email(new_email, '请确认您的邮箱更换',
                           'email/change_email',
                           user=current_user, token=token)
                flash('确认新邮箱的电子邮件已经发送到您的新邮箱。')
                
            return redirect(url_for('main.index'))
        else:
            if english == "yes":
                flash('Invalid password or username.')
            else:
                flash('用户名或密码无效。')
    return render_template("change_email.html", form=form,english=english)


@main.route('/change-email/<token>')
@login_required
def change_email(token):
    english=request.cookies.get('english')
    if current_user.change_email(token):
        if english == "yes":
            flash('Your new Email has been updated.')
        else:
            flash('您的邮箱已经更新了。')
    else:
        if english == "yes":
            flash('Invalid request.')
        else:
            flash('请求无效。')
    return redirect(url_for('main.index'))


@main.route('/edit-avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    english=request.cookies.get('english')
    if request.method == 'POST':
        file = request.files['file']
        size = (1024, 1024)
        im = Image.open(file)
        im.thumbnail(size)
        
        if file and allowed_file(file.filename):
            filename1 = current_user.email.replace('@','__').replace('.','__') + '.' + file.filename.split('.')[-1]
            im.save(os.path.join('app/static', 'avatar', filename1))
            current_user.avatar_file = url_for('static', 
                                               filename='%s/%s' % ('avatar', filename1))
            db.session.commit()
            current_user.is_avatar_default = False
            if english == "yes":
                flash('The portrait has been updated.')
            else:
                flash('头像修改成功')
            return redirect(url_for('main.user', username=current_user.username))
    return render_template('change_avatar.html',english=english)


@main.route('/edit-pic', methods=['GET', 'POST'])
@login_required
def change_pic():
    english=request.cookies.get('english')
    if request.method == 'POST':
        file = request.files['file']
        size = (1024, 1024)
        im = Image.open(file)
        im.thumbnail(size)
        teacher = Teacher.query.filter_by(teacher_id=current_user.id).first()
        
        if file and allowed_file(file.filename):
            filename1 = current_user.email.replace('@','__').replace('.','__') + '.' + file.filename.split('.')[-1]
            im.save(os.path.join('app/static', 'teacher_pic', filename1))
            teacher.pic = url_for('static',filename='%s/%s' % ('teacher_pic', filename1))
            db.session.commit()
            current_user.is_avatar_default = False
            if english == "yes":
                flash('The portrait has been updated.')
            else:
                flash('头像修改成功')
            return redirect(url_for('main.teacher', id=current_user.id))
    return render_template('change_pic.html',english=english)

@main.route('/edit-lesson-pic/<int:id>', methods=['GET', 'POST'])
@login_required
def change_lesson_pic(id):
    english=request.cookies.get('english')
    if request.method == 'POST':
        file = request.files['file']
        size = (1024, 1024)
        im = Image.open(file)
        im.thumbnail(size)
        lesson = Lesson.query.filter_by(id=id).first()    
        if file and allowed_file(file.filename):
            filename = file.filename
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
            im.save(os.path.join('app/static', 'lesson', filename1))
            try:
                os.remove("/root/517shangke/app"+lesson.pic)
            except:
                pass

            lesson.pic = url_for('static',filename='%s/%s' % ('lesson', filename1))
            db.session.commit()
            current_user.is_avatar_default = False
            if english == "yes":
                flash('The portrait has been updated.')
            else:
                flash('课程封面修改成功')
            return redirect(url_for('main.lesson', id=id))
    return render_template('change_lesson_pic.html',english=english)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    english=request.cookies.get('english')
    if english == "yes":
        form = EditProfileFormE()
    else:
        form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.student_no = form.student_no.data
        current_user.tel = form.tel.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        if english == "yes":
            flash('Your profile has been updated.')
        else:
            flash('您的资料已经更新了。现在您可以选课或登记为老师。')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.student_no.data = current_user.student_no
    form.tel.data = current_user.tel
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form,english=english)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    english=request.cookies.get('english')
    user = User.query.get_or_404(id)
    if english == "yes":
        form = EditProfileAdminFormE(user=user)
    else:
        form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        if english == "yes":
            flash('The profile has been updated.')
        else:
            flash('您的资料已经更新了。')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user,english=english)


@main.route('/add-teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    english=request.cookies.get('english')
    if english == "yes":
        form = AddTeacherFormE()
    else:
        form = AddTeacherForm()
    teacher = Teacher()
    if form.validate_on_submit():
        teacher.teacher_id = current_user.id
        teacher.school = form.school.data
        teacher.field = form.field.data
        teacher.about_teacher = form.about_teacher.data
        current_user.teacher = True
        if english == "yes":
            flash("Your teacher's profile has been created.")
        else:
            flash('您的教师资料已经登记，你可以进入老师主页开课了。')
        db.session.add(teacher)        
        db.session.add(teacher)
        return redirect(url_for('main.teacher',id=current_user.id))
    return render_template("add_teacher.html",form=form,english=english)


@main.route('/edit-teacher/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    english=request.cookies.get('english')
    teacher = Teacher.query.filter_by(teacher_id=id).first()
    if english == "yes":
        form = AddTeacherFormE()
    else:
        form = AddTeacherForm()
    if form.validate_on_submit():
        teacher.school = form.school.data
        teacher.field = form.field.data
        teacher.about_teacher = form.about_teacher.data
        db.session.commit()
        if english == "yes":
            flash('The profile has been updated.')
        else:
            flash('您的资料已经更新了。') 
        return redirect(url_for('main.teacher',id=current_user.id))
    form.school.data = teacher.school
    form.field.data = teacher.field
    form.about_teacher.data = teacher.about_teacher
    return render_template("edit_teacher.html",form=form,teacher=teacher,english=english)
           
           
           
@main.after_app_request
def after_request(response):
    english=request.cookies.get('english')
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            if english == "yes":
                current_app.logger.warning(
                'Query is slow %s\n Parmeters: %s\n Time: %fs\ Context: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
            else:
                current_app.logger.warning(
                '查询缓慢：%s\n参数：%s\n时间：%fs\n上下文：%s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    english=request.cookies.get('english')
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    if english == "yes":
        return "Closing..."
    else:
        return '关闭中...'


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))



@main.route('/markdown')
def markdown():
    english=request.cookies.get('english')
    return render_template("markdown.html", english=english)

@main.route('/about')
def about():
    english=request.cookies.get('english')
    return render_template("about.html", english=english)

@main.route('/wujiangang')
def wujiangang():
    english=request.cookies.get('english')
    return render_template("wujiangang.html", english=english)

@main.route('/jiangangwu')
def jiangangwu():
    english=request.cookies.get('english')
    return render_template("jiangangwu.html", english=english)

@main.route('/blog', methods=['GET', 'POST'])
def blog():
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = PostFormE(values)
    else:
        form = PostForm(values)
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        pagination = current_user.followed_posts.filter(Post.private == False).\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    else:
        pagination = Post.query.filter(Post.private == False).\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts = pagination.items
    return render_template('blog.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination, english=english)

@main.route('/suggestion')
@login_required
def suggestion():
    english=request.cookies.get('english')
    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed_posts.filter(Post.tag == 'suggestion').\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts = pagination.items
    return render_template('suggestion.html', posts=posts,
                           pagination=pagination, english=english)
    

@main.route('/show-all')
def show_all():
    resp = make_response(redirect(url_for('.blog')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/show-followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.blog')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    english=request.cookies.get('english')
    page = request.args.get('page', 1, type=int)
    users = User.query.filter(User.id > 0).order_by(User.last_seen.desc()).all()
    user = User.query.filter_by(username=username).first_or_404()
    atme_bodies = []
    mylessons = []
    openedlessons = Lesson.query.filter_by(teacher_id=user.id).order_by(Lesson.timestamp.desc()).all()
    students = []
    students = Student.query.filter_by(student_id=user.id).order_by(Student.timestamp.desc()).all() 
    mylessons = []
    if students != []:    
        for s in students:
            newlesson = NewLesson.query.filter_by(id=s.newlesson_id).first()
            lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()
            mylessons.append([newlesson,lesson])
    show_my_private = "0"
    show_my_private = request.cookies.get('show_my_private', '')
    pagination = user.posts.filter(Post.private == False).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    atmes = AtMe.query.filter_by(username=username).order_by(AtMe.timestamp.desc()).all()

    pagination_private = user.posts.filter(Post.private == True).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts_private = pagination_private.items

    if atmes != None:
        for atme in atmes:
            comment = Comment.query.filter_by(id=atme.comment_id).first()
            atme_bodies.append([atme,comment])
    pagination_atme = AtMe.query.filter_by(username=username).paginate(page, \
                                        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    return render_template('user.html', user=user, users=users, atme_bodies=atme_bodies,\
                           posts=posts,posts_private=posts_private,openedlessons=openedlessons,\
                       pagination=pagination,pagination_private=pagination_private,pagination_atme=pagination_atme,\
                       show_my_private=show_my_private, mylessons=mylessons,english=english)
    
@main.route('/show-my-all/<username>')
def show_my_all(username):
    resp = make_response(redirect(url_for('.user',username=username)))
    resp.set_cookie('show_my_private', '0', max_age=30*24*60*60)
    return resp


@main.route('/show-my-private/<username>')
@login_required
def show_my_private(username):
    resp = make_response(redirect(url_for('.user',username=username)))
    resp.set_cookie('show_my_private', '1', max_age=30*24*60*60)
    return resp

@main.route('/show-my-selected-classes/<username>')
def show_my_selected_classes(username):
    resp = make_response(redirect(url_for('.user',username=username)))
    resp.set_cookie('show_my_private', '2', max_age=30*24*60*60)
    return resp

@main.route('/show-my-atme/<username>')
@login_required
def show_my_atme(username):
    resp = make_response(redirect(url_for('.user',username=username)))
    resp.set_cookie('show_my_private', '3', max_age=30*24*60*60)
    return resp

@main.route('/show-my-all-users-atme/<username>')
@login_required
def show_my_all_users(username):
    resp = make_response(redirect(url_for('.user',username=username)))
    resp.set_cookie('show_my_private', '4', max_age=30*24*60*60)
    return resp


#@main.route('/show-my-commented/<username>')
#@login_required
#def show_my_commented(username):
#    resp = make_response(redirect(url_for('.user',username=current_user.username)))
#    resp.set_cookie('show_my_commented', '', max_age=30*24*60*60)
#    return resp
#


@main.route('/user2/<username>')
def user2(username):
    english=request.cookies.get('english')
    page = request.args.get('page', 1, type=int)
    show_my_private = False
    users = User.query.filter(User.id > 0).order_by(User.member_since.desc()).all()
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_authenticated and current_user.username==username:
        show_my_private = bool(request.cookies.get('show_my_private', ''))

    if not show_my_private:
        pagination = user.posts.filter(Post.private == False).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
    if show_my_private:
        pagination = current_user.posts.filter(Post.private == True).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
    if current_user.is_authenticated and current_user.username==username:
        students = Student.query.filter_by(student_id=current_user.id).all() 
        mylessons = []
        for s in students:
            newlesson = NewLesson.query.filter_by(id=s.newlesson_id).first()
            lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()
            mylessons.append([newlesson,lesson])
        return render_template('user.html', user=user, posts=posts,users=users, 
                           pagination=pagination,show_my_private=show_my_private,
                           mylessons=mylessons, english=english)
    return render_template('user.html', user=user, posts=posts,users=users, 
                           pagination=pagination,show_my_private=show_my_private, english=english)



@main.route('/user-posts/<username>')
def user_posts(username):
    english=request.cookies.get('english')
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    pagination = user.posts.filter(Post.private == False).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
    posts = pagination.items
    return render_template('user_posts.html', user=user, posts=posts,
                           pagination=pagination, english=english)


@main.route('/comments-on-me/<int:user_id>')
@login_required
def comments_on_me(user_id):
    english=request.cookies.get('english')
#    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=user_id).first()
    posts = Post.query.filter_by(author_id=user.id).all()    
    post_comments = []
    post_comments2 = []
    timestamps = []
    for post in posts:
        comments = Comment.query.filter_by(post_id=post.id).all()
        if len(comments) != 0:
            for comment in comments:
                post_comments.append([post,comment])
                timestamps.append(comment.timestamp)
    if len(post_comments) != 0:
        timestamps2 = sorted(timestamps,reverse=True)
        for t in timestamps2:
            post_comments2.append(post_comments[timestamps.index(t)])
#    pagination = Comment
#    Post.query.join(Comment, Comment.post_id == user.id)\
#            .filter(Comment.author_id == user.id).order_by(Post.timestamp.desc()).paginate(
#            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#            error_out=False)
    return render_template('comments_on_me.html', post_comments2=post_comments2, english=english)
#                           pagination=pagination)

@main.route('/sent-comments/<int:user_id>')
@login_required
def sent_comments(user_id):
    english=request.cookies.get('english')
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(author_id=user_id).order_by(db.desc(Comment.timestamp)).all()    
    pagination = Comment.query.filter_by(author_id=user_id).paginate(page, \
                                        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    post_comments = []
    for comment in comments:
        post = Post.query.filter_by(id=comment.post_id).first()
        if post is not None:
            post_comments.append([post,comment])
        else:
            if english == "yes":
                post_comments.append(["The original blog has been deleted.",comment])
            else:
                post_comments.append(["原帖子已经删除",comment])
    return render_template('sent_comments.html', post_comments=post_comments,pagination=pagination, english=english)




@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    english=request.cookies.get('english')
    if current_user.is_authenticated:
        collect = CollectPost.query.filter_by(post_id=id).filter_by(user_id=current_user.id).first()
    else:
       collect = None 
    if collect == None:
        is_collect = 0
    else:
        is_collect = 1
    post = Post.query.get_or_404(id)
    if current_user.is_authenticated:
        if current_user.id != post.author_id and post.private == True:
            if english == "yes":
                flash('The blog has been set as private.')
            else:
                flash('帖子已经设为私有。')
            return redirect(url_for('.sent_comments',user_id=current_user.id))
    if english == "yes":
        form = CommentFormE()
    else:
        form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        if english == "yes":
            flash('The comment has been uploaded.')
        else:
            flash('评论已经上传。')
        body = form.body.data
#        comment = Comment.query.filter_by(body=form.body.data).filter_by(post_id=post.id).first()
        ats = body.split('@')[1:]
        if len(ats) > 0:
            for at in body.split('@'):
                username = at.split(' ')[0]
                user = User.query.filter_by(username=username).first()
                if user is not None:
                    atme = AtMe(comment_id=comment.id,username=username, username_whoatme=current_user.username)
                    db.session.add(atme)
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    if post.tag != None and 'newlessons' in post.tag:
        flag = 1
        newlesson_id = int(post.tag.split('_')[1])
        newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
        lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()
        return render_template('post.html', post=post, form=form, is_collect=is_collect, \
                           comments=comments, pagination=pagination,\
                           lesson_name=lesson.lesson_name, \
                           newlesson_id=newlesson_id,flag=flag, english=english)
    else:
        flag = 0
    
    return render_template('post.html', post=post, form=form, flag=flag,
                      is_collect=is_collect, comments=comments, pagination=pagination, english=english)


@main.route('/write/<string:tag>', methods=['GET', 'POST'])
@login_required
def write(tag):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = PostFormE(values)
    else:
        form = PostForm(values)
    enctype="multipart/form-data"
    if form.private.data == None:
        private = False
    else:
        private = form.private.data
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(topic=form.topic.data,body=form.body.data,
                    private=private, tag=tag,
                    author=current_user._get_current_object())
        if request.method == 'POST':
            pic = request.files['pic']
            size = (1024, 1024) 
            if pic and allowed_file(pic.filename):
                im = Image.open(pic)
                im.thumbnail(size)        
                filename = secure_filename(pic.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'post', filename1))
                post.pic = url_for('static',filename='%s/%s' % ('post', filename1))
                
        db.session.add(post)
        if english == "yes":
            flash('The blog has been uploaded.')
        else:
            flash('帖子已经提交。')
        if 'posts' in tag:
            return redirect(url_for('.user',username=current_user.username))
        if 'suggestion' in tag:
            return redirect(url_for('.suggestion'))
        if 'newlessons' in tag:
            return redirect(url_for('.current_lesson',newlesson_id=int(tag.split('_')[1]),tag=tag))
            
    return render_template('write.html', form=form,enctype=enctype,tag=tag, english=english)

@main.route('/write2/<string:tag>', methods=['GET', 'POST'])
@login_required
def write2(tag):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = PostFormE2(values)
    else:
        form = PostForm2(values)
    enctype="multipart/form-data"
    if form.private.data == None:
        private = False
    else:
        private = form.private.data
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(topic=form.topic.data,body=form.body.data,
                    private=private,tag=tag,
                    author=current_user._get_current_object())
        if request.method == 'POST':
            pic = request.files['pic']
            size = (1024, 1024) 
            if pic and allowed_file(pic.filename):
                im = Image.open(pic)
                im.thumbnail(size)        
                filename = secure_filename(pic.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'post', filename1))
                post.pic = url_for('static',filename='%s/%s' % ('post', filename1))
    
            pic1 = request.files['pic1']
            if pic1 and allowed_file(pic1.filename):
                im = Image.open(pic1)
                im.thumbnail(size)        
                filename = secure_filename(pic1.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'post', filename1))
                post.pic1 = url_for('static',filename='%s/%s' % ('post', filename1))
    
            pic2 = request.files['pic2']
            size = (1024, 1024) 
            if pic2 and allowed_file(pic2.filename):
                im = Image.open(pic2)
                im.thumbnail(size)        
                filename = secure_filename(pic2.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'post', filename1))
                post.pic2 = url_for('static',filename='%s/%s' % ('post', filename1))
    
            pic3 = request.files['pic3']
            size = (1024, 1024) 
            if pic3 and allowed_file(pic3.filename):
                im = Image.open(pic3)
                im.thumbnail(size)        
                filename = secure_filename(pic3.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'post', filename1))
                post.pic3 = url_for('static',filename='%s/%s' % ('post', filename1))
    
            file1 = request.files['file1']
            if file1 and allowed_file(file1.filename):
                filename = secure_filename(file1.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file1.save(os.path.join('app/static', 'file', filename1))
                post.file1 = url_for('static',filename='%s/%s' % ('file', filename1))
                post.filename1 = file1.filename        
    
            file2 = request.files['file2']
            if file2 and allowed_file(file2.filename):
                filename = secure_filename(file2.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file2.save(os.path.join('app/static', 'file', filename1))
                post.file2 = url_for('static',filename='%s/%s' % ('file', filename1))
                post.filename2 = file2.filename        
    
            file3 = request.files['file3']
            if file3 and allowed_file(file3.filename):
                filename = secure_filename(file3.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file3.save(os.path.join('app/static', 'audio', filename1))
                post.file3 = url_for('static',filename='%s/%s' % ('audio', filename1))
                post.filename3 = file3.filename        
    
            file4 = request.files['file4']
            if file4 and allowed_file(file4.filename):
                filename = secure_filename(file4.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file4.save(os.path.join('app/static', 'video', filename1))
                post.file4 = url_for('static',filename='%s/%s' % ('video', filename1))
                post.filename4 = file4.filename
    
            file5 = request.files['file5']
            if file5 and allowed_file(file5.filename):
                filename = secure_filename(file5.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file5.save(os.path.join('app/static', 'video', filename1))
                post.file5 = url_for('static',filename='%s/%s' % ('video', filename1))
                post.filename5 = file5.filename

        db.session.add(post)
        if english == "yes":
            flash('The blog has been uploaded.')
        else:
            flash('帖子已经提交。')
        if 'posts' in tag:
            return redirect(url_for('.user',username=current_user.username))
        if 'suggestion' in tag:
            return redirect(url_for('.suggestion'))
        if 'newlesson' in tag:
            return redirect(url_for('.current_lesson',newlesson_id=int(tag.split('_')[1]),tag=tag))
    return render_template('write2.html', form=form,enctype=enctype,tag=tag, english=english)



@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    english=request.cookies.get('english')
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    if english == "yes":
        form = PostFormE()
    else:
        form = PostForm()
    if form.validate_on_submit():
        post.topic = form.topic.data
        post.body = form.body.data
        post.private = form.private.data

        pic = request.files['pic']
        size = (1024, 1024) 
        if pic and allowed_file(pic.filename):
            im = Image.open(pic)
            im.thumbnail(size)        
            filename = secure_filename(pic.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
            im.save(os.path.join('app/static', 'post', filename1))
            try:
                os.remove("/root/517shangke/app"+post.pic)
            except:
                pass
            post.pic = url_for('static',filename='%s/%s' % ('post', filename1))
      
        db.session.add(post)
        if english == "yes":
            flash('The blog has been updated.')
        else:
            flash('帖子已经修改。')
        if post.tag != None and 'suggestion' in post.tag:
            return redirect(url_for('.suggestion'))
        elif post.tag != None and 'newlessons' in post.tag:
            return redirect(url_for('.current_lesson',newlesson_id=int(post.tag.split('_')[1]),tag=post.tag))
        else:
            return redirect(url_for('.post', id=post.id))
    form.topic.data = post.topic
    form.body.data = post.body
    form.private.data = post.private
    return render_template('edit_post.html', form=form,id=id, tag=post.tag, english=english)


@main.route('/edit2/<int:id>', methods=['GET', 'POST'])
@login_required
def edit2(id):
    english=request.cookies.get('english')
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    if english == "yes":
        form = PostFormE2()
    else:
        form = PostForm2()
    if form.validate_on_submit():
        post.topic = form.topic.data
        post.body = form.body.data
        post.private = form.private.data

        pic = request.files['pic']
        size = (1024, 1024) 
        if pic and allowed_file(pic.filename):
            im = Image.open(pic)
            im.thumbnail(size)        
            filename = secure_filename(pic.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
            im.save(os.path.join('app/static', 'post', filename1))
            try:
                os.remove("/root/517shangke/app"+post.pic)
            except:
                pass    
                    
            post.pic = url_for('static',filename='%s/%s' % ('post', filename1))

        pic1 = request.files['pic1']
        size = (1024, 1024) 
        if pic1 and allowed_file(pic1.filename):
            im = Image.open(pic1)
            im.thumbnail(size)        
            filename = secure_filename(pic1.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' + str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            im.save(os.path.join('app/static', 'post', filename1))
            try:
                os.remove("/root/517shangke/app"+post.pic1)
            except:
                pass
            post.pic1 = url_for('static',filename='%s/%s' % ('post', filename1))

        pic2 = request.files['pic2']
        size = (1024, 1024) 
        if pic2 and allowed_file(pic2.filename):
            im = Image.open(pic2)
            im.thumbnail(size)        
            filename = secure_filename(pic2.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' + str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            im.save(os.path.join('app/static', 'post', filename1))
            try:
                os.remove("/root/517shangke/app"+post.pic2)
            except:
                pass
            post.pic2 = url_for('static',filename='%s/%s' % ('post', filename1))

        pic3 = request.files['pic3']
        size = (1024, 1024) 
        if pic3 and allowed_file(pic3.filename):
            im = Image.open(pic3)
            im.thumbnail(size)        
            filename = secure_filename(pic3.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' + str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            im.save(os.path.join('app/static', 'post', filename1))
            try:
                os.remove("/root/517shangke/app"+post.pic3)
            except:
                pass
            post.pic3 = url_for('static',filename='%s/%s' % ('post', filename1))

        file1 = request.files['file1']
        if file1 and allowed_file(file1.filename):
            filename = secure_filename(file1.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            file1.save(os.path.join('app/static', 'file', filename1))
            try:
                os.remove("/root/517shangke/app"+post.file1)
            except:
                pass
            post.file1 = url_for('static',filename='%s/%s' % ('file', filename1))
            post.filename1 = file1.filename        

        file2 = request.files['file2']
        if file2 and allowed_file(file2.filename):
            filename = secure_filename(file2.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            file2.save(os.path.join('app/static', 'file', filename1))
            try:
                os.remove("/root/517shangke/app"+post.file2)
            except:
                pass
            post.file2 = url_for('static',filename='%s/%s' % ('file', filename1))
            post.filename2 = file2.filename        

        file3 = request.files['file3']
        if file3 and allowed_file(file3.filename):
            filename = secure_filename(file3.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            file3.save(os.path.join('app/static', 'audio', filename1))
            try:
                os.remove("/root/517shangke/app"+post.file3)
            except:
                pass
            post.file3 = url_for('static',filename='%s/%s' % ('audio', filename1))
            post.filename3 = file3.filename        

        file4 = request.files['file4']
        if file4 and allowed_file(file4.filename):
            filename = secure_filename(file4.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            file4.save(os.path.join('app/static', 'video', filename1))
            try:
                os.remove("/root/517shangke/app"+post.file4)
            except:
                pass
            post.file4 = url_for('static',filename='%s/%s' % ('video', filename1))
            post.filename4 = file4.filename

        file5 = request.files['file5']
        if file5 and allowed_file(file5.filename):
            filename = secure_filename(file5.filename)
            filename1 = current_user.email.replace('@','__').replace('.','__') \
                        + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
            file5.save(os.path.join('app/static', 'video', filename1))
            try:
                os.remove("/root/517shangke/app"+post.file5)
            except:
                pass
            post.file5 = url_for('static',filename='%s/%s' % ('video', filename1))
            post.filename4 = file5.filename
            
        db.session.commit()
        flash('帖子已经修改。')
        if post.tag != None and 'suggestion' in post.tag:
            return redirect(url_for('.suggestion'))
        elif post.tag != None and 'newlessons' in post.tag:
            return redirect(url_for('.current_lesson',newlesson_id=int(post.tag.split('_')[1]),tag=post.tag))
        else:
            return redirect(url_for('.post', id=post.id))
    form.topic.data = post.topic
    form.body.data = post.body
    form.private.data = post.private
    return render_template('edit_post2.html', form=form, id=id, tag=post.tag, english=english)




@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    english=request.cookies.get('english')
    user = User.query.filter_by(username=username).first()
    if user is None:
        if english == "yes":
            flash('Invalid user.')
        else:
            flash('无效用户。')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        if english == "yes":
            flash('You have followed him/her.')
        else:
            flash('您已关注此人。')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    if english == "yes":
        flash('You have followed ' % username)
    else:
        flash('您已关注了 %s。' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    english=request.cookies.get('english')
    user = User.query.filter_by(username=username).first()
    if user is None:
        if english == "yes":
            flash('无效用户，')
        else:
            flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        if english == "yes":
            flash("You haven't followed him/her.")
        else:
            flash('您没有关注此人。')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    if english == "yes":
        flash('You do not follow %s any more。' % username)
    else:
        flash('您不再关注 %s 。' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    english=request.cookies.get('english')
    user = User.query.filter_by(username=username).first()
    if user is None:
        if english == "yes":
            flash('Invalid user.')
        else:
            flash('无效用户。')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, 
                           endpoint='.followers', pagination=pagination,
                           follows=follows, english=english)


@main.route('/followed-by/<username>')
def followed_by(username):
    english=request.cookies.get('english')
    user = User.query.filter_by(username=username).first()
    if user is None:
        if english == "yes":
            flash('Invalid user.')
        else:
            flash('无效用户。')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followered-by.html', user=user, 
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows, english=english)


@main.route('/show-write')
@login_required
def show_write():
    resp = make_response(redirect(url_for('.write')))
    resp.set_cookie('show_write', '1', max_age=30*24*60*60)
    return resp


@main.route('/del-user/<int:id>')
@login_required
def del_user(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('.user',username=current_user.username))


@main.route('/del-teacher/<int:id>')
@login_required
def del_teacher(id):
    Teacher.query.filter_by(id=id).delete()
    current_user.teacher = 0
    db.session.commit()
    return redirect(url_for('.user',username=current_user.username))


@main.route('/del-post/<int:id>')
@login_required
def del_post(id):
    post = Post.query.filter_by(id=id).first()
    tag = post.tag
    if post.pic != None:
        try:
            os.remove("/root/517shangke/app"+post.pic)
        except:
            pass    
    if post.pic1 != None:
        try:
            os.remove("/root/517shangke/app"+post.pic1)
        except:
            pass    
    if post.pic2 != None:
        try:
            os.remove("/root/517shangke/app"+post.pic2)
        except:
            pass    
    if post.pic3 != None:
        try:
            os.remove("/root/517shangke/app"+post.pic3)
        except:
            pass    
    if post.file1 != None:
        try:
            os.remove("/root/517shangke/app"+post.file1)
        except:
            pass    
    if post.file2 != None:
        try:
            os.remove("/root/517shangke/app"+post.file2)
        except:
            pass    
    if post.file3 != None:
        try:
            os.remove("/root/517shangke/app"+post.file3)
        except:
            pass    
    if post.file4 != None:
        try:
            os.remove("/root/517shangke/app"+post.file4)
        except:
            pass    
    if post.file5 != None:
        try:
            os.remove("/root/517shangke/app"+post.file5)
        except:
            pass     
    db.session.delete(Post.query.get_or_404(id))
    db.session.commit()
    if 'posts' in tag:
        return redirect(url_for('.user',username=current_user.username))
    if 'suggestion' in tag:
        return redirect(url_for('.suggestion'))
    else:
        return redirect(url_for('.current_lesson',newlesson_id=int(tag.split('_')[1]),tag=tag))


@main.route('/del-comment/<int:id>/<int:id2>')
@login_required
def del_comment(id,id2):
    AtMe.query.filter_by(comment_id=id).delete()
    db.session.delete(Comment.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('.post',id=id2))


@main.route('/del-comment2/<int:id>')
@login_required
def del_comment2(id):
    db.session.delete(Comment.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('.sent_comments',user_id=current_user.id))

@main.route('/open-lesson', methods=['GET', 'POST'])
@login_required
def open_lesson():
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = AddLessonFormE(values)
    else:
        form = AddLessonForm(values)
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        lesson = Lesson(lesson_name=form.lesson_name.data,\
                        about_lesson=form.about_lesson.data,teacher_id=current_user.id)
        if request.method == 'POST':
            pic = request.files['pic']
            size = (1024, 1024) 
            if pic and allowed_file(pic.filename):
                im = Image.open(pic)
                im.thumbnail(size)        
                filename = secure_filename(pic.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'lesson', filename1))
                lesson.pic = url_for('static',filename='%s/%s' % ('lesson', filename1))      

            file1 = request.files['file1']
            if file1 and allowed_file(file1.filename):
                filename = secure_filename(file1.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file1.save(os.path.join('app/static', 'file', filename1))
                lesson.file1 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename1 = file1.filename        
    
            file2 = request.files['file2']
            if file2 and allowed_file(file2.filename):
                filename = secure_filename(file2.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file2.save(os.path.join('app/static', 'file', filename1))
                lesson.file2 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename2 = file2.filename        
    
            file3 = request.files['file3']
            if file3 and allowed_file(file3.filename):
                filename = secure_filename(file3.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file3.save(os.path.join('app/static', 'file', filename1))
                lesson.file3 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename3 = file3.filename      
    
            file4 = request.files['file4']
            if file4 and allowed_file(file4.filename):
                filename = secure_filename(file4.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file4.save(os.path.join('app/static', 'file', filename1))
                lesson.file4 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename4 = file4.filename

            file5 = request.files['file5']
            if file5 and allowed_file(file5.filename):
                filename = secure_filename(file5.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file5.save(os.path.join('app/static', 'lessonfile', filename1))
                lesson.file5 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename5 = file5.filename
                
    
            file6 = request.files['file6']
            if file6 and allowed_file(file6.filename):
                filename = secure_filename(file6.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file6.save(os.path.join('app/static', 'lessonfile', filename1))
                lesson.file6 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename6 = file6.filename
                
    
            file7 = request.files['file7']
            if file7 and allowed_file(file7.filename):
                filename = secure_filename(file7.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file7.save(os.path.join('app/static', 'lessonfile', filename1))
                lesson.file7 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename7 = file7.filename
                
    
            file8 = request.files['file8']
            if file8 and allowed_file(file8.filename):
                filename = secure_filename(file8.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file8.save(os.path.join('app/static', 'lessonfile', filename1))
                lesson.file8 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename8 = file8.filename
                                    
        db.session.add(lesson)
        lessons = Lesson.query.filter_by(teacher_id=current_user.id).all()
        return redirect(url_for('main.lesson',id=lessons[-1].id))
    return render_template('open_lesson.html', form=form, english=english)

@main.route('/edit-lesson/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_lesson(id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = AddLessonFormE(values)
    else:
        form = AddLessonForm(values)
    lesson = Lesson.query.filter_by(id=id).first()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        lesson.lesson_name = form.lesson_name.data
        lesson.about_lesson = form.about_lesson.data
        lesson.teacher_id = current_user.id
        if request.method == 'POST':
            pic = request.files['pic']
            size = (1024, 1024) 
            if pic and allowed_file(pic.filename):
                im = Image.open(pic)
                im.thumbnail(size)        
                filename = secure_filename(pic.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' + str(time.time()).replace('.','_') + '.' + filename.split('.')[-1]
                im.save(os.path.join('app/static', 'lesson', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.pic)
                except:
                    pass
                lesson.pic = url_for('static',filename='%s/%s' % ('lesson', filename1))   

            file1 = request.files['file1']
            if file1 and allowed_file(file1.filename):
                filename = secure_filename(file1.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file1.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file1)
                except:
                    pass
                lesson.file1 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename1 = file1.filename        
    
            file2 = request.files['file2']
            if file2 and allowed_file(file2.filename):
                filename = secure_filename(file2.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file2.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file2)
                except:
                    pass
                lesson.file2 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename2 = file2.filename        
    
            file3 = request.files['file3']
            if file3 and allowed_file(file3.filename):
                filename = secure_filename(file3.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file3.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file3)
                except:
                    pass
                lesson.file3 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename3 = file3.filename      
 
            file4 = request.files['file4']
            if file4 and allowed_file(file4.filename):
                filename = secure_filename(file4.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file4.save(os.path.join('app/static', 'file', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file4)
                except:
                    pass
                lesson.file4 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename4 = file4.filename

            file5 = request.files['file5']
            if file5 and allowed_file(file5.filename):
                filename = secure_filename(file5.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file5.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file5)
                except:
                    pass
                lesson.file5 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename5 = file5.filename
                
    
            file6 = request.files['file6']
            if file6 and allowed_file(file6.filename):
                filename = secure_filename(file6.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file6.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file6)
                except:
                    pass
                lesson.file6 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename6 = file6.filename
                
    
            file7 = request.files['file7']
            if file7 and allowed_file(file7.filename):
                filename = secure_filename(file7.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file7.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file7)
                except:
                    pass
                lesson.file7 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename7 = file7.filename
                
    
            file8 = request.files['file8']
            if file8 and allowed_file(file8.filename):
                filename = secure_filename(file8.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file8.save(os.path.join('app/static', 'lessonfile', filename1))
                try:
                    os.remove("/root/517shangke/app"+post.file8)
                except:
                    pass
                lesson.file8 = url_for('static',filename='%s/%s' % ('lessonfile', filename1))
                lesson.filename8 = file8.filename
                                    
        db.session.add(lesson)
        return redirect(url_for('.lesson',id=id))
    form.lesson_name.data=lesson.lesson_name
    form.about_lesson.data=lesson.about_lesson
    return render_template('edit_lesson.html', form=form,id=id,lesson=lesson, english=english)


@main.route('/del-lesson/<int:id>')
@login_required
def del_lesson(id):
    lesson = Lesson.query.filter_by(id=id).first()
    if lesson.file1 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file1)
        except:
            pass    
    if lesson.file2 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file2)
        except:
            pass    
    if lesson.file3 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file3)
        except:
            pass    
    if lesson.file4 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file4)
        except:
            pass    
    if lesson.file5 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file5)
        except:
            pass     
    if lesson.file6 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file6)
        except:
            pass    
    if lesson.file7 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file7)
        except:
            pass    
    if lesson.file8 != None:
        try:
            os.remove("/root/517shangke/app"+lesson.file8)
        except:
            pass             
    db.session.delete(Lesson.query.get_or_404(id))
    db.session.commit()
    teacher = Teacher.query.filter_by(teacher_id=current_user.id).first()
    return redirect(url_for('.teacher',id=teacher.teacher_id))

@main.route('/lesson-main', methods=['GET', 'POST'])
def lesson_main():
    english=request.cookies.get('english')
    page = request.args.get('page', 1, type=int)
    show_all_teacher = "0"
    show_all_teacher = request.cookies.get('show_all_teacher', '')
    teachers = Teacher.query.filter(Teacher.id>0).all()
    teachers_all = []
    for teacher in teachers:
        user = User.query.filter_by(id=teacher.teacher_id).first()
        if user.teacher:
            lessons = Lesson.query.filter_by(teacher_id=teacher.teacher_id).all()
            teachers_all.append([teacher,user,lessons])
    pagination = Lesson.query.\
                          order_by(Lesson.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    lessons = pagination.items
    n = len(lessons)
    users = []
    for lesson in lessons:
        users.append(User.query.filter_by(id = lesson.teacher_id).first())
    return render_template('lesson_main.html', lessons=lessons,users=users,
                           show_all_teacher=show_all_teacher, n=n,
                           pagination=pagination, teachers_all=teachers_all,english=english)

@main.route('/lesson/<int:id>')
def lesson(id):
    english=request.cookies.get('english')
    lesson = Lesson.query.filter_by(id=id).first()
    user_teacher = User.query.filter_by(id=lesson.teacher_id).first()   
    teacher = Teacher.query.filter_by(teacher_id=lesson.teacher_id).first()
    newlessons = NewLesson.query.filter_by(lesson_id=id).all()
    show_all_class = "0"
    show_all_class = request.cookies.get('show_all_class', '')
    students = []
    if current_user.is_authenticated:
        students = Student.query.filter_by(student_id=current_user.id).all() 
    mylessons = []
    for s in students:
        nl = NewLesson.query.filter_by(id=s.newlesson_id).first()
        if nl in newlessons:
            mylessons.append(nl)
    lesson_files = []
    lessonfiles = LessonFile.query.filter_by(lesson_id=id).order_by(LessonFile.timestamp.desc()).all()
    for lf in lessonfiles:
        lesson_files.append([lesson,lf])
    lesson_discussions = []
    for newlesson in newlessons:
        posts = Post.query.filter_by(tag="newlessons_"+str(newlesson.id)).order_by(Post.timestamp.desc()).all()
        for p in posts:
            user2 = User.query.filter_by(id=p.author_id).first()
            lesson_discussions.append([lesson,newlesson,p,user2])
    lesson_students = []
    newlessons = NewLesson.query.filter_by(lesson_id=lesson.id).order_by(NewLesson.timestamp.desc()).all()
    for newlesson in newlessons:
        students = Student.query.filter_by(newlesson_id=newlesson.id).order_by(Student.timestamp.desc()).all()
        for student in students:
            user3 = User.query.filter_by(id=student.student_id).first()
            lesson_students.append([lesson,newlesson,user3])
    return render_template('lesson.html',lesson=lesson,user_teacher=user_teacher,\
                           lesson_files=lesson_files,lesson_discussions=lesson_discussions,\
                           lesson_students=lesson_students,\
                       newlessons=newlessons,mylessons=mylessons,teacher=teacher,show_all_class=show_all_class, english=english)






















#    elif show_all_class == "2":
#        pass
#    elif show_all_class == "3":
#        pass
#    else:
#        students = Student.query.filter_by(newlesson_id=newlesson_id).all()
#        student = None
#        if current_user.is_authenticated:
#            ss  = Student.query.filter_by(student_id=current_user.id).all()
#            if len(ss) != 0:
#                for s in ss:
#                    if s in students:
#                        student = s
#        
#        users_confirmed = []
#        users_unconfirmed = []
#        for s in students:
#            if s.confirm:
#                users_confirmed.append(User.query.filter_by(id=s.student_id).first())            
#            else:
#                users_unconfirmed.append(User.query.filter_by(id=s.student_id).first())
#    
#        newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
#        lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
#        user = User.query.filter_by(id=lesson.teacher_id).first() 
#    
#        page = request.args.get('page', 1, type=int)
#    
#        pagination = Post.query.filter(Post.tag == "newlessons_"+str(newlesson_id)).\
#                              order_by(Post.timestamp.desc()).paginate(
#                              page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#                                                               error_out=False)
#        posts = pagination.items
#        
#        return render_template('current_lesson.html',user=user,lesson=lesson,\
#                               student=student,users_confirmed=users_confirmed,\
#                               users_unconfirmed=users_unconfirmed,\
#                               newlesson=newlesson, show_lesson_discussion=show_lesson_discussion,posts=posts, english=english)        
#        

@main.route('/current-lesson/<int:newlesson_id>',methods=['GET', 'POST'])
def current_lesson(newlesson_id):
    english=request.cookies.get('english')

    show_lesson_discussion = "0"
    show_lesson_discussion = request.cookies.get('show_lesson_discussion', '')

    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
    teacher = User.query.filter_by(id=lesson.teacher_id).first()    
    students = Student.query.filter_by(newlesson_id=newlesson_id).all()

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.tag == "newlessons_"+str(newlesson_id)).\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts = pagination.items
    pagination_teacher = Post.query.filter(Post.tag == "newlessons_"+str(newlesson_id)).\
                                          filter_by(author_id=teacher.id).\
                          order_by(Post.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts_teacher = pagination_teacher.items



    student = None
    if current_user.is_authenticated:
        ss  = Student.query.filter_by(student_id=current_user.id).all()
        if len(ss) != 0:
            for s in ss:
                if s in students:
                    student = s
    
    users_confirmed_posts = []
    for s in students:
        if s.confirm:
            if Post.query.filter_by(topic=s.topic).filter_by(author_id=s.student_id).first():
                users_confirmed_posts.append([s,User.query.filter_by(id=s.student_id).first(),\
                                        Post.query.filter_by(topic=s.topic).first().id])
    users_confirmed = []
    users_unconfirmed = []
    for s in students:
        if s.confirm:
            users_confirmed.append(User.query.filter_by(id=s.student_id).first())            
        else:
            users_unconfirmed.append(User.query.filter_by(id=s.student_id).first())
    if len(students)>1:
        n = random.randint(0,len(students)-1)
        replier = User.query.filter_by(id=students[n].student_id).first()
    else:
        replier = ""

    if request.method == 'POST':
        if current_user==teacher:
            seat = request.form['seat']
            student = Student.query.filter_by(seat=seat).first()
            student.absence = student.absence + 1
            db.session.commit()           
        else:
            student.seat = request.form['seat']
            db.session.commit()
        
    seats = []
    absences = []
    for i in range(newlesson.room_row):
        if i < 9:
            row = "0" + str(i+1)
        else:
            row = str(i+1)
        for j in range(newlesson.room_column):
            if j < 9:
                column = "0" + str(j+1)
            else:
                column = str(j+1)            
            flag = 0
            seat = row + column
            for s in students:
                if s.seat != None:
                    if i+1==int(s.seat[0:2]) and j+1==int(s.seat[2:4]):
                        seats.append(User.query.filter_by(id=s.student_id).first().name)
                        absences.append(s.absence)
                        flag = 1
                        break
            if flag == 0:
                seats.append(seat)
                absences.append('')
    return render_template('current_lesson.html',teacher=teacher,lesson=lesson,\
                               student=student,posts=posts,posts_teacher=posts_teacher,\
                               users_confirmed=users_confirmed,users_unconfirmed=users_unconfirmed,\
                               users_confirmed_posts=users_confirmed_posts,\
                               replier=replier, seats=seats,absences=absences,\
                               newlesson=newlesson, show_lesson_discussion=show_lesson_discussion,english=english)        
               

@main.route('/show-lesson-discussion/<int:newlesson_id>')
def show_lesson_discussion(newlesson_id):
    resp = make_response(redirect(url_for('main.current_lesson',newlesson_id=newlesson_id)))
    resp.set_cookie('show_lesson_discussion', '0', max_age=30*24*60*60)
    return resp

@main.route('/show-lesson-namelist/<int:newlesson_id>')
def show_lesson_namelist(newlesson_id):
    resp = make_response(redirect(url_for('main.current_lesson',newlesson_id=newlesson_id)))
    resp.set_cookie('show_lesson_discussion', '1', max_age=30*24*60*60)
    return resp


@main.route('/show-lesson-seat/<int:newlesson_id>')
def show_lesson_seat(newlesson_id):
    resp = make_response(redirect(url_for('main.current_lesson',newlesson_id=newlesson_id)))
    resp.set_cookie('show_lesson_discussion', '2', max_age=30*24*60*60)
    return resp


@main.route('/show-lesson-exercise/<int:newlesson_id>')
def show_lesson_exercise(newlesson_id):
    resp = make_response(redirect(url_for('main.current_lesson',newlesson_id=newlesson_id)))
    resp.set_cookie('show_lesson_discussion', '3', max_age=30*24*60*60)
    return resp

@main.route('/show-lesson-notice/<int:newlesson_id>')
def show_lesson_notice(newlesson_id):
    resp = make_response(redirect(url_for('main.current_lesson',newlesson_id=newlesson_id)))
    resp.set_cookie('show_lesson_discussion', '4', max_age=30*24*60*60)
    return resp




#@main.route('/current-lesson-namelist/<int:newlesson_id>',methods=['GET', 'POST'])
#def current_lesson_namelist(newlesson_id):
#    english=request.cookies.get('english')
#    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
#    student = None
#    if current_user.is_authenticated:
#        ss  = Student.query.filter_by(student_id=current_user.id).all()
#        if len(ss) != 0:
#            for s in ss:
#                if s in students:
#                    student = s
#                    
#    users_confirmed = []
#    users_unconfirmed = []
#    for s in students:
#        if s.confirm:
#            users_confirmed.append(User.query.filter_by(id=s.student_id).first())            
#        else:
#            users_unconfirmed.append(User.query.filter_by(id=s.student_id).first())
#
#    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
#    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
#    user = User.query.filter_by(id=lesson.teacher_id).first() 
#
#    
#    return render_template('current_lesson_namelist.html',user=user,lesson=lesson,\
#                           student=student,users_confirmed=users_confirmed,\
#                           users_unconfirmed=users_unconfirmed,\
#                           newlesson=newlesson, english=english)
#
#
#@main.route('/current-lesson-absence/<int:newlesson_id>',methods=['GET', 'POST'])
#@login_required
#def current_lesson_absence(newlesson_id):
#    english=request.cookies.get('english')
#    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
#    student = None
#    if current_user.is_authenticated:
#        ss  = Student.query.filter_by(student_id=current_user.id).all()
#        if len(ss) != 0:
#            for s in ss:
#                if s in students:
#                    student = s
#                    
#    if len(students)>1:
#        n = random.randint(0,len(students)-1)
#        replier = User.query.filter_by(id=students[n].student_id).first()
#    else:
#        replier = ""
#    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
#    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
#    teacher_user = User.query.filter_by(id=lesson.teacher_id).first() 
#    user = User.query.filter_by(id=lesson.teacher_id).first()
#    if request.method == 'POST':
#        if current_user==teacher_user:
#            seat = request.form['seat']
#            student = Student.query.filter_by(seat=seat).first()
#            student.absence = student.absence + 1
#            db.session.commit()           
#        else:
#            student.seat = request.form['seat']
#            db.session.commit()
#        
#    seats = []
#    absences = []
#    for i in range(newlesson.room_row):
#        if i < 9:
#            row = "0" + str(i+1)
#        else:
#            row = str(i+1)
#        for j in range(newlesson.room_column):
#            if j < 9:
#                column = "0" + str(j+1)
#            else:
#                column = str(j+1)            
#            flag = 0
#            seat = row + column
#            for s in students:
#                if s.seat != None:
#                    if i+1==int(s.seat[0:2]) and j+1==int(s.seat[2:4]):
#                        seats.append(User.query.filter_by(id=s.student_id).first().name)
#                        absences.append(s.absence)
#                        flag = 1
#                        break
#            if flag == 0:
#                seats.append(seat)
#                absences.append('')
#    return render_template('current_lesson_absence.html',user=user,lesson=lesson,\
#                           student=student,\
#                           newlesson=newlesson,seats=seats,absences=absences,replier=replier, english=english)
#
#@main.route('/current-lesson-topic/<int:newlesson_id>',methods=['GET', 'POST'])
#@login_required
#def current_lesson_topic(newlesson_id):
#    english=request.cookies.get('english')
#    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
#    student = None
#    if current_user.is_authenticated:
#        ss  = Student.query.filter_by(student_id=current_user.id).all()
#        if len(ss) != 0:
#            for s in ss:
#                if s in students:
#                    student = s
#    
#    users_confirmed = []
#    users_unconfirmed = []
#    for s in students:
#        if s.confirm:
#            if Post.query.filter_by(topic=s.topic).filter_by(author_id=s.student_id).first():
#                users_confirmed.append([s,User.query.filter_by(id=s.student_id).first(),\
#                                        Post.query.filter_by(topic=s.topic).first().id])
##                Post.query.filter(Post.topic==s.topic and Post.author_id==s.student_id).first().id])
#            else:
#                users_confirmed.append([s,User.query.filter_by(id=s.student_id).first(),None])
#                
#    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
#    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
#    user = User.query.filter_by(id=lesson.teacher_id).first() 
#    return render_template('current_lesson_topic.html',user=user,lesson=lesson,\
#                           student=student,users_confirmed=users_confirmed,\
#                           users_unconfirmed=users_unconfirmed,\
#                           newlesson=newlesson, english=english)
#
#    
#@main.route('/current-lesson-discussion/<int:newlesson_id>', methods=['GET', 'POST'])
#@login_required
#def current_lesson_discussion(newlesson_id):
#    english=request.cookies.get('english')
#    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
#    users_confirmed = []
#    users_unconfirmed = []
#    for s in students:
#        if s.confirm:
#            users_confirmed.append(User.query.filter_by(id=s.student_id).first())            
#        else:
#            users_unconfirmed.append(User.query.filter_by(id=s.student_id).first())
#    if current_user.is_authenticated:
#        student = Student.query.filter_by(student_id=current_user.id).first()
#    else:
#        student = None
#
#    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
#    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
#    user = User.query.filter_by(id=lesson.teacher_id).first() 
#
#    page = request.args.get('page', 1, type=int)
#    show_lesson_discussion = "0"
#    if current_user.is_authenticated:
#        show_lesson_discussion = bool(request.cookies.get('show_lesson_discussion', ''))
#
#    pagination = Post.query.filter(Post.tag == "newlessons_" + str(newlesson_id)).\
#                          order_by(Post.timestamp.desc()).paginate(
#                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#                                                           error_out=False)
#    posts = pagination.items
#    return render_template('current_lesson_discussion.html', posts=posts,pagination=pagination,\
#         show_lesson_discussion=show_lesson_discussion, newlesson=newlesson,lesson=lesson,user=user,student=student, english=english)













@main.route('/select-lesson/<int:newlesson_id>')
@login_required
def select_lesson(newlesson_id):
    english=request.cookies.get('english')
    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()
    if current_user.id == lesson.teacher_id:
        if english == "yes":
            flash('The teacher of the class cannot select the class.')
        else:
            flash("开课老师不能选修自己的课程。")
        return redirect(url_for('main.lesson',id=lesson.id))
    if current_user.name == None or current_user.tel == None or \
        current_user.location == None or current_user.about_me == None:
        if english == "yes":
            flash('Please update your profile.')
        else:
            flash("请先完善个人资料。")
        return redirect(url_for('main.lesson',id=lesson.id))
    students = Student.query.filter_by(student_id=current_user.id).all()
    for s in students:
        if s.newlesson_id == newlesson_id:
            if english == "yes":
                flash('You have selected the class.')
            else:
                flash('你已经选了该课程。')
            return redirect(url_for('main.lesson',id=newlesson.lesson_id))
    student = Student(student_id=current_user.id,newlesson_id=newlesson_id,confirm=0)
    db.session.add(student)
    return redirect(url_for('main.current_lesson',newlesson_id=newlesson_id))



@main.route('/update-topic/<int:newlesson_id>',methods=['GET', 'POST'])
@login_required
def update_topic(newlesson_id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = UpdateTopicFormE(values)
    else:
        form = UpdateTopicForm(values)

    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
    student = None
    if current_user.is_authenticated:
        ss  = Student.query.filter_by(student_id=current_user.id).all()
        if len(ss) != 0:
            for s in ss:
                if s in students:
                    student = s
                    post = Post.query.filter_by(topic=student.topic).first()
    users_confirmed = []
    for s in students:
        if s.confirm:
            users_confirmed.append(User.query.filter_by(id=s.student_id).first())            

    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
    lesson = Lesson.query.filter_by(id=newlesson.lesson_id).first()   
    user = User.query.filter_by(id=lesson.teacher_id).first() 
    
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        student.topic = request.form['topic']
        student.body = request.form['body']
        if request.method == 'POST':
            file1 = request.files['file1']
            if file1 and allowed_file(file1.filename):
                filename = secure_filename(file1.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file1.save(os.path.join('app/static', 'post', filename1))
                student.file1 = url_for('static',filename='%s/%s' % ('post', filename1))
                student.filename1 = file1.filename        
    
            file2 = request.files['file2']
            if file2 and allowed_file(file2.filename):
                filename = secure_filename(file2.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file2.save(os.path.join('app/static', 'post', filename1))
                student.file2 = url_for('static',filename='%s/%s' % ('post', filename1))
                student.filename2 = file2.filename        
    
            file3 = request.files['file3']
            if file3 and allowed_file(file3.filename):
                filename = secure_filename(file3.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file3.save(os.path.join('app/static', 'post', filename1))
                student.file3 = url_for('static',filename='%s/%s' % ('post', filename1))
                student.filename3 = file3.filename      
    
            file4 = request.files['file4']
            if file4 and allowed_file(file4.filename):
                filename = secure_filename(file4.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file4.save(os.path.join('app/static', 'file', filename1))
                student.file4 = url_for('static',filename='%s/%s' % ('post', filename1))
                student.filename4 = file4.filename
    
            file5 = request.files['file5']
            if file5 and allowed_file(file5.filename):
                filename = secure_filename(file5.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file5.save(os.path.join('app/static', 'post', filename1))
                student.file5 = url_for('static',filename='%s/%s' % ('post', filename1))
                student.filename5 = file5.filename
        if post != None and post.author_id == current_user.id and post.tag == 'newlessons_'+ str(newlesson_id):
            post.topic = student.topic
            post.body = student.body
            post.file1 = student.file1
            post.file2 = student.file2
            post.file3 = student.file3
            post.file4 = student.file4
            post.file5 = student.file5
            post.filename1 = student.filename1
            post.filename2 = student.filename2
            post.filename3 = student.filename3
            post.filename4 = student.filename4
            post.filename5 = student.filename5
        else:
            post = Post(topic=student.topic,body=student.body,file1 = student.file1,
                            file2 = student.file2,                            
                            file3 = student.file3,                            
                            file4 = student.file4,                            
                            file5 = student.file5,                            
                            filename1 = student.filename1,
                            filename2 = student.filename2,
                            filename3 = student.filename3,
                            filename4 = student.filename4,
                            filename5 = student.filename5,
                         tag='newlessons_'+ str(newlesson_id),
                        author=current_user._get_current_object())
        db.session.commit()
        return redirect(url_for('main.current_lesson',newlesson_id=newlesson_id,
                    user=user,newlesson=newlesson,\
                    users_confirmed=users_confirmed,student=student))
    form.topic.data = student.topic
    form.body.data = student.body
            
    return render_template('update_topic.html',form=form,newlesson_id=newlesson_id, english=english)

    
@main.route('/del-topic/<int:student_id>')
@login_required
def del_topic(student_id):
    student = Student.query.filter_by(id=student_id).first()
    student.topic = None
    student.body = None
    student.body_html = None
    student.file1 = None
    student.file2 = None
    student.file3 = None
    student.file4 = None
    student.file5 = None
    student.filename1 = None
    student.filename2 = None
    student.filename3 = None
    student.filename4 = None
    student.filename5 = None    
    return redirect(url_for('.current_lesson',newlesson_id=student.newlesson_id))    
    
    
@main.route('/open-new-lesson/<int:id>', methods=['GET', 'POST'])
@login_required
def open_new_lesson(id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = NewLessonFormE(values)
    else:
        form = NewLessonForm(values)
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        newlesson = NewLesson(year=form.year.data,season=form.season.data,\
                              room_row=form.room_row.data,\
                              room_column=form.room_column.data,\
                              about = form.about.data,lesson_id = id)
        db.session.add(newlesson)
        return redirect(url_for('main.lesson',id=id))
    return render_template('open_new_lesson.html', form=form, english=english)

    
@main.route('/upload-lesson-file/<int:id>', methods=['GET', 'POST'])
@login_required
def upload_lesson_file(id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = LessonFileFormE(values)
    else:
        form = LessonFileForm(values)
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        lessonfile = LessonFile(filetype=form.filetype.data,visibility=form.visibility.data,\
                              about = form.about.data,lesson_id = id)
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file.save(os.path.join('app/static', 'lesson', filename1))
                lessonfile.file = url_for('static',filename='%s/%s' % ('lesson', filename1))
                lessonfile.filename = file.filename               
        db.session.add(lessonfile)   
        return redirect(url_for('main.lesson',id=id))
    return render_template('upload_lesson_file.html', form=form, english=english)

@main.route('/edit-lesson-file/<int:file_id>/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson_file(file_id,lesson_id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    lessonfile = LessonFile.query.filter_by(id=file_id).first()
    if english == "yes":
        form = LessonFileFormE(values)
    else:
        form = LessonFileForm(values)
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        lessonfile.filetype=form.filetype.data
        lessonfile.visibility=form.visibility.data
        lessonfile.about = form.about.data
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename1 = current_user.email.replace('@','__').replace('.','__') \
                            + '__' +str(time.time()).replace('.','') + '.' + filename.split('.')[-1]
                file.save(os.path.join('app/static', 'lesson', filename1))
                lessonfile.file = url_for('static',filename='%s/%s' % ('lesson', filename1))
                lessonfile.filename = file.filename               
        db.session.commit()   
        return redirect(url_for('main.lesson',id=lesson_id))
    form.about.data = lessonfile.about
    form.filetype.data = lessonfile.filetype
    form.visibility.data = lessonfile.visibility
    return render_template('edit_lesson_file.html', form=form, file_id=file_id, lesson_id=lesson_id,english=english)

@main.route('/del-lesson-file/<int:file_id>/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def del_lesson_file(file_id,lesson_id):
    LessonFile.query.filter_by(id=file_id).delete()
    return redirect(url_for('main.lesson',id=lesson_id))

    
@main.route('/edit-new-lesson/<int:newlesson_id>', methods=['GET', 'POST'])
@login_required
def edit_new_lesson(newlesson_id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = NewLessonFormE(values)
    else:
        form = NewLessonForm(values)
    newlesson = NewLesson.query.filter_by(id=newlesson_id).first()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        newlesson.year=form.year.data
        newlesson.season=form.season.data
        newlesson.room_row=form.room_row.data
        newlesson.room_column=form.room_column.data
        newlesson.about = form.about.data
        db.session.commit()
        return redirect(url_for('main.current_lesson',newlesson_id=newlesson_id))
    form.year.data = newlesson.year
    form.season.data = newlesson.season
    form.room_row.data = newlesson.room_row
    form.room_column.data = newlesson.room_column
    form.about.data = newlesson.about
    return render_template('edit_new_lesson.html', form=form,newlesson_id=newlesson_id, english=english)


@main.route('/del-new-lesson/<int:newlesson_id>')
@login_required
def del_new_lesson(newlesson_id):
    db.session.delete(NewLesson.query.get_or_404(newlesson_id))
    db.session.commit()
    teacher = Teacher.query.filter_by(teacher_id=current_user.id).first()
    return redirect(url_for('.teacher',id=teacher.teacher_id))

@main.route('/del-student/<int:newlesson_id>/<int:student_id>')
@login_required
def del_student(newlesson_id,student_id,):
    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
    student = None
    if current_user.is_authenticated:
        ss  = Student.query.filter_by(student_id=student_id).all()
        if len(ss) != 0:
            for s in ss:
                if s in students:
                    student = s
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('.current_lesson',newlesson_id=newlesson_id))

@main.route('/auth-student/<int:newlesson_id>/<int:student_id>')
@login_required
def auth_student(newlesson_id,student_id):
    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
    student = None
    if current_user.is_authenticated:
        ss  = Student.query.filter_by(student_id=student_id).all()
        if len(ss) != 0:
            for s in ss:
                if s in students:
                    student = s
    student.confirm = 1
    db.session.commit()
    return redirect(url_for('.current_lesson',newlesson_id=newlesson_id))

@main.route('/del-student-from-teacher/<int:newlesson_id>/<int:student_id>')
@login_required
def del_student_from_teacher(newlesson_id,student_id,):
    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
    student = None
    if current_user.is_authenticated:
        ss  = Student.query.filter_by(student_id=student_id).all()
        if len(ss) != 0:
            for s in ss:
                if s in students:
                    student = s
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('.teacher',id=current_user.id))

@main.route('/auth-student-from-teacher/<int:newlesson_id>/<int:student_id>')
@login_required
def auth_student_from_teacher(newlesson_id,student_id):
    students = Student.query.filter_by(newlesson_id=newlesson_id).all()
    student = None
    if current_user.is_authenticated:
        ss  = Student.query.filter_by(student_id=student_id).all()
        if len(ss) != 0:
            for s in ss:
                if s in students:
                    student = s
    student.confirm = 1
    db.session.commit()
    return redirect(url_for('.teacher',id=current_user.id))



@main.route('/lesson-comment')
@login_required
def lesson_comments():
    english=request.cookies.get('english')
    return render_template('lesson_comments.html', english=english)


@main.route('/show-all-lesson')
def show_all_lesson():
    resp = make_response(redirect(url_for('main.lesson_main')))
    resp.set_cookie('show_all_teacher', '0', max_age=30*24*60*60)
    return resp


@main.route('/show-all-teacher')
def show_all_teacher():
    resp = make_response(redirect(url_for('main.lesson_main')))
    resp.set_cookie('show_all_teacher', '1', max_age=30*24*60*60)
    return resp

@main.route('/show-about-lesson/<int:id>')
def show_about_lesson(id):
    resp = make_response(redirect(url_for('main.lesson',id=id)))
    resp.set_cookie('show_all_class', '0', max_age=30*24*60*60)
    return resp

@main.route('/show-all-class/<int:id>')
def show_all_class(id):
    resp = make_response(redirect(url_for('main.lesson',id=id)))
    resp.set_cookie('show_all_class', '1', max_age=30*24*60*60)
    return resp


@main.route('/show-all-file/<int:id>')
def show_all_file(id):
    resp = make_response(redirect(url_for('main.lesson',id=id)))
    resp.set_cookie('show_all_class', '2', max_age=30*24*60*60)
    return resp


@main.route('/show-all-discussion/<int:id>')
def show_all_discussion(id):
    resp = make_response(redirect(url_for('main.lesson',id=id)))
    resp.set_cookie('show_all_class', '3', max_age=30*24*60*60)
    return resp


@main.route('/show-all-student/<int:id>')
def show_all_student(id):
    resp = make_response(redirect(url_for('main.lesson',id=id)))
    resp.set_cookie('show_all_class', '4', max_age=30*24*60*60)
    return resp


@main.route('/teacher/<int:id>')
def teacher(id):
    english=request.cookies.get('english')
    show_opened_lesson = "0"
    show_opened_lesson = request.cookies.get('show_opened_lesson', '')
    teacher = Teacher.query.filter_by(id=id).first_or_404()
    user = User.query.filter_by(id=teacher.teacher_id).first_or_404()
    lessons = Lesson.query.filter_by(teacher_id=id).order_by(Lesson.timestamp.desc()).all()
    lesson_files = []
    if lessons is not None:
        for lesson in lessons:
            lessonfiles = LessonFile.query.filter_by(lesson_id=lesson.id).order_by(LessonFile.timestamp.desc()).all()
            for lf in lessonfiles:
                lesson_files.append([lesson,lf])
    lesson_discussions = []
    if lessons is not None:
        for lesson in lessons:
            newlessons = NewLesson.query.filter_by(lesson_id=lesson.id).order_by(NewLesson.timestamp.desc()).all()
            for newlesson in newlessons:
                posts = Post.query.filter_by(tag="newlessons_"+str(newlesson.id)).order_by(Post.timestamp.desc()).all()
                for p in posts:
                    user2 = User.query.filter_by(id=p.author_id).first()
                    lesson_discussions.append([lesson,newlesson,p,user2])
    lesson_students = []
    if lessons is not None:
        for lesson in lessons:
            newlessons = NewLesson.query.filter_by(lesson_id=lesson.id).order_by(NewLesson.timestamp.desc()).all()
            for newlesson in newlessons:
                students = Student.query.filter_by(newlesson_id=newlesson.id).order_by(Student.timestamp.desc()).all()
                for student in students:
                    user3 = User.query.filter_by(id=student.student_id).first()
                    lesson_students.append([lesson,newlesson,user3,student])
    return render_template('teacher.html', teacher=teacher,user=user,lessons=lessons,\
                           lesson_files=lesson_files,lesson_discussions=lesson_discussions,\
                           lesson_students=lesson_students,
                           show_opened_lesson=show_opened_lesson,english=english)







@main.route('/show-about-teacher/<int:id>')
def show_about_teacher(id):
    resp = make_response(redirect(url_for('main.teacher',id=id)))
    resp.set_cookie('show_opened_lesson', '0', max_age=30*24*60*60)
    return resp



@main.route('/show-opened-lesson/<int:id>')
def show_opened_lesson(id):
    resp = make_response(redirect(url_for('main.teacher',id=id)))
    resp.set_cookie('show_opened_lesson', '1', max_age=30*24*60*60)
    return resp


@main.route('/show-opened-lesson-file/<int:id>')
def show_opened_lesson_file(id):
    resp = make_response(redirect(url_for('main.teacher',id=id)))
    resp.set_cookie('show_opened_lesson', '2', max_age=30*24*60*60)
    return resp


@main.route('/show-opened-lesson-discussion/<int:id>')
def show_opened_lesson_discussion(id):
    resp = make_response(redirect(url_for('main.teacher',id=id)))
    resp.set_cookie('show_opened_lesson', '3', max_age=30*24*60*60)
    return resp


@main.route('/show-opened-lesson-student/<int:id>')
def show_opened_lesson_student(id):
    resp = make_response(redirect(url_for('main.teacher',id=id)))
    resp.set_cookie('show_opened_lesson', '4', max_age=30*24*60*60)
    return resp



@main.route('/show-chosen-lesson')
@login_required
def show_chosen_lesson(username):
    resp = make_response(redirect(url_for('.lesson')))
    resp.set_cookie('show_chosen_lesson', '1', max_age=30*24*60*60)
    return resp

@main.route('/show-my-teach')
@login_required
def show_my_teach(username):
    resp = make_response(redirect(url_for('.user')))
    resp.set_cookie('show_my_teach', '1', max_age=30*24*60*60)
    return resp


@main.route('/show-open-lesson')
@login_required
def show_open_lesson(username):
    resp = make_response(redirect(url_for('.user')))
    resp.set_cookie('show_open_lesson', '1', max_age=30*24*60*60)
    return resp

@main.route('/collect/<int:post_id>/<int:is_collect>')
@login_required
def collect(post_id,is_collect):
    if is_collect:
        collectpost = CollectPost.query.filter_by(user_id=current_user.id).filter_by(post_id=post_id).first()
        db.session.delete(collectpost)        
    else:
        collectpost = CollectPost(user_id=current_user.id,post_id=post_id)
        db.session.add(collectpost)
    db.session.commit()
    return redirect(url_for('.post',id=post_id))

@main.route('/collection/<int:user_id>')
@login_required
def collection(user_id):
    english=request.cookies.get('english')
    values = CombinedMultiDict([flask.request.files,flask.request.form])
    if english == "yes":
        form = PostFormE(values)
    else:
        form = PostForm(values)
    page = request.args.get('page', 1, type=int)
    collectposts = CollectPost.query.filter_by(user_id=user_id).all()
    posts = []
    timestamps = []
    for cp in collectposts:        
        p = Post.query.filter_by(id=cp.post_id).filter_by(private=False).first()
        if p is not None:
            posts.append(p)
            timestamps.append(cp.timestamp)
    pagination = CollectPost.query.filter(CollectPost.user_id==current_user.id).order_by(CollectPost.timestamp.desc()).paginate(
                          page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                           error_out=False)
    posts2 = []
    if len(posts) != 0:
        timestamps2 = sorted(timestamps,reverse=True)
        for t in timestamps2:
            posts2.append(posts[timestamps.index(t)])
    return render_template('collection.html', form=form, posts=posts2, pagination=pagination, english=english)

@main.route('/white-board')
def white_board():
    english=request.cookies.get('english')
    return render_template('white_board.html', english=english)

@main.route('/clock')
def clock():
    english=request.cookies.get('english')
    return render_template('clock.html', english=english)

@main.route('/countdown')
def countdown():
    english=request.cookies.get('english')
    return render_template('countdown.html', english=english)

@main.route('/tools')
def tools():
    english=request.cookies.get('english')
    return render_template('tools.html', english=english)

@main.route('/claculator')
def calculator():
    english=request.cookies.get('english')
    return render_template('calculator.html', english=english)


@main.route('/claculator-science')
def calculator_science():
    english=request.cookies.get('english')
    return render_template('calculator_science.html', english=english)


@main.route('/claculator-date')
def calculator_date():
    english=request.cookies.get('english')
    return render_template('calculator_date.html', english=english)

#@main.route('/collection/<int:sender_id>/<int:receiver_id>')
#@login_required
#def letter(sender_id,receiver_id):
#    pass

@main.route('/criticism/<int:newlesson_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def criticism(newlesson_id,student_id):
    english=request.cookies.get('english')
    student = Student.query.filter_by(id=student_id).first()
    user = User.query.filter_by(id=student.student_id).first()
    if english == "yes":
        form = CriticismFormE()
    else:
        form = CriticismForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        student.criticism = form.criticism.data
        student.score = form.score.data
        db.session.commit()
        return redirect(url_for('.current_lesson',id=current_user.id,newlesson_id=newlesson_id,english=english))   
    return render_template('criticism.html', form=form,user=user,newlesson_id=newlesson_id,english=english)


@main.route('/edit-criticism/<int:newlesson_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_criticism(newlesson_id,student_id):
    english=request.cookies.get('english')
    student = Student.query.filter_by(id=student_id).first()
    user = User.query.filter_by(id=student.student_id).first()
    if english == "yes":
        form = CriticismFormE()
    else:
        form = CriticismForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        student.criticism = form.criticism.data
        student.score = form.score.data
        db.session.commit()
        return redirect(url_for('.current_lesson',id=current_user.id,newlesson_id=newlesson_id,english=english))   
    form.criticism.data = student.criticism
    form.score.data = student.score
    return render_template('criticism.html', form=form,user=user,newlesson_id=newlesson_id,english=english)

#
#@main.route('/vote/<int:post_id>/<int:user_id>')
#@login_required
#def vote(post_id,user_id):
#    english=request.cookies.get('english')
#    vote = Vote.query.filter_by(post_id=post_id).filter_by(user_id=user_id).first()
#    if vote == None:
#        vote = Vote(post_id=post_id,user_id=user_id)
#        db.session.add(vote)
#        if english == "yes":
#            flash('已经点赞！')
#        else:
#            flash('You have voted successfully!')
#    else:
#        if english == "yes":
#            flash('已经点过赞了！')
#        else:
#            flash('You have ever already voted!')
#    return redirect(url_for(s=post_id))
#
#        
