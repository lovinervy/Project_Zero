from os import path
from flask import Flask, make_response, render_template, request, redirect, send_from_directory, url_for

from Translator import translator
import core
from Translator.custom_typing import PathToFile

app = Flask(__name__)
control = core.ControlDatabase()


app.config['OUTPUT_FOLDER'] = translator.OUTPUT_PATH


# Get files from output folder
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
        elif not control.valid_url(url):
            return make_response(render_template('index.html', error='Ошибка неверный url'))
        return redirect(url_for('configure', url=url))
    return render_template('index.html')


@app.route('/video_config', methods=('GET', 'POST'))
def configure():
    if request.form.get('tr_to'):
        url = request.cookies.get('url')
        translate_to = request.form.get('tr_to')
        language = request.form.get('lang').lower()
        video_data = control.have_video(url)
        audio_data = control.have_translate_voice(url, 'default')

        if video_data and audio_data:
            video_path = video_data[2]
            audio_path = audio_data[2]
            content_path = PathToFile(video=video_path, audio=audio_path)
        else:
            content_path = translator.download_yt_content(url)
            control.add_video(url, content_path.video)
            control.add_voiceover(url, 'default', content_path.audio)

        if translate_to == 'Voice' and language != 'default':
            has_audio = control.have_translate_voice(url, language)
            if not has_audio:
                has_subs = control.have_translate_subs(url, language)
                if not has_subs:
                    subs_path = core.get_subs_from_youtube(url, language)
                    control.add_subtitles(url, language, subs_path)
                else:
                    subs_path = has_subs[2]
                subtitle = translator.get_dict_subs_from_data(subs_path)
                voiceover = translator.modify_voice(language, subtitle, content_path.audio)
                control.add_voiceover(url, language, voiceover)
                has_audio = control.have_translate_voice(url, language)
            content_path.audio = has_audio[2]
            result_video = translator.merge_video_audio(content_path)
        elif translate_to == 'Subs' and language != 'default':
            has_subs = control.have_translate_subs(url, language)
            if not has_subs:
                subs_path = core.get_subs_from_youtube(url, language)
                control.add_subtitles(url, language, subs_path)
            else:
                subs_path = has_subs[2]
            result_video = translator.merge_video_subs(content_path, subs_path)
        else:
            result_video = translator.merge_video_audio(content_path)

        response = make_response(render_template('video.html', video=result_video))
        return response
    
    url = request.args.get('url')
    languages = ['Default']

    has_subs = translator.get_support_subs(url)
    if has_subs:
        languages += translator.SUPPORTED_LANGUAGES
    response = make_response(render_template('video_settings.html', languages=languages))
    response.set_cookie('url', url)
    return response


@app.route('/video', methods=['POST'])
def video():
    return render_template('video.html')
