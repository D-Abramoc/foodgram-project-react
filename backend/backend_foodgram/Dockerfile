FROM python:3.10-slim

WORKDIR /app

COPY . .
RUN apt update -y \
&& apt upgrade -y
RUN pip install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "backend_foodgram.wsgi:application", "--bind", "0:8000" ]