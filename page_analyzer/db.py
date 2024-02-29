import os
from contextlib import contextmanager
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor

load_dotenv()


@contextmanager
def connection():
    database_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(database_url)
    try:
        yield conn
    finally:
        conn.close()


def get_cursor(connection):
    return connection.cursor(cursor_factory=NamedTupleCursor)


def find_url_by_id(id_):
    with connection() as conn, get_cursor(conn) as cursor:
        query = """
            SELECT *
            FROM urls
            WHERE id = %s;"""
        cursor.execute(query, (id_, ))
        return cursor.fetchone()


def find_url_by_name(name):
    with connection() as conn, get_cursor(conn) as cursor:
        query = """
            SELECT *
            FROM urls
            WHERE name = %s;"""
        cursor.execute(query, (name, ))
        return cursor.fetchone()


def find_checks(url_id):
    with connection() as conn, get_cursor(conn) as cursor:
        query = """
            SELECT *
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC;"""
        cursor.execute(query, (url_id, ))
        return cursor.fetchall()


def find_all_urls():
    with connection() as conn, get_cursor(conn) as cursor:
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
        return cursor.fetchall()


def insert_new_url(data):
    with connection() as conn, get_cursor(conn) as cursor:
        query = """
            INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id;"""
        cursor.execute(query=query, vars=data)
        return cursor.fetchone()


def insert_url_check(data):
    with connection() as conn, get_cursor(conn) as cursor:
        query = """
            INSERT INTO url_checks (
                url_id, status_code, h1,
                title, description, created_at)\
            VALUES (%s, %s, %s, %s, %s, %s);"""
        cursor.execute(query=query, vars=data)
