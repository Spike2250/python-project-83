import os
from datetime import datetime

from flask import (
    Flask, flash, redirect,
    render_template, request, url_for)
from dotenv import load_dotenv
import requests
import psycopg2
from bs4 import BeautifulSoup

from .db import (
    insert_new_url, insert_url_check,
    find_url_by_id, find_url_by_name,
    find_all_urls, find_checks)
from .parsing import get_seo_data
import page_analyzer.url


load_dotenv()
SECRET = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def urls_post():
    url_from_request = request.form.to_dict().get('url', '')
    errors = page_analyzer.url.validate(url_from_request)

    if 'Not valid url' in errors:
        flash('Некорректный URL', 'alert-danger')
        if 'No url' in errors:
            flash('URL обязателен', 'alert-danger')
        return render_template('index.html'), 422

    new_url = page_analyzer.url.normalize(url_from_request)

    data = (new_url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        url_id = insert_new_url(data).id
        flash('Страница успешно добавлена', 'alert-success')
    except psycopg2.errors.UniqueViolation:
        url_id = find_url_by_name(new_url).id
        flash('Страница уже существует', 'alert-warning')

    return redirect(url_for('one_url', id_=url_id))


@app.route('/urls', methods=['GET'])
def urls():
    urls = find_all_urls()
    return render_template('all_urls.html', urls=urls)


@app.route('/urls/<int:id_>', methods=['GET'])
def one_url(id_):
    url = find_url_by_id(id_)
    if url is None:
        flash('Такой страницы не существует', 'alert-warning')
        return redirect(url_for('index'))

    return render_template('show.html', ID=id_, name=url.name,
                           created_at=url.created_at,
                           checks=find_checks(id_))


@app.route('/urls/<int:id_>/checks', methods=['POST'])
def check_url(id_):
    url = find_url_by_id(id_)
    try:
        with requests.get(url.name) as response:
            status_code = response.status_code
            response.raise_for_status()

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return render_template('show.html', ID=id_, name=url.name,
                               created_at=url.created_at,
                               checks=find_checks(id_)), 422

    h1, title, description = get_seo_data(
        BeautifulSoup(response.text, 'html.parser')
    )

    data = (id_, status_code, h1, title, description,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    insert_url_check(data)
    flash('Страница успешно проверена', 'alert-success')

    return redirect(url_for('one_url', id_=id_))


@app.errorhandler(psycopg2.OperationalError)
def special_exception_handler(error):
    return render_template('error.html'), 500
