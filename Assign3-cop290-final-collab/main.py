from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import math
from datetime import datetime
import os

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server=True

app = Flask(__name__)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

app.debug = True
db = SQLAlchemy(app)
app.secret_key = "cop290 assignment 3"
app.config['UPLOAD_FOLDER'] = params['upload_location']

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    subject  = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(11), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(10), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    images = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(20), nullable=False)
    likes = db.Column(db.Integer, nullable=True)

class Post_review(db.Model):
    CommentID = db.Column(db.Integer, primary_key=True)
    PostID =  db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(80), nullable=False)
    Review = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class User(db.Model):
    name = db.Column(db.String(80), nullable=False)
    USERID = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    PostUploaded = db.Column(db.String(80), nullable=False)
    ProfilePhoto = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Recipes(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    RecipeAuthor = db.Column(db.String(80), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    Slug = db.Column(db.String(80), nullable=False)
    Category = db.Column(db.String(20), nullable=True)
    Ingredients = db.Column(db.String(900), nullable=False)
    Instructions = db.Column(db.String(1200), nullable=False)
    Image = db.Column(db.String(80), nullable=False)
    Likes = db.Column(db.Integer, primary_key=True)
    Tagger =  db.Column(db.String(80), nullable=False)


@app.route('/')
def home():
    lat_post = Posts.query.filter_by().all()
    recipe =  Recipes.query.filter_by().all()
    return render_template("index.html" ,lat_post = lat_post , recipe = recipe,params = params)

@app.route('/homechef/all_posts')
def all_posts():
    all_posts = Posts.query.order_by(Posts.sno.desc()).all()
    last = math.ceil(len(all_posts)/int(params['no_of_posts']))
    #[0: params['no_of_posts']]
    #posts = posts[]
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page= int(page)
    all_posts = all_posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    #Pagination Logic
    #First
    if (page==1):
        prev = "#"
        next = "?page="+ str(page+1)
    elif(page==last):
        prev = "?page=" + str(page - 1)
        next = "#"
    else:
        prev = "?page=" + str(page - 1)
        next = "?page=" + str(page + 1)
    return render_template("all_posts.html", all_posts=all_posts, prev=prev, next=next,params=params)

@app.route('/about')
def about():
    return render_template("about.html", params=params)

@app.route('/contact', methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        entry = Contacts(name=name,email = email, subject= subject,  message = message, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html",params=params)

@app.route('/homechef')
def homechef():
    latest_posts = Posts.query.filter_by().all()
    top_users = User.query.filter_by().all()
    return render_template("homechef.html",params= params, latest_posts = latest_posts[:5], top_users = top_users[:6])

@app.route('/logout', methods = ['GET'])
def logout():
    session['logged_in'] = False
    params['path_of_img'] =""
    # redirecting to home page
    return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if (request.method=='GET'):
        return render_template("login.html")
    elif(request.method=='POST'):
        name = request.form.get('name')
        typ_pass = request.form.get('password')
        user_list = User.query.filter_by(name=name).first()
        # for exist_user in user_list:
        if check_password_hash(user_list.password, typ_pass ):
                flash('You have successfully logged in.', "success")
                session['logged_in'] = True
                session['email'] = user_list.email 
                session['username'] = user_list.name
                params['path_of_img'] = user_list.ProfilePhoto
                return redirect("/" )
        else:
            flash('Username or Password Incorrect', "Danger")
            return render_template("login.html")
        

@app.route('/pages_register', methods = ['GET', 'POST'])
def pages_register():
    if (request.method=='GET'):
        return render_template("pages-register.html")
    elif(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        PostUploaded = ""
        ProfilePhoto = "default.png"
        password = generate_password_hash(request.form.get('password'), method='sha256')
        entry = User(name=name,email = email,PostUploaded=PostUploaded,ProfilePhoto = ProfilePhoto, password = password)
        db.session.add(entry)
        db.session.commit()
        session['logged_in'] = True
        session['email'] = email 
        session['username'] = name
        params['path_of_img']= ProfilePhoto 
        flash('You have successfully registered', 'success')
        return redirect("/")

# img upload is still pending to be done
@app.route('/post_form', methods = ['GET', 'POST'])
def post_form():
    if(request.method=='POST'):
        author = request.form.get('author')
        email = request.form.get('email')
        title = request.form.get('title')
        content = request.form.get('content')
        f = request.files['images']
        if f.filename != '' :
            f.save(os.path.join(app.root_path,"static/img/foodimg/", secure_filename(f.filename)))
            images  = secure_filename(f.filename)
        else:
            flash('no image selected')
        slug = "food-post-"
        entry = Posts(author=author,email = email, title= title,  content = content, date= datetime.now(),slug = slug,images = images , likes=0)
        db.session.add(entry)
        db.session.commit()
    return render_template("post_form.html",params=params)

@app.route('/homechef/all_posts/post_details/<string:post_slug>', methods = ['GET', 'POST'])
def post_details(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    post_review = Post_review.query.filter_by(PostID = post.sno).all()
    usr = User.query.filter_by(name = post.author).first()
    if(request.method=='POST'):
        UserName = request.form.get('UserName')
        Review = request.form.get('Review')
        entry = Post_review(UserName = UserName, PostID = post.sno ,Review = Review, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template('post-details.html', params=params, post=post, post_review = post_review,usr=usr)



@app.route('/recipes/recipe_form', methods = ['GET', 'POST'] )
def recipe_form():
    if(request.method=='POST'):
        RecipeAuthor = request.form.get('RecipeAuthor')
        Category = request.form.get('Category')
        Title = request.form.get('Title')
        Ingredients = request.form.get('Ingredients')
        Instructions = request.form.get('Instructions')
        slug = "recipe-post-"
        tagger = "postedrec"
        f = request.files['images']
        if f.filename != '' :
            f.save(os.path.join(app.root_path,"static/img/foodimg/", secure_filename(f.filename)))
            images  = secure_filename(f.filename)
        else:
            flash('no image selected')
        entry = Recipes(RecipeAuthor=RecipeAuthor,Category = Category, Title= Title,  Ingredients = Ingredients,Instructions = Instructions, Date= datetime.now(), Slug = slug, Image = images, Likes=0,Tagger = tagger)
        db.session.add(entry)
        db.session.commit()
    return render_template("recipe_form.html",params=params)

@app.route('/recipes/recipe_details/<string:rec_slug>')
def recipe_details(rec_slug):
    recipe = Recipes.query.filter_by(Slug=rec_slug).first()
    auth = User.query.filter_by(name = recipe.RecipeAuthor).first()
    all_rec = Recipes.query.filter_by().all()
    return render_template("recipe-details.html",params=params,recipe=recipe,all_rec = all_rec,auth=auth)


@app.route('/recipes/search', methods = ['GET', 'POST'])
def search_recipe():
    search_term = request.form.get('searched')
    found_rec = Recipes.query.filter(Recipes.Title.like('%' + search_term + '%')).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)


@app.route('/recipes/categories/Breakfast', methods = ['GET', 'POST'])
def search_breakfast():
    search_term = "Breakfast"
    found_rec = Recipes.query.filter_by(Category = search_term).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)

@app.route('/recipes/categories/Lunch', methods = ['GET', 'POST'])
def search_lunch():
    search_term = "Lunch"
    found_rec = Recipes.query.filter_by(Category = search_term).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)
@app.route('/recipes/categories/Dinner', methods = ['GET', 'POST'])
def search_dinner():
    search_term = "Dinner"
    found_rec = Recipes.query.filter_by(Category = search_term).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)

@app.route('/recipes/categories/Appetizer', methods = ['GET', 'POST'])
def search_appetizert():
    search_term = "Appetizer"
    found_rec = Recipes.query.filter_by(Category = search_term).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)

@app.route('/recipes/categories/Soups', methods = ['GET', 'POST'])
def search_soups():
    search_term = "Soups"
    found_rec = Recipes.query.filter_by(Category = search_term).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)

@app.route('/recipes/categories/Desserts', methods = ['GET', 'POST'])
def search_desserts():
    search_term = "Desserts"
    found_rec = Recipes.query.filter_by(Category = search_term).all()
    # found_rec = found_rec.order_by(Recipes.Title).all()
    return render_template("recipes.html",all_rec = found_rec,params=params)

@app.route('/recipes')
def recipes():
    all_rec = Recipes.query.filter_by().all()
    last = math.ceil(len(all_rec)/int(params['no_of_rec']))
    #[0: params['no_of_posts']]
    #posts = posts[]
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page= int(page)
    all_rec = all_rec[(page-1)*int(params['no_of_rec']): (page-1)*int(params['no_of_rec'])+ int(params['no_of_rec'])]
    #Pagination Logic
    #First
    if (page==1):
        prev = "#"
        next = "?page="+ str(page+1)
    elif(page==last):
        prev = "?page=" + str(page - 1)
        next = "#"
    else:
        prev = "?page=" + str(page - 1)
        next = "?page=" + str(page + 1)
    return render_template("recipes.html", all_rec=all_rec, prev=prev, next=next,params=params)

@app.route('/shop')
def shop():
    return render_template("shop.html", params=params)
    
@app.route('/user_profile/<string:username>', methods = ['GET','POST'])
def profile(username):
    search_name = User.query.filter_by(name = username).first()
    if(request.method=='GET'):
        return render_template("user_profile.html",params = params,name=search_name)
    elif (request.method=='POST'):
        search_name.name= request.form.get('name')
        search_name.email = request.form.get('email')
        f = request.files['ProfilePhoto']
        if f.filename != '' :
            f.save(os.path.join(app.root_path,"static/img/user_images", secure_filename(f.filename)))
            search_name.ProfilePhoto  = secure_filename(f.filename)
        session['username'] = request.form.get('name')
        session['email'] = request.form.get('email')
        params['path_of_img'] = search_name.ProfilePhoto 
        db.session.commit()
        n_pass= request.form.get('newpassword')
        nr_pass = request.form.get('renewpassword')
        if (n_pass !="" and n_pass == nr_pass):
            search_name.password = generate_password_hash(request.form.get('newpassword'), method='sha256')
            db.session.commit()
        else:
            flash("Password don't match")
        return render_template("user_profile.html", params = params, name = search_name )


if __name__ == "__main__" :
    app.run(debug=True)