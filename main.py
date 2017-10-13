from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:marcia1@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body
        

@app.route('/blog')
def display_blogs():
    

    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('entry.html', page_title="Blog Entry", blog=blog)

    else:
        blogs = Blog.query.all()

        return render_template('blog.html', blogs=blogs)



@app.route('/newpost', methods=['POST', 'GET'])
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
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            query_param_url = "/blog?id=" + str(new_blog.id)
            return redirect(query_param_url)
        else:
            return render_template('new_blog_post.html', blog_title_error=blog_title_error, 
                                                         blog_body_error=blog_body_error)


if __name__ == '__main__':
    app.run()



