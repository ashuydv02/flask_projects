from flask import render_template, url_for, flash, redirect, request
from blogs import app, db, bcrypt
from blogs.forms import RegistrationForm, LoginForm, PostForm
from blogs.models import User, Post
from bcrypt import *
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc, or_


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(desc(Post.date_posted)).paginate(page=page, per_page=3)
    return render_template('home.html', posts = posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(
            f'''Your Account has been created for {form.username.data}
            Now you can login with your email and password...''',
            'success'
        )
        return redirect(url_for("login"))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Successfully loged in...", 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:   
            flash("Login Unsuccessfull. Please check email and password", 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("Successfully loged out...", 'success')
    return redirect(url_for("home"))


@app.route('/account')
@login_required
def account():
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', image_file=image_file)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Your Post has been successfully created...", "success")
        return redirect(url_for("home"))
    return render_template('create_post.html', form=form, legend='Create Post')


@app.route('/search')
def search():
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    posts = Post.query.join(User).filter(
            or_(
                Post.title.ilike(f'%{query}%'),
                Post.content.ilike(f'%{query}%'),
                User.username.ilike(f'%{query}%')
            )
        ).order_by(desc(Post.date_posted)).paginate(page=page, per_page=3)
    return render_template('search_posts.html', posts=posts, query=query)


@app.route('/post/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Post.query.get(id)
    if not post:
        flash("No Post found...", 'danger')
        return redirect(url_for("account"))
    if post.author != current_user:
        flash("Not Authorized to access this content...", 'danger')
        return redirect(url_for("account"))

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data 
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for("account"))
    else:
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', form=form, legend='Update Post')


@app.route('/post/<int:id>/delete', methods=['GET'])
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if not post:
        flash("No Post found...", 'danger')
        return redirect(url_for("account"))
    if post.author != current_user:
        flash("Not Authorized to access this content...", 'danger')
        return redirect(url_for("account"))
    
    db.session.delete(post)
    db.session.commit()
    flash("Your Post has been deleted successfully...", "success")
    return redirect(url_for("account"))


@app.route('/user_posts/<string:username>')
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(desc(Post.date_posted)).paginate(page=page, per_page=3)
    if current_user.is_authenticated:
        if current_user == user:
            return redirect(url_for('account'))
    return render_template('user_posts.html', user=user, posts=posts)


@app.errorhandler(404)
def error_404(error):
    return render_template('404_error.html'), 404


@app.errorhandler(500)
def error_404(error):
    return render_template('500_error.html'), 500
