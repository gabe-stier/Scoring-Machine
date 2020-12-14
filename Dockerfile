FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000/tcp
ENV FLASK_APP='front_end/__init__.py:app()'
ENV FLASK_ENV='development'

CMD ["sh", "./test.sh"]
# CMD [ "sh", "./start.sh" ]
