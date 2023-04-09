#!flask/bin/python
from flask import Flask, render_template, redirect, jsonify
from flask_login import LoginManager
from tech import db_session, users
from forms.user_form import RegisterForm, EnterForm

app = Flask(__name__, template_folder='templates')
# login_manager = LoginManager()
# login_manager.init_app(app)
app.secret_key = 'secret_key'


@app.route('/')
def home_page():
    return render_template('index.html', name='abanon')


@app.route('/reg')
def reg():
    form = RegisterForm()
    if form.validate_on_submit():
        # обращение к бд
        return redirect('/')
        pass
    return render_template('register_form.html', form=form)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
