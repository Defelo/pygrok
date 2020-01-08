FROM python:3.8-alpine

WORKDIR /app

RUN pip install pipenv

ADD Pipfile /app/
ADD Pipfile.lock /app/

RUN pipenv install

ADD ngrok.x86 /app/
ADD ngrok.arm /app/
ADD totp.py /app/
ADD telegram.py /app/
ADD ngrok.py /app/
ADD pygrok.py /app/

CMD pipenv run pygrok
