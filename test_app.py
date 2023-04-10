#!flask/bin/python
from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager, login_user, login_required
from tech import db_session, users
from forms.user_form import RegisterForm, EnterForm

app = Flask(__name__, template_folder='templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(users.User).get(user_id)


@app.route('/')
def home_page():
    return render_template('index.html', name='abanon')


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegisterForm()
    print(1)
    if form.validate_on_submit():
        print(2)
        if not type(form.age.data) == int:
            return render_template('register_form.html', form=form,
                                   message='Неверно указан возраст')
        elif form.age.data not in range(0, 100):
            return render_template('register_form.html', form=form,
                                   message='Неверно указан возраст')
        db_sess = db_session.create_session()
        if db_sess.query(users.User).filter(users.User.nicname == form.nicname.data).first():
            return render_template('register_form.html', form=form,
                                   message='Пользователь с таким никнеймом уже существует')
        elif db_sess.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register_form.html', form=form,
                                   message='Пользователь с такой почтой уже существует')
        else:
            user = users.User(
                nicname=form.nicname.data, email=form.email.data, age=form.age.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()

            return redirect('/enter')
    return render_template('register_form.html', form=form)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/enter', methods=['GET', 'POST'])
def enter():
    form = EnterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(users.User).filter(users.User.nicname == form.nicname.data).first():
            return render_template('enter_form.html', form=form, message='Такой пользователь не зарегистрирован')
        user = db_sess.query(users.User).filter(users.User.nicname == form.nicname.data).first()
        if user.check_password(form.password.data):
            login_user(user)
            return redirect('/success')
        else:
            return render_template('enter_form.html', form=form, message='Неверный пароль')
    return render_template('enter_form.html', form=form)


@app.route('/secret')
def secret():
    pass


if __name__ == '__main__':
    db_session.global_init('db/all.db')
    app.run(port=8080, host='127.0.0.1')
