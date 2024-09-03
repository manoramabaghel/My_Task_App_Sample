from flask import Flask, request, render_template, redirect, url_for, session, flash
from models import init_db, add_user, get_user, add_task, get_tasks_with_filters, get_task_categories, get_reminders
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# @app.before_first_request
# def setup():
#     init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        user = get_user(session['username'])
        search_title = request.args.get('search', '')
        sort_by = request.args.get('sort', 'due_date')
        filter_category = request.args.get('category', '')
        tasks = get_tasks_with_filters(user['id'], search_title, sort_by, filter_category)
        task_count = len(tasks)  # Count the number of tasks
        categories = get_task_categories(user['id'])  # Assume a function to get task categories
        return render_template('home.html', tasks=tasks, task_count=task_count,
                               categories=categories, search_title=search_title,
                               sort_by=sort_by, filter_category=filter_category)
    return redirect(url_for('login'))

@app.route('/reminders')
def reminders():
    if 'username' in session:
        user = get_user(session['username'])
        reminders = get_reminders(user['id'])
        return render_template('reminders.html', reminders=reminders)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passcode = request.form['passcode']
        user = get_user(username)
        if user and check_password_hash(user['passcode'], passcode):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or passcode')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        passcode = request.form['passcode']
        if get_user(username):
            flash('Username already exists')
        else:
            hashed_passcode = generate_password_hash(passcode)
            add_user(username, hashed_passcode)
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_task', methods=['GET', 'POST'])
def add_task_route():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = get_user(session['username'])
    if request.method == 'POST':
        title = request.form['title']
        due_date = request.form['due_date']
        if title and due_date:
            add_task(user['id'], title, due_date)
            return redirect(url_for('home'))
        else:
            flash('Title and Due Date are required.')
    return render_template('add_task.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
