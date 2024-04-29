from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import MySQLdb
import json
import bcrypt
import math


with open('config.json','r') as c:
    params = json.load(c)["params"]



local_server = True
app = Flask(__name__)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)
app.secret_key = 'super-secret-key'




class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subject = db.Column(db.String(120),nullable=False)
    message = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(120))

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    slug_post = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(120),nullable=False)
    date = db.Column(db.String(120))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    
    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        def _hash_password(self, password):
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

@app.route("/")
def home():
   
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)
@app.route('/about')
def about():
     
     return render_template('about.html', params=params)



@app.route('/post//<string:slug_post>', methods = ["GET"])
def post_route(slug_post):
    posts = Posts.query.filter_by(slug_post=slug_post).first()
    return render_template('post.html', params=params, posts=posts)

@app.route('/contact', methods = ["GET", "POST"])
def contact():
    if (request.method == "POST"):
        # Add entry to Database
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Add some users :::
        entry = Contact(name=name, email=email, subject=subject, message=message, date=datetime.now() )
        db.session.add(entry)
        db.session.commit()
        

    return render_template('contact.html', params=params)


@app.route('/edit/<string:sno>', methods = ["GET", "POST"])
def edit(sno):
    if request.method == "POST":
        box_title = request.form.get('title')
        tline = request.form.get('tagline')
        slug = request.form.get('slug_post')
        content = request.form.get('content')
        date = datetime.now()
        
        if sno == '0':
            posts = Posts(title=box_title, tagline=tline, slug_post=slug, content=content, date=date)
            db.session.add(posts)
            db.session.commit()
           
        else:
            posts = Posts.query.filter_by(sno=sno).first()
            posts.title = box_title
            posts.tagline = tline
            posts.slug_post = slug
            posts.content = content
            posts.date = date
            db.session.commit()
            return redirect('/edit/' + sno) 
        
    
    posts = Posts.query.filter_by(sno=sno).first()       
    return render_template('edit.html', params=params, posts=posts, sno=sno)

@app.route('/delete/<string:sno>', methods = ["GET", "POST"])
def delete(sno):
        posts = Posts.query.filter_by(sno=sno).first()
        db.session.delete(posts)
        db.session.commit()
        return redirect('/dashboard')
        



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')



    return render_template('register.html',params=params)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html', params=params)


@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        posts = Posts.query.all()
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html',user=user, params=params, posts=posts)
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')



if __name__ == "__main__":
    app.run(debug=True, port=5151) 