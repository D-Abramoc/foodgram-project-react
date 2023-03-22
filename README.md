# praktikum_new_diplom
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
- Создать файл окружения и заполнить его по примеру
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

## Автор
![Me](image/me.JPG)