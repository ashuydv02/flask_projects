from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>First Project</h1>"

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return "<b>About Page</b>"


if __name__ == "__main__":
    app.run(debug=True)