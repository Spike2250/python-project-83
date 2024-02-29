import os
# from contextlib import contextmanager
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connect():
    return psycopg2.connect(DATABASE_URL)


def get_cursor(connection):
    return connection.cursor(cursor_factory=NamedTupleCursor)


def find_url_by_id(id_):
    conn = get_connect()
    with conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT *
                FROM urls
                WHERE id = %s;"""
            cursor.execute(query, (id_, ))
            url = cursor.fetchone()
    conn.close()
    return url


def find_url_by_name(name):
    conn = get_connect()
    with conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT *
                FROM urls
                WHERE name = %s;"""
            cursor.execute(query, (name, ))
            url = cursor.fetchone()
    conn.close()
    return url


def find_checks(url_id):
    conn = get_connect()
    with conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT *
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;"""
            cursor.execute(query, (url_id, ))
            check = cursor.fetchall()
    conn.close()
    return check


def find_all_urls():
    conn = get_connect()
    with conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT DISTINCT ON (urls.id)
                    urls.id AS id,
                    urls.name AS name,
                    url_checks.created_at AS last_check,
                    url_checks.status_code AS status_code
                FROM urls LEFT JOIN url_checks
                    ON urls.id = url_checks.url_id
                AND url_checks.id = (SELECT MAX(id)
                    FROM url_checks
                    WHERE url_id = urls.id)
                ORDER BY urls.id DESC;"""
            cursor.execute(query)
            urls = cursor.fetchall()
    conn.close()
    return urls


def insert_new_url(data):
    conn = get_connect()
    with conn:
        with get_cursor(conn) as cursor:
            query = """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id;"""
            cursor.execute(query=query, vars=data)
            url = cursor.fetchone()
    conn.close()
    return url


def insert_url_check(data):
    conn = get_connect()
    with conn:
        with get_cursor(conn) as cursor:
            query = """
                INSERT INTO url_checks (
                    url_id, status_code, h1,
                    title, description, created_at)\
                VALUES (%s, %s, %s, %s, %s, %s);"""
            cursor.execute(query=query, vars=data)
    conn.close()
