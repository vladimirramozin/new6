# YATUBE

## Описание проекта: 

социальная сеть, позволяющая писать, комментировать, обновлять посты. Подписываться на интересующих авторов. Создавать и вступать в группы по интересам. Реализованы модели: посты (Post), группы (Group), комментарии (Comment), пописки (Follow). Подключено кеширование главной страницы. Реализованы кастомные страницы ошибок.

## Как запустить проект: 
Клонировать репозиторий и перейти в него в командной строке:
"""
git clone https://github.com/vladimirramozin/new6.git
cd api_final_yatube
"""
Cоздать и активировать виртуальное окружение:
"""
python3 -m venv env source .venv/bin/activate 
"""
Установить зависимости из файла requirements.txt:
"""
python3 -m pip install --upgrade pip pip install -r requirements.txt 
"""
Выполнить миграции:
"""
python3 manage.py migrate Запустить проект:
python3 manage.py runserver
"""
## Системные требования: 
Django==2.2.16
mixer==7.1.2
Pillow==8.3.1
pytest==6.2.4
pytest-django==4.4.0
pytest-pythonpath==0.7.3
requests==2.26.0
six==1.16.0
sorl-thumbnail==12.7.0
