# praktikum_new_diplom
# Kittygram

## Описание

Foodgram- сайт на котором пользователи могут регистрироваться, делиться своими рецептами, информацией о них, и смотреть рецепты других пользователей, добавлять их к себе в покупки, избранное и подписываться или отписываться от других пользователей. 

# Как запустить проект:
__
## Подключение к серверу:

* Нужно зайти на сервер с помощью команды:
ssh -i путь_до_файла_с_SSH_ключом/название_файла_закрытого_SSH-ключа login@ip 
Далее вам понадобится ввести пароль от закрытого SSH-ключа (passphrase).

## Установка backend и frontend приложения:

* Клонировать репозиторий и перейти в него в командной строке:
cd foodgram-project-react

* Cоздать и активировать виртуальное окружение:
python3 -m venv env
source env/bin/activate

* Установить зависимости из файла requirements.txt:
python3 -m pip install --upgrade pip
pip install -r requirements.txt

* Выполнить миграции:
python3 manage.py migrate

* После деплоя на сервер соберите статику:
sudo docker compose -f docker-compose.production.yml  exec backend python manage.py collectstatic

sudo docker compose -f docker-compose.production.yml  exec backend cp -r /app/static/. /backend_static/static/

* Загрузите ингредиенты:
 docker compose -f docker-compose.production.yml exec backend python manage.py load_data

* Создайте суперпользователя:
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

Находять в панели административной панели создайте теги: назовите их: Завтрак, Обед, Ужин, задайте цветовой код и slug.

* Создайте файл .env:
POSTGRES_DB='название bd'
POSTGRES_USER='указать user'
POSTGRES_PASSWORD='user пароль'
DB_NAME='указать name db'
DB_PORT='указать порт'
DB_HOST='хост db'
DEBUG='False'
ALLOWED_HOSTS='указать хосты'
SECRET_KEY='секретный ключ'
___

## Установка Gunicorn и Nginx на сервере реализуется автоматически при деплое проекта на сервер
___

## Стек технологий

Django==3.2.3
djangorestframewosudo systemctl reload nginx rk==3.12.4
djoser==2.1.0
gunicorn==20.1.0
Nginx
Certbot

## GitHub Actions

Логика автомитизации тестирования, сборки образов проекта и их отправка на Docker Hub, перезапуска и отправки сообщения о успешном деплое по шагам описана в файле .github/workflows/foodgram_workflow.yml workflow.


Автор [Darya](https://github.com/PopkovaDar):relaxed:
