from flask import render_template, url_for, flash, redirect
from blogs import app
from blogs.forms import RegistrationForm, LoginForm
from blogs.models import User, Post


# posts = [
#     {
#         'author': 'Ashish Yadav',
#         'title': 'Blog Post 1',
#         'content': 'First blog content',
#         'date_posted': 'Augest 20, 2024'
#     },
#     {
#         'author': 'Aswan',
#         'title': 'Blog Post 2',
#         'content': 'First blog content',
#         'date_posted': 'Augest 22, 2024'
#     }
# ]


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts = posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}...", 'success')
        return redirect(url_for("home"))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Successfully loged in...", 'success')
        return redirect(url_for("home"))
    return render_template('login.html', form=form)
