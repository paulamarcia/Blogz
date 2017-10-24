from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:marcia1@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'turtle123456'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))



    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog' ]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        login_error = ''
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            login_error = 'User password incorrect, or user does not exist'
            return render_template('login.html', login_error=login_error)

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    username_error = ''
    password_error = ''
    verify_error = ''
    existing_user_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
    
        if len(username) < 3 or len(username) > 20:
            username_error = 'Username must be between 3-20 charaters'

        if ' ' in username:
            username_error = 'Username cannot contain spaces'

        if len(password) < 3 or len(password) > 20:
            password_error = 'Password must be between 3-20 charaters'

        if ' ' in password:
            password_error = 'Password cannot contain spaces'

        
        if password != verify:
            verify_error = "Password and Verify Password don't match"

    
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            existing_user_error = 'Username already exists'
            return render_template('signup.html', existing_user_error=existing_user_error)

    return render_template('signup.html',
                           username_error=username_error,
                           password_error=password_error,
                           verify_error=verify_error,
                           )


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('index.html', title="Blog Posts by Author", blogs=blogs)



@app.route('/blog')
def display_blogs():
    owner_id = request.args.get('user')

    if (owner_id):
        
        blogs = Blog.query.filter_by(owner_id=owner_id)
        return render_template('index.html', title="Author's Posts", blogs=blogs)

    
    blog_id = request.args.get('id')

    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('entry.html', page_title="Blog Entry", blog=blog)

    sort_type = request.args.get('sort')
    if sort_type == "newest":
        blogs = Blog.query.order_by(Blog.created.desc()).all()
    else:
        blogs = Blog.query.all()

    return render_template('index.html', blogs=blogs)



@app.route('/newpost', methods=['POST', 'GET'] )
def add_post():
    if request.method == "GET":
        return render_template('new_blog_post.html')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        blog_title_error = ""
        blog_body_error = ""

        if title == "": 
            blog_title_error = 'Uh Oh! Your blog needs a title!'
        if body == "":
            blog_body_error = 'Uh Oh! There must be something you want to blog about!'

        if not blog_title_error and not blog_body_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog_post = Blog(title, body, owner)
            db.session.add(new_blog_post)
            db.session.commit()
            query_param_url = "/blog?id=" + str(new_blog_post.id)
            return redirect(query_param_url)
        else:
            return render_template('new_blog_post.html', blog_title_error=blog_title_error, 
                                                         blog_body_error=blog_body_error)


if __name__ == '__main__':
    app.run()

  

