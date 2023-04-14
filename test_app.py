import os
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, redirect, request, flash, url_for, send_from_directory
from flask_login import LoginManager, login_user, current_user
from werkzeug.utils import secure_filename

from forms.user_form import RegisterForm, EnterForm
# from forms.images_form import UploadForm, photos
from tech import db_session, users, images

UPLOAD_FOLDER = os.path.abspath('data')
app = Flask(__name__, template_folder='templates')
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(users.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def home_page():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        imgs = db_sess.query(images.Image).filter(images.Image.user == current_user)
        return render_template('all_images.html', images=imgs)
    return render_template('get_in_or_reg.html', name=current_user, title="Outgramm5")


@app.route('/registration', methods=['GET', 'POST'])
def reg():
    form = RegisterForm()
    print(1)
    if form.validate_on_submit():
        print(2)
        if not type(form.age.data) == int:
            return render_template('register_form.html', form=form, title='Регистрация',
                                   message='Неверно указан возраст')
        elif form.age.data not in range(0, 100):
            return render_template('register_form.html', form=form, title='Регистрация',
                                   message='Неверно указан возраст')
        db_sess = db_session.create_session()
        if db_sess.query(users.User).filter(users.User.nicname == form.nicname.data).first():
            return render_template('register_form.html', form=form, title='Регистрация',
                                   message='Пользователь с таким никнеймом уже существует')
        elif db_sess.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register_form.html', form=form, title='Регистрация',
                                   message='Пользователь с такой почтой уже существует')
        else:
            user = users.User(
                nicname=form.nicname.data, email=form.email.data, age=form.age.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()

            return redirect('/enter')
    return render_template('register_form.html', form=form, title='Регистрация')


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
            return render_template('enter_form.html', form=form, message='Такой пользователь не зарегистрирован',
                                   title='Вход')
        user = db_sess.query(users.User).filter(users.User.nicname == form.nicname.data).first()
        if user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect('/success')
        else:
            return render_template('enter_form.html', form=form, message='Неверный пароль', title='Вход')
    return render_template('enter_form.html', form=form, title='Вход')


@app.route('/secret')
def secret():
    pass


@app.route('/add_image', methods=['GET', 'POST'])
def add_image():
    # form = UploadForm()
    # if form.validate_on_submit():
    #     filename = photos.save(form.photo.data)
    #     file_url = photos.url(filename)
    # else:
    #     file_url = None
    # return render_template('add_image.html', form=form, file_url=file_url)

    # if request.method == 'POST':
    #     form = cgi.FieldStorage()
    #     fileitem = form.getfirst('filename')
    #     print(fileitem)
    #     if fileitem.filename:
    #         fn = os.path.basename(fileitem.filename)
    #
    #         # open read and write the file into the server
    #         open(fn, 'wb').write(fileitem.file.read())
    #         return redirect('/success')

    if request.method == 'POST':
        print('.')
        if 'f' not in request.files:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            flash('Не могу прочитать файл')
            return redirect(request.url)
        print(1)
        print(current_user)
        file = request.files['f']
        # private = request.files['private']
        print(type(file))
        # Если файл не выбран, то браузер может
        # отправить пустой файл без имени.
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file:
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join('static/img/' + filename))
            db_sess = db_session.create_session()
            image = images.Image()
            print('?')
            image.filepath = os.path.join("/static/img/", filename)
            print('!')
            current_user.images.append(image)
            print(11)
            db_sess.merge(current_user)
            print(12)
            db_sess.commit()
            # если все прошло успешно, то перенаправляем
            # на функцию-представление `download_file`
            # для скачивания файла
            return redirect('/success')
            # return redirect(url_for('download_file', name=filename))

    return render_template('add_image.html', title="Add image")


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == '__main__':
    db_session.global_init('db/all.db')
    app.run(port=8080, host='127.0.0.1')
