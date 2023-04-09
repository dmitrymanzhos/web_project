#!flask/bin/python
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from tech import db_session, users

app = Flask(__name__, template_folder='templates')
# login_manager = LoginManager()
# login_manager.init_app(app)
app.secret_key = 'secret_key'


@app.route('/')
def home_page():
    return render_template('index.html', name='abanon')


@app.route('/reg')
def reg():
    return render_template()


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
