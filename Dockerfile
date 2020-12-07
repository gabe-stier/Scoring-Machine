FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

CMD [ "sh", "./start.sh" ]
# WORKDIR /usr/src/app/app
EXPOSE 5000/tcp