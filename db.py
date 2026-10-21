import os
import pymysql
import pymysql.cursors
from flask import g
from config import Config

def get_db_connection(include_db=True):
    """
    Establish a connection to the MySQL database.
    Returns a PyMySQL connection with dictionary cursor.
    """
    params = Config.get_db_params(include_db=include_db)
    return pymysql.connect(
        host=params['host'],
        port=params['port'],
        user=params['user'],
        password=params['password'],
        database=params.get('database'),
        charset=params['charset'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

def get_db():
    """
    Get or create a database connection for the current Flask request context.
    """
    if 'db' not in g:
        g.db = get_db_connection(include_db=True)
    return g.db

def close_db(e=None):
    """
    Close the database connection at the end of the Flask request.
    """
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def init_db():
    """
    Initialize the database using schema.sql.
    Creates database and tables if they don't exist.
    """
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

    # First connect without specifying database to create it safely
    conn = get_db_connection(include_db=False)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
    finally:
        conn.close()

    # Now connect to the new database and execute schema statements
    conn = get_db_connection(include_db=True)
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Clean out line-level SQL comments
        cleaned_lines = [line for line in sql_script.splitlines() if not line.strip().startswith('--')]
        cleaned_script = '\n'.join(cleaned_lines)

        statements = [stmt.strip() for stmt in cleaned_script.split(';') if stmt.strip()]
        with conn.cursor() as cursor:
            for statement in statements:
                if statement.upper().startswith('USE ') or statement.upper().startswith('CREATE DATABASE'):
                    continue
                cursor.execute(statement)
        conn.commit()
        print(f"Database '{Config.DB_NAME}' initialized successfully.")
    finally:
        conn.close()

def check_db_connection():
    """
    Check if MySQL server is reachable and credentials are valid.
    Returns (True, "OK") or (False, error_message).
    """
    try:
        conn = get_db_connection(include_db=False)
        conn.close()
        return True, "Successfully connected to MySQL Server."
    except pymysql.MySQLError as e:
        return False, str(e)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        try:
            print(f"Connecting to MySQL on {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")
            init_db()
            print("Schema initialized successfully!")
        except Exception as ex:
            print(f"Error initializing database: {ex}")
    else:
        success, msg = check_db_connection()
        print(f"DB Connection Check: {'SUCCESS' if success else 'FAILED'}")
        print(f"Details: {msg}")
