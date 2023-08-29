import mariadb
from flask import g 
def connect_db():
    try:
        conn = mariadb.connect(
            host='127.0.0.1',
            port=3306,
            user="appuser",
            password='1234!@#$',
            database='food'
        )
        conn.autocommit = True
        return conn

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")

def get_db():
    if not hasattr(g, 'mariadb_db'):
        g.mariadb_db = connect_db()
    return g.mariadb_db
