FROM python:3

WORKDIR /usr/src/app

EXPOSE 5001
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

CMD ["python","__init__.py"]

