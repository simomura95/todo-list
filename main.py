import os
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import *
from datetime import datetime

# create flask app
app = Flask(__name__)
app.app_context().push()  # to avoid errors during runtime

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///to-do-list.db'  # db path and name. If not existing, is created with db.create_all()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # block warnings from sqlalchemy
db = SQLAlchemy(app)

Bootstrap(app)  # bootstrap on app

# flask login
app.config['SECRET_KEY'] = os.environ.get('FLASK_LOGIN_KEY')  # needed for flask login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=int(user_id))).scalar()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    lists = relationship("List", back_populates="user")


class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_in = db.Column(db.DateTime(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="lists")
    todo_items = relationship("Todo", back_populates="list")


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    date_in = db.Column(db.DateTime(100), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'))
    list = relationship("List", back_populates="todo_items")
# db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# lists in db for the current user. Includes a form to add a new list
@app.route("/lists", methods=["GET", "POST"])
@login_required
def lists():
    new_list_form = NewItemForm()
    if new_list_form.validate_on_submit():
        new_list = List(title=new_list_form.text.data, date_in=datetime.now(), user_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('lists'))
    # else:
    #     print(new_list_form.errors)
    all_lists = db.session.execute(db.select(List).filter_by(user_id=current_user.id).order_by(List.date_in.desc())).scalars().all()
    return render_template("lists.html", lists=all_lists, form=new_list_form)


# delete a list
@app.route("/delete-list/<int:list_id>")
@login_required
def delete_list(list_id):
    list_to_delete = db.session.execute(db.select(List).filter_by(id=list_id, user_id=current_user.id)).scalar()
    if list_to_delete:
        db.session.delete(list_to_delete)
        db.session.commit()
    else:
        return abort(404, "List not found for this user")
    return redirect(url_for('lists'))


@app.route("/list-<int:list_id>", methods=["GET", "POST"])
@login_required
def list_todos(list_id):
    if db.session.execute(db.select(List).filter_by(id=list_id)).scalar().user_id != current_user.id:
        return abort(403)
    new_todo_form = NewItemForm()
    if new_todo_form.validate_on_submit():
        new_todo = Todo(text=new_todo_form.text.data, done=False, date_in=datetime.now(), list_id=list_id)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('list_todos', list_id=list_id))
    # else:
    #     print(new_list_form.errors)
    all_todos = db.session.execute(db.select(Todo).filter_by(list_id=list_id).order_by(Todo.date_in.desc())).scalars().all()
    return render_template("list_todos.html", todos=all_todos, form=new_todo_form, list_id=list_id)


@app.route("/check-todo/<int:todo_id>")
@login_required
def check_todo(todo_id):
    todo_to_check = db.session.execute(db.select(Todo).filter_by(id=todo_id)).scalar()
    list_id = todo_to_check.list_id
    if db.session.execute(db.select(List).filter_by(id=list_id)).scalar().user_id != current_user.id:
        return abort(403)
    if todo_to_check:
        todo_to_check.done = not todo_to_check.done
        db.session.commit()
    else:
        return abort(404, "Item not found")
    return redirect(url_for('list_todos', list_id=list_id))


@app.route("/delete-todo/<int:todo_id>")
@login_required
def delete_todo(todo_id):
    todo_to_delete = db.session.execute(db.select(Todo).filter_by(id=todo_id)).scalar()
    list_id = todo_to_delete.list_id
    if db.session.execute(db.select(List).filter_by(id=list_id)).scalar().user_id != current_user.id:
        return abort(403)
    if todo_to_delete:
        db.session.delete(todo_to_delete)
        db.session.commit()
    else:
        return abort(404, "Item not found")
    return redirect(url_for('list_todos', list_id=list_id))


# register a new user, who must have a mail not already in use
# password is hashed and then saved in db, so that it is secure
@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        if db.session.execute(db.select(User).filter_by(email=register_form.email.data)).scalar():
            register_form.email.errors.append('Mail already in use')
            # flash("Mail already in use")
        else:
            new_user = User(
                email=register_form.email.data,  # ignore warning, it is correct
                password=generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8),  # encrypt password (via hashing)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('lists'))
    # print(register_form.errors)
    return render_template("register.html", form=register_form)


# login
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_login = db.session.execute(db.select(User).filter_by(email=login_form.email.data)).scalar()
        if not user_login:
            login_form.email.errors.append('Mail not registered')
        elif check_password_hash(pwhash=user_login.password, password=login_form.password.data):
            # password stored in db is decrypted and compared to the one given by the user
            login_user(user_login)
            return redirect(url_for('lists'))
        else:
            login_form.password.errors.append('Wrong Password')
    # print(login_form.errors)  # for debug
    return render_template("login.html", form=login_form)


# logout (only logged-in users, obviously)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
