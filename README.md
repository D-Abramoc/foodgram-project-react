# praktikum_new_diplom
## Подготовка postgresql
- Установите postgresql
```
sudo apt update
```
```
sudo apt install postgresql postgresql-contrib -y
```
- Подключитесь к СУБД
```
sudo -u postgres psql
```
- Создайте базу. Имя должно быть такое же какое будете создавать в окружении. Пример в файле .env.sample в корневом каталоге.
```
CREATE DATABASE <имя-базы>;
```
- Создайте пользователя и пароль. Также должны совпадать с данными окружения.
```
CREATE USER <логин-для-подключения-к-базе> WITH ENCRYPTED PASSWORD '<пароль-для-подключения-к-базе>';
```
- Дайте пользователю права на управление базой
```
GRANT ALL PRIVILEGES ON DATABASE <имя-базы> TO <логин-для-подключения-к-базе>; 
```
- Для возможности запуска тестов определите возможность создания тестовой базы
```
ALTER ROLE <логин-для-подключения-к-базе> CREATEDB;
```
## Развертывание на локальной машине
- Клонировать репозиторий
```
git@github.com:D-Abramoc/foodgram-project-react.git
``` 
- Перейти в каталог foodgram-project-react
```
cd foodgram-project-react
```
- Создать виртуальное окружение и активировать его
```
python3 -m venv venv
```
```
. venv/bin/activate
```
- Перейти в каталог backend
```
cd backend/
```
- Установить зависимости
```
pip install -r requirements.txt
```
- Перейти в каталог backend_foodgram/ содержащий файл settings.py
```
cd backend_foodgram/backend_foodgram/
```
- Создать файл окружения и заполнить его по примеру .env.sample
```
touch .env
```
- Создайте миграции
```
python manage.py makemigrations users
python manage.py makemigrations recipes
```
- Примените миграции
```
python manage.py migrate
```
- Создайте суперюзера
```
python manage.py createsuperuser
```
- Запустите локальный сервер
```
python manage.py runserver
```
## Запуск документации API
- Перейдите в каталог infra в корневом каталоге foodgram-project-react и выполите команду
```
sudo docker-compose up
```
- Документация API доступна по адресу
```
http://localhost/api/docs/
```


# Запуск на сервере #

![Workflow for test, build and deploy](https://github.com/D-Abramoc/foodgram-project-react/actions/workflows/foodgram_wf.yml/badge.svg)

Проект доступен по:
```
http://84.201.155.156/
```

## Описание ##

Цель проекта применить CICD при развертывании Django проекта на сервере

## Технологии ##

 - Python ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
 - Django  ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
 - Docker
 - Git Action ![Git](https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white)

## Запуск проекта ##
- Установить на сервер docker и docker-compose
- Создать форк репозитория:
```
github.com/D-Abramoc/foodgram-project-react.git
```
- В своем репозитории перейти на вкладку Settings:
![Tap on Settings](images/settings-min.png)
1. Нажать Secrets and variables:
![Tap Secrets and variables](images/tap-to-secrets-and-variables-min.png)
2. В открывшемся списке нажать Actions:
![Tap to Actions](images/tap-to-actions-min.png)
3. Нажать New repository secret:
![Tap New repository secret](images/tap-new-repository-secret-min.png)
4. Создать переменную из файла .secrets.sample:
![Add secret](images/add-secret-min.png)
- Повторить шаги 3 и 4 для каждой переменной.
- Скопировать из папки infra файлы docker-compose.yml и nginx.conf на ваш сервер в папку /home/<ваш-юзернейм>/:
```
scp -i <path-to-ssh-key> infra/docker-compose.yml <servername>@<ip>:/home/<username>/
```
```
scp -i <path-to-ssh-key> infra/nginx/ <servername>@<ip>:/home/<username>/
```
- Сделать любые изменения в файле README и запушить изменения в репозиторий.
- Зайти на сервер и выполнить команды:
```
sudo docker-compose exec web python manage.py makemigrations users
```
```
sudo docker-compose exec web python manage.py makemigrations recipes
```
```
sudo docker-compose exec web python manage.py migrate
```
```
sudo docker-compose exec web python manage.py collectstatic
```
- Для заполнения базы ингредиентов:
```
sudo docker-compose exec web python manage.py upload
```

- Открыть описание API проекта по адресу:
```
http://<ip-of-your-server>/redoc/
```
## Автор
![Me](image/me.JPG)