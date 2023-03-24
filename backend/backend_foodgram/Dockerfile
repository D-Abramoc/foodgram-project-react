FROM python:3.10-slim

WORKDIR /app

COPY /home/dmitry/Dev/Diploma/foodgram-project-react/backend/backend_foodgram/requirements.txt .
# COPY . ./requirements.txt
# RUN apt-get update -y \
# && apt-get upgrade -y

RUN pip install -r requirements.txt
# && pip install --upgrade pip \
# && pip install -r /app/requirements.txt --no-cache-dir

# COPY ./ .

CMD python manage.py runserver 0:5000
# CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]