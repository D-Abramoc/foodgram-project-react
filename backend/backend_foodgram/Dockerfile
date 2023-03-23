FROM python:3.10-slim

WORKDIR /app

COPY . .
# COPY . ./requirements.txt
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
# RUN apt-get update -y \
# && apt-get upgrade -y pip \
# && pip install --upgrade pip \
# && pip install -r /app/requirements.txt --no-cache-dir

# COPY ./ .

CMD python manage.py runserver 0:5000
# CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]