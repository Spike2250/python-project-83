from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        messages=messages,
    )
