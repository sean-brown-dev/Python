from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_word():
    return render_template('index.html')


@app.route('/blog')
def blog():
    return "Blog route"


@app.route('/blog/2020/dogs')
def dog_blog():
    return "The 2020 dog blog"
