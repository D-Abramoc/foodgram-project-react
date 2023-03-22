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
## Автор
![Me](image/me.JPG)