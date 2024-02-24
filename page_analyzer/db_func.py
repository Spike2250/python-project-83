import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect_to_db():
    return psycopg2.connect(DATABASE_URL)


def get_cursor(connection):
    return connection.cursor(cursor_factory=NamedTupleCursor)


# def select_from_db(select_query, many_values=False):
#     with connect_to_db() as conn:
#         with get_cursor(conn) as cursor:
#             cursor.execute(select_query)
#             if many_values:
#                 return cursor.fetchall()
#             else:
#                 return cursor.fetchone()


def find_url_by_id(id_):
    with connect_to_db() as conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT *
                FROM urls
                WHERE id = %s;"""
            cursor.execute(query, (id_, ))
            return cursor.fetchone()


def find_url_by_name(name):
    with connect_to_db() as conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT *
                FROM urls
                WHERE name = %s;"""
            cursor.execute(query, (name, ))
            return cursor.fetchone()


def find_checks(url_id):
    with connect_to_db() as conn:
        with get_cursor(conn) as cursor:
            query = """
                SELECT *
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;"""
            cursor.execute(query, (url_id, ))
            return cursor.fetchall()


def find_all_urls():
    with connect_to_db() as conn:
        with get_cursor(conn) as cursor:
            query = '''
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
                ORDER BY urls.id DESC;'''
            cursor.execute(query)
            return cursor.fetchall()
