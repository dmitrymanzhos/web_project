import os
from flask import Flask, render_template, redirect, request, flash, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.utils import secure_filename

from forms.user_form import RegisterForm, EnterForm
from tech import db_session, users, images

UPLOAD_FOLDER = os.path.abspath('static')
app = Flask(__name__, template_folder='templates')  # инициализация
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@login_manager.user_loader
def load_user(user_id):  # загрузка пользователя по id
    db_sess = db_session.create_session()
    return db_sess.query(users.User).get(user_id)


@app.route('/logout')
@login_required
def logout():  # выход из профиля
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def home_page():  # главная страница
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        imgs = db_sess.query(images.Image)
        return render_template('all_images.html', images=imgs, title="Главная")
    return render_template('get_in_or_reg.html', name=current_user, title="Главная")  # если пользователь не зарег.


@app.route('/profile')
@login_required
def profile():  # страница профиля
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        imgs = db_sess.query(images.Image).filter(images.Image.user == current_user)
        return render_template('profile.html', images=imgs, user=current_user, title="Профиль")


@app.route('/info')
def info():  # о приложении
    return render_template('info.html', title="О приложении")


@app.route('/registration', methods=['GET', 'POST'])
def reg():  # регистрация
    form = RegisterForm()
    if form.validate_on_submit():   # при нажатии
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
            return redirect('/')
        else:
            return render_template('enter_form.html', form=form, message='Неверный пароль', title='Вход')
    return render_template('enter_form.html', form=form, title='Вход')


@app.route('/add_image', methods=['GET', 'POST'])
@login_required
def add_image():  # добавление изображения
    if request.method == 'POST':
        print('.')
        if 'f' not in request.files:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['f']
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
            image.filepath = os.path.join("/static/img/", filename)
            current_user.images.append(image)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/profile')
    return render_template('add_image.html', title="Добавление фото")


@app.route('/image_delete/<int:img_id>', methods=['GET', 'POST'])
@login_required
def image_delete(img_id):  # удаление фото
    db_sess = db_session.create_session()
    image = db_sess.query(images.Image).filter(images.Image.id == img_id, images.Image.user == current_user).first()
    if image:
        if os.path.isfile(image.filepath[1:]):
            os.remove(image.filepath[1:])
            db_sess.delete(image)
            db_sess.commit()
    else:
        abort(404)
    return redirect('/profile')


if __name__ == '__main__':
    db_session.global_init('db/all.db')
    app.run(port=8080, host='127.0.0.1')
