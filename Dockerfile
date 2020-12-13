FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

ENV FLASK_APP='app/__init__.py:app()'
ENV FLASK_ENV='development'

CMD ["flask", "run","--host=0.0.0.0"]

# CMD [ "sh", "./start.sh" ]
# WORKDIR /usr/src/app/app
EXPOSE 5000/tcp
EXPOSE 6379