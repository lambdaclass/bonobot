FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN set -ex && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "gunicorn", "-b0.0.0.0:8000", "wsgi:app", "--timeout", "200" ]
