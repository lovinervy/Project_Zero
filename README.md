# Project_Zero

## Пример работы
[Оригинальное видео](https://www.youtube.com/watch?v=t_p4ZyAYyaY)

[Прогнанный через наш сервис](https://zen.yandex.ru/embed/vps3aVbErE3Y)
## Перед установкой
Скачать программу через [git](https://git-scm.com/):

```git clone https://github.com/lovinervy/Project_Zero.git -b update```

## Внимание 
В requirements.txt не все библиотеки нужны для корректной работы программы, для того, чтобы узнать какие конкретно библиотеки нужны, слейдуйте по инструкции

## Установка

### Здесь описано установка только под Ubuntu

Установка ffmpeg:
```bash
sudo apt install ffmpeg
```

Есть 3 способа генерации голоса из которых 2 бесплатные и 1 платная.
* Через сервис Yandex Cloud (Платно)
* Через TTS Silero (Бесплатно) (Пока не задокументировано)
* Через pyttsx3 (Бесплатно, но проверялась только под ОС Mac) (Пока не задокументировано)


### Yandex Cloud
<span style="color:red">Внимание, чтобы пользоватся сервисами Яндекса нужно иметь деньги на счету Я.Облаки!</span>

Чтобы запустить программу с использованием сервисов Яндекса нужно получить Folder ID и OAuth

Как получить: [Folder ID](https://cloud.yandex.ru/docs/resource-manager/operations/folder/get-id)

Как получить: [OAuth-токен](https://cloud.yandex.ru/docs/iam/concepts/authorization/oauth-token)

Ключи добавить в ```config.json```

Установить [sox](https://manpages.ubuntu.com/manpages/bionic/man1/sox.1.html)
```bash
sudo apt intall sox
```
Установить [Python](https://pytohn.org) >= 3.8.5
```bash
sudo apt install python3
```

В терминале зайти в директорию программы и выполнить след. команды

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install Flask pytube requests pydub
```

Чтобы запустить на локальном машине
```bash
flask run
```

В браузере в адресной строке указываете
```localhost:5000```
