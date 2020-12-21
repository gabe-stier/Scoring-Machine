FROM python:3

WORKDIR /usr/src/app

EXPOSE 5000/tcp
EXPOSE 5001/tcp

ENV FLASK_APP='front_end/__init__.py:app()'
ENV FLASK_ENV='development'
ENV DEBUG=True

COPY requirements.txt ./

RUN apt-get update && apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .


CMD ["sh", "test.sh"]
# CMD [ "sh", "start.sh" ]
