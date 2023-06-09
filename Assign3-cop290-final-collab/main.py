from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import math
from datetime import datetime
import os
import random
import requests
params = json.load(open('config.json', 'r'))["params"]

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

@app.route('/' ,methods = ['GET','POST'])
def home():
    lat_post = Posts.query.filter_by().all()
    recipe =  Recipes.query.filter_by().all()
    params['benefit_str']=""
    params['caution_str']=""
    if (request.method == 'GET'):
        params['benefit_str']=""
        params['caution_str']=""
        return render_template("index.html" ,lat_post = lat_post , recipe = recipe,params = params)
    elif (request.method=='POST'):
        params['benefit_str']=""
        params['caution_str']=""
        rec_name = request.form.get('name')
        url = "https://edamam-recipe-search.p.rapidapi.com/search"
        querystring = {"q": rec_name}

        headers = {
            "content-type": "application/octet-stream",
            "X-RapidAPI-Key": "04384185a2msha8801dfad644f63p15e50ajsnb860fe374bb6",
            "X-RapidAPI-Host": "edamam-recipe-search.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        benifits= response.json()['hits'][0]['recipe']['healthLabels']
        l=len(benifits)
        for i in range(l):
            params['benefit_str']=params['benefit_str']+" "+ benifits[i]
            
        caution= response.json()['hits'][0]['recipe']['cautions']
        l=len(caution)

        for i in range(l):
            params['caution_str']=params['caution_str']+" "+ caution[i]
        return render_template("index.html" ,lat_post = lat_post , recipe = recipe,params = params)

@app.route('/about', methods = ['GET','POST'])
def benefit():
        return render_template("about.html", params=params)
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
        flash('You have successfully registered')
        return redirect("/")

# img upload is still pending to be done
@app.route('/post_form', methods = ['GET', 'POST'])
def post_form():
    if(request.method=='POST'):
        author = session['username']
        email = request.form.get('email')
        title = request.form.get('title')
        content = request.form.get('content')
        f = request.files['images']
        if f.filename != '' :
            f.save(os.path.join(app.root_path,"static/img/foodimg/", secure_filename(f.filename)))
            images  = secure_filename(f.filename)
        else:
            flash('no image selected')
        slug = "food-post-" + str(random.randint(100,200000))
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
        if 'comment_btn' in request.form :
            UserName = request.form.get('UserName')
            Review = request.form.get('Review')
            entry = Post_review(UserName = UserName, PostID = post.sno ,Review = Review, date= datetime.now())
            db.session.add(entry)
            db.session.commit()
        elif 'like_btn' in request.form :
            post.likes = post.likes+ 1
            db.session.commit()
    return render_template("post-details.html",params=params, post=post, post_review = post_review,usr=usr)


@app.route('/recipes/recipe_form', methods = ['GET', 'POST'] )
def recipe_form():
    if(request.method=='POST'):
        all_rec = Recipes.query.filter_by().all()
        RecipeAuthor =  session['username']
        Category = request.form.get('Category')
        Title = request.form.get('Title')
        Ingredients = request.form.get('Ingredients')
        Instructions = request.form.get('Instructions')
        slug = "recipe-post-" + str(random.randint(100,200000))
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
        recipe = Recipes.query.filter_by(Slug=slug).first()
        return render_template("recipe-details.html",params=params,recipe=recipe,all_rec = all_rec,auth=RecipeAuthor)
    else:
        return render_template("recipe_form.html",params=params)

@app.route('/recipes/recipe_details/<string:rec_slug>')
def recipe_details(rec_slug):
    recipe = Recipes.query.filter_by(Slug=rec_slug).first()
    auth = User.query.filter_by(name = recipe.RecipeAuthor).first()
    all_rec = Recipes.query.filter_by().all()
    return render_template("recipe-details.html",params=params,recipe=recipe,all_rec = all_rec,auth=auth)
    

    
       
@app.route('/recipes/recipe_details/<string:rec_slug>', methods = ['GET', 'POST'])
def recipe_convertor(rec_slug):
    recipe = Recipes.query.filter_by(Slug=rec_slug).first()

    url = "https://microsoft-translator-text.p.rapidapi.com/translate"

    querystring = {"to[0]":"hi","api-version":"3.0","profanityAction":"NoAction","textType":"plain"}

    payload1 = [{ "Text": recipe.Instructions }]
    payload2 = [{ "Text": recipe.Ingredients }]
    payload3 = [{ "Text": recipe.Title }]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "04384185a2msha8801dfad644f63p15e50ajsnb860fe374bb6",
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
    }

    response1 = requests.post(url, json=payload1, headers=headers, params=querystring)
    response2 = requests.post(url, json=payload2, headers=headers, params=querystring)
    response3 = requests.post(url, json=payload3, headers=headers, params=querystring)

    if (request.method =='POST'):
        if('Convertor' in request.form) :
            recipe.Instructions = response1.json()[0]['translations'][0]['text']
            recipe.Ingredients = response2.json()[0]['translations'][0]['text']
            recipe.Title = response3.json()[0]['translations'][0]['text']
    all_rec = Recipes.query.filter_by().all()
    auth = User.query.filter_by(name = recipe.RecipeAuthor).first()
            
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
    recipe_posted = Recipes.query.filter_by(RecipeAuthor = username).all()
    post_posted = Posts.query.filter_by(author = username).all()
    if(request.method=='GET'):
        return render_template("user_profile.html",params = params,name=search_name,recipe_posted=recipe_posted,post_posted=post_posted )
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
        return render_template("user_profile.html", params = params, name = search_name ,recipe_posted=recipe_posted,post_posted=post_posted )


if __name__ == "__main__" :
    app.run(debug=True, host ="10.17.50.5")
