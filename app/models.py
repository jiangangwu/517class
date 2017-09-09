from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80
    ALLOWED_EXTENSIONS = set(['bmp','BMP','jif','JIF','JPG','jpg','JPEG','jpeg','PNG','png','txt','TXT','pdf','PDF','xls','XLS','xlsx','XLSX','ppt','PPT','pptx','PPTX','doc','DOC','docx','DOCX', 'zip', 'ZIP', 'rar', 'RAR','wav','mp3','ogg','Wav','Mp3','Ogg','WAV','MP3','OGG','Mp4','Mpeg4','WebM','mp4','mpeg4','webm','MP4','MPEG4','WEBM','mov','MOV','Mov','mpg','MPG','Mpg','avi','AVI','Avi'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Permission.ALLOWED_EXTENSIONS


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    default = db.Column(db.Boolean, default=False, nullable=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    __table_args__ = {"useexisting": True}
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CollectPost(db.Model):
    __tablename__ = 'collectposts'
    __table_args__ = {"useexisting": True}
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'),primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Letter(db.Model):
    __tablename__ = 'letters'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    
    body = db.Column(db.Text())
    
    body_html = db.Column(db.Text)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    sendername = db.Column(db.String, db.ForeignKey('users.username'))
    receivername = db.Column(db.String, db.ForeignKey('users.username'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Letter(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     sender=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3','h4', 'p','br','u','del','tt','cite',
                        'font','big','small','strike','sup','sub','span','img','kdb']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_letter', id=self.id, _external=True),
            'topic':self.topic,
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'sender': url_for('api.get_sender', id=self.sendername,
                              _external=True),
            'receiver': url_for('api.get_receiver', id=self.receivername,
                              _external=True),
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('信件内容不能为空。')
        return Letter(body=body)
    
    def count_sender(self):
        return Letter.query.filter_by(sendername=self.username).count()
    def count_receiver(self):
        return Letter.query.filter_by(receivername=self.username).count()

    
#class Vote:
#    __tablename__ = 'votes'
#    __table_args__ = {"useexisting": True}
#    id = db.Column(db.Integer, primary_key=True)
#
#    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#    
#    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
#    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#    
#    def count_vote(self,post_id):
#        votes = self.query.filter_by(post_id=post_id).all()
#        return len(votes)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    student_no = db.Column(db.Integer)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(64))  
    confirmed = db.Column(db.Boolean, default=False)
    teacher = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    tel = db.Column(db.String(64))
    about_me = db.Column(db.Text(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    avatar_file = db.Column(db.String(64))

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    letters = db.relationship('Letter', foreign_keys=[Letter.sendername], backref='sender', lazy='dynamic')
    letters = db.relationship('Letter', foreign_keys=[Letter.receivername], backref='receiver', lazy='dynamic')
    clicktimes = db.relationship('ClickTime', backref='click_user', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    teachers = db.relationship('Teacher', backref='teacher', lazy='dynamic')
    lessons = db.relationship('Lesson', backref='lessonteacher', lazy='dynamic')
    students = db.relationship('Student', backref='student', lazy='dynamic')
    collectposts = db.relationship('CollectPost', backref='collect_user', lazy='dynamic')
    atmes = db.relationship('AtMe', backref='atme_username', lazy='dynamic')
#    votes = db.relationship('Vote', backref='voter', lazy='dynamic')

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def n_commented(self):
        lnth = 0
        for post in Post.query.filter(self.id==Post.author_id).all():
            comments = Comment.query.filter(post.id==Comment.post_id).all()
            lnth += len(comments)
        return lnth
    
    def n_commented_new(self):
        lnth = 0
        posts = Post.query.filter_by(author_id=self.id).all()    
        for post in posts:
            comments = Comment.query.filter_by(post_id=post.id).all()
            if len(comments) != 0:
                for comment in comments:
                    if comment.timestamp > self.last_seen:
                        lnth += 1
        return lnth
    
    def n_collected(self):
        collections = CollectPost.query.filter(self.id==CollectPost.user_id).all()
        lnth = len(collections)
        return lnth

    def commented(self):
        commented_ = []
        for post in Post.query.filter(self.id==Post.author_id).all():
            commented_.append([post,Comment.query.filter(post.id==Comment.post_id).all()])
        return commented_

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('密码为不可读。')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None
            
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username
 
    def count_atme(self):
        return AtMe.query.filter_by(username=self.username).count()

    def count_private(self):
        return Post.query.filter_by(author_id=self.id).filter_by(private=True).count()

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(64))

    pic = db.Column(db.String(64))  
    pic1 = db.Column(db.String(64))  
    pic2 = db.Column(db.String(64))  
    pic3 = db.Column(db.String(64))  

    file1 = db.Column(db.String(64))  
    filename1 = db.Column(db.String(64))       
    file2 = db.Column(db.String(64))  
    filename2 = db.Column(db.String(64))       
    file3 = db.Column(db.String(64))  
    filename3 = db.Column(db.String(64))       
    file4 = db.Column(db.String(64))  
    filename4 = db.Column(db.String(64))       
    file5 = db.Column(db.String(64))  
    filename5 = db.Column(db.String(64))       

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    private = db.Column(db.Boolean, default=False)
    
    tag = db.Column(db.String(64))  

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    collectposts = db.relationship('CollectPost', backref='post', lazy='dynamic')
#    votes = db.relationship('Vote', backref='post', lazy='dynamic')


    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3','h4', 'p','br','u','del','tt','cite',
                        'font','big','small','strike','sup','sub','span','img','kdb']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'topic':self.topic,
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('帖子不能为空。')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    disabled = db.Column(db.Boolean)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    atmes = db.relationship('AtMe', backref='comment', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3','h4', 'p','br','u','del','tt','cite',
                        'font','big','small','strike','sup','sub','span','img','kdb']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('评论不能为空。')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Lesson(db.Model):
    __tablename__ = 'lessons'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(64))
    about_lesson = db.Column(db.Text())
    about_lesson_html = db.Column(db.Text)
    pic = db.Column(db.String(64))  
    file1 = db.Column(db.String(64))  
    file2 = db.Column(db.String(64))  
    file3 = db.Column(db.String(64))  
    file4 = db.Column(db.String(64))  
    file5 = db.Column(db.String(64))  
    file6 = db.Column(db.String(64))  
    file7 = db.Column(db.String(64))  
    file8 = db.Column(db.String(64))  
    filename1 = db.Column(db.String(64))  
    filename2 = db.Column(db.String(64))  
    filename3 = db.Column(db.String(64))  
    filename4 = db.Column(db.String(64))    
    filename5 = db.Column(db.String(64))    
    filename6 = db.Column(db.String(64))    
    filename7 = db.Column(db.String(64))    
    filename8 = db.Column(db.String(64))        
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    newlessons = db.relationship('NewLesson', backref='newlesson', lazy='dynamic')

    lessonfiles = db.relationship('LessonFile', backref='lessonfile', lazy='dynamic')


    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Lesson(about_lesson=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     teacher=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_about_lesson(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3','h4', 'p','br','u','del','tt','cite',
                        'font','big','small','strike','sup','sub','span','img','kdb']
        target.about_lesson_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'lesson_name':self.lesson_name,
            'about_lesson': self.about_lesson,
            'about_lesson_html': self.about_lesson_html,
            'timestamp': self.timestamp,
            'teacher': url_for('api.get_user', id=self.teacher_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        about_lesson = json_post.get('about_lesson')
        if about_lesson is None or about_lesson == '':
            raise ValidationError('帖子不能为空。')
        return Lesson(about_lesson=about_lesson)
    
    def count_newlesson(self):
        return NewLesson.query.filter_by(lesson_id=self.id).count()
    def count_file(self):
        return LessonFile.query.filter_by(lesson_id=self.id).count()
    def count_discussion(self):
        newlessons = NewLesson.query.filter_by(lesson_id=self.id).all()
        n = 0
        for nl in newlessons:
            n += Post.query.filter_by(tag="newlessons_" + str(nl.id)).count()
        return n
    def count_student(self):
        newlessons = NewLesson.query.filter_by(lesson_id=self.id).all()
        n = 0
        for nl in newlessons:
            n += Student.query.filter_by(newlesson_id=nl.id).count()
        return n


db.event.listen(Lesson.about_lesson, 'set', Lesson.on_changed_about_lesson)


class NewLesson(db.Model):
    __tablename__ = 'newlessons'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(4))
    season = db.Column(db.String(4))
    room_row = db.Column(db.Integer)
    room_column = db.Column(db.Integer)
    about = db.Column(db.String(64))  

#    start_date = 
#    end_date = 
#    weekday1 = 
#    start_hour1 = 
#    start_minute1 = 
#    end_hour1 = 
#    end_minute1 = 
#
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))

    students_id = db.relationship('Student', backref='students', lazy='dynamic')
    
    def count_student(self):
        return Student.query.filter_by(newlesson_id=self.id).count()
    def count_seat(self):
        return Student.query.filter_by(newlesson_id=self.id).count()-\
    Student.query.filter_by(newlesson_id=self.id).filter_by(seat=None).count()
    def count_discussion(self):
        return Post.query.filter_by(tag="newlessons_" + str(self.id)).count()
    def count_exercise(self):
        return Student.query.filter_by(newlesson_id=self.id).count()-\
    Student.query.filter_by(newlesson_id=self.id).filter_by(topic=None).count()



class LessonFile(db.Model):
    __tablename__ = 'lessonfiles'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    
    filetype = db.Column(db.String(8))
    visibility = db.Column(db.String(8))
    file = db.Column(db.String(64))
    filename = db.Column(db.String(64))  
    about = db.Column(db.String(128))  
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))


class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    seat = db.Column(db.String(4))
    absence = db.Column(db.Integer,default=0)
    confirm = db.Column(db.Boolean, default=False)

    topic = db.Column(db.String(64))  
    body = db.Column(db.Text())
    body_html = db.Column(db.Text())
    
    file1 = db.Column(db.String(64))  
    file2 = db.Column(db.String(64))  
    file3 = db.Column(db.String(64))  
    file4 = db.Column(db.String(64))  
    file5 = db.Column(db.String(64))   
    
    filename1 = db.Column(db.String(64))  
    filename2 = db.Column(db.String(64))  
    filename3 = db.Column(db.String(64))  
    filename4 = db.Column(db.String(64))  
    filename5 = db.Column(db.String(64))   
    
    criticism = db.Column(db.Text())
    criticism_html = db.Column(db.Text())
    score = db.Column(db.Integer)
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    newlesson_id = db.Column(db.Integer, db.ForeignKey('newlessons.id'))


    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Student(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     student=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_about_student(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3','h4', 'p','br','u','del','tt','cite',
                        'font','big','small','strike','sup','sub','span','img','kdb']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_student', id=self.id, _external=True),
            'score':self.score,
            'body': self.body,
            'body_html': self.body_html,
            'criticism': self.criticism,
            'critiism_html': self.criticism_html,
            'timestamp': self.timestamp,
            'student': url_for('api.get_user', id=self.student_id,
                              _external=True),
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('帖子不能为空。')
        return Student(body=body)
    
    

class Teacher(db.Model):
    __tablename__ = 'teachers'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(64))
    field = db.Column(db.String(64))  
    pic = db.Column(db.String(64))  
    about_teacher = db.Column(db.Text())
    about_teacher_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Teacher(about_teacher=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     teacher=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_about_teacher(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3','h4', 'p','br','u','del','tt','cite',
                        'font','big','small','strike','sup','sub','span','img','kdb']
        target.about_teacher_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'teacher_id':self.teacher_id,
            'about_teacher': self.about_teacher,
            'about_teacher_html': self.about_teacher_html,
            'timestamp': self.timestamp,
            'teacher': url_for('api.get_user', id=self.teacher_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        about_teacher = json_post.get('about_teacher')
        if about_teacher is None or about_teacher == '':
            raise ValidationError('帖子不能为空。')
        return Teacher(about_teacher=about_teacher)

    
    def count_lesson(self):
        return Lesson.query.filter_by(teacher_id=self.id).count()
    def count_file(self):
        lessons = Lesson.query.filter_by(teacher_id=self.id).all()
        n = 0
        if lessons is not None:
            for lesson in lessons:
                n += LessonFile.query.filter_by(lesson_id=lesson.id).count()
        return n
    def count_discussion(self):
        lessons = Lesson.query.filter_by(teacher_id=self.id).all()
        n = 0
        if lessons is not None:
            for lesson in lessons:
                newlessons = NewLesson.query.filter_by(lesson_id=lesson.id).all()
                for newlesson in newlessons:
                    n += Post.query.filter_by(tag="newlessons_"+str(newlesson.id)).count()
        return n
    def count_student(self):
        lessons = Lesson.query.filter_by(teacher_id=self.id).all()
        n = 0
        if lessons is not None:
            for lesson in lessons:
                newlessons = NewLesson.query.filter_by(lesson_id=lesson.id).all()
                for newlesson in newlessons:
                    n += Student.query.filter_by(newlesson_id=newlesson.id).count()
        return n

db.event.listen(Teacher.about_teacher, 'set', Teacher.on_changed_about_teacher)


class AtMe(db.Model):
    __tablename__ = 'atmes'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    username_whoatme = db.Column(db.String(64))
    username = db.Column(db.String, db.ForeignKey('users.username'))
    

class ClickTime(db.Model):
    __tablename__ = 'clicktimes'
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)

    user_comments_on_me = db.Column(db.DateTime)
    user_followed_by = db.Column(db.DateTime)
    user_show_my_atme = db.Column(db.DateTime)
    user_show_my_all_users = db.Column(db.DateTime)
    
    teacher_show_opened_lesson_discussion = db.Column(db.DateTime)
    teacher_show_opened_lesson_student = db.Column(db.DateTime)
    
    
    lesson_show_all_discussion = db.Column(db.DateTime)
    lesson_show_all_student = db.Column(db.DateTime)
    
    
    current_lesson_show_lesson_namelist = db.Column(db.DateTime)
    current_lesson_show_lesson_exercise = db.Column(db.DateTime)
    current_lesson_show_lesson_seat = db.Column(db.DateTime)
    current_lesson_show_lesson_discussion = db.Column(db.DateTime)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
