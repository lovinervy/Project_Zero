from os import path
from flask import Flask, make_response, render_template, request, redirect, send_from_directory, url_for

from Translator import translator
import core

app = Flask(__name__)


app.config['OUTPUT_FOLDER'] = translator.OUTPUT_PATH


# Для того чтобы открыть доступ к директории outputs
@app.route(f'/{app.config["OUTPUT_FOLDER"]}/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    directory = path.join(app.root_path, app.config['OUTPUT_FOLDER'])
    return send_from_directory(path=filename, directory=directory)


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return make_response(render_template('index.html', error='Ошибка укажите url'))
        elif not core.valid_url(url):
            return make_response(render_template('index.html', error='Ошибка неверный url'))
        return redirect(url_for('configure', url=url))
    return render_template('index.html')


@app.route('/video_config', methods=('GET', 'POST'))
def configure():
    if request.method == 'POST':
        translate_to = request.form.get('tr_to')
        language = request.form.get('lang').lower()
        return redirect(url_for('video', tr_to=translate_to, lang=language))
    url = request.args.get('url')
    languages = ['Default']
    languages += translator.SUPPORTED_LANGUAGES
    response = make_response(render_template(
        'video_settings.html', languages=languages))
    response.set_cookie('url', url)
    return response


@app.route('/video')
def video():
    url = request.cookies.get('url')
    translate_to = request.args.get('tr_to')
    language = request.args.get('lang').lower()

    # Инициализируем класс помощник с требуемыми параметрами к видео
    helper = core.TranslateHelper(translate_to, url, language)
    # Формируем видео с требуемыми параметрами и возвращает путь на локальном диске
    video = helper.execute()
    return render_template('video.html', video=video)
