from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap5
from forms import RegisterForm, LoginForm, TodoForm, EditTodoForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_ckeditor import CKEditor
import secrets
import os
from datetime import datetime
from models import db, Todo, User

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)  # Raises a 403 Forbidden error
        elif current_user.get_id() != '1':
            abort(403)  # Raises a 403 Forbidden error
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/user_home', methods=['GET', 'POST'])
@login_required
def user_home():
    todos = current_user.todos
    return render_template('user_home.html', todos=todos)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password=hashed_pw
        )
        existing_user = User.query.filter_by(email=new_user.email).first()
        if existing_user:
            # If user exists, flash a message and redirect to login page
            flash('You have already registered with that email address. Please login instead.', 'danger')
            return redirect(url_for('login'))

        # If no existing user, add and commit the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            print(f"Logged in User: {user}, ID: {user.id}")
            return redirect(url_for('user_home'))

        flash('Login failed. Please check your email and password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        new_todo = Todo(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            completed=form.completed.data,
            user_id=current_user.id
        )
        db.session.add(new_todo)
        db.session.commit()
        flash('Todo added!', 'success')
        return redirect(url_for('user_home'))
    return render_template('add_todo.html', form=form)


@app.route('/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted!', 'success')
    return redirect(url_for('user_home'))


@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    if todo.user_id != current_user.id:
        abort(403) # Forbidden if the task does not belong to the current user

    form = EditTodoForm(obj=todo)
    if form.validate_on_submit():
        # Updates the task with form data
        todo.title = form.title.data
        todo.description = form.description.data
        todo.due_date = form.due_date.data
        todo.completed = form.completed.data
        db.session.commit()
        flash('Task has been updated!', 'success')
        return redirect(url_for('user_home'))

    return render_template('edit.html', form=form, todo=todo)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
