# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
#
# db = SQLAlchemy()
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     hashed_passcode = db.Column(db.String(120), nullable=False)
#
#     def set_password(self, passcode):
#         self.hashed_passcode = generate_password_hash(passcode)
#
#     def check_password(self, passcode):
#         return check_password_hash(self.hashed_passcode, passcode)
#
import sqlite3

DATABASE = 'tasks_app.db'

def get_db():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        return (f"An error occurred: {e}")

def init_db():
    try:
        with get_db() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    passcode TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    category TEXT,
                    reminder_date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
    except Exception as e:
        return (f"An error occurred: {e}")

def add_user(username, passcode):
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO users (username, passcode) VALUES (?, ?)', (username, passcode))
            conn.commit()
    except Exception as e:
        return (f"An error occurred: {e}")

def get_user(username):
    try:
        with get_db() as conn:
            return conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    except Exception as e:
        return (f"An error occurred: {e}")

def add_task(user_id, title, due_date,category='', reminder_date=''):
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO tasks (user_id, title, due_date, category, reminder_date) VALUES (?, ?, ?, ?, ?)', (user_id, title, due_date, category, reminder_date))
            conn.commit()
    except Exception as e:
        return (f"An error occurred: {e}")

# def get_tasks(user_id):
#     with get_db() as conn:
#         return conn.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchall()
def get_tasks_with_filters(user_id, search_title='', sort_by='due_date', filter_category=''):
    try:
        with get_db() as conn:
            query = "SELECT title, due_date FROM tasks WHERE user_id = ?"
            params = [user_id]
            if search_title:
                query += " AND title LIKE ?"
                params.append(f'%{search_title}%')

            if filter_category:
                query += " AND category = ?"
                params.append(filter_category)

            query += f" ORDER BY {sort_by}"

            return conn.execute(query, params).fetchall()
    except Exception as e:
        return (f"An error occurred: {e}")

def get_task_categories(user_id):
    try:
        with get_db() as conn:
            query = "SELECT DISTINCT category FROM tasks WHERE user_id = ?"
            conn_obj = conn.execute(query, (user_id,))
            categories = [row[0] for row in conn_obj.fetchall()]
            return categories
    except Exception as e:
        return (f"An error occurred: {e}")

def get_reminders(user_id):
    try:
        with get_db() as conn:
            query = "SELECT title, due_date, reminder_date FROM tasks WHERE user_id = ? AND reminder_date IS NOT NULL"
            reminders = conn.execute(query, (user_id,)).fetchall()
            return reminders
    except Exception as e:
        return (f"An error occurred: {e}")
