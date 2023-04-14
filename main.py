from telegram.ext import CommandHandler


with open('data/APIKEY.txt', encoding='utf-8') as f:
    APIKEY = f.read().rstrip('\n')
print(APIKEY)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!",
    )


# def open_():
#     app.run()


async def echo(update, context):
    await update.message.reply_text(f"Я получил сообщение {update.message.text}")


async def restart(update, context):
    """Вызывает /start при перезагрузке"""
    await start(update, context)


async def open(update, context):
    """Открывает ссылку"""
    # subprocess.call(['python', 'app.py'])
    # subprocess.Popen(args=["start", "python", 'app.py'], shell=True, stdout=subprocess.PIPE)
    await update.message.reply_text(f"http://127.0.0.1:8080/index")
    run_app()
    # Popen('python app.py')
    # open_()


def main():
    application = Application.builder().token(APIKEY).build()
    text = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(text)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler('restart', restart))
    application.add_handler(CommandHandler('open', open))
    # application.add_handler(CommandHandler("help", help_command))
    # application.add_handler(CommandHandler('time', time))
    # application.add_handler(CommandHandler('date', date))

    application.run_polling()


def run_app():
    app = flask.Flask(__name__)

    @app.route('/')
    def start():
        return 'Миссия Колонизация Марса'

    @app.route('/index')
    def index():
        return "И на Марсе будут яблони цвести!"

    if __name__ == '__main__':
        app.run(port=8080, host='127.0.0.1')
        print('started')



if __name__ == '__main__':
    main()
