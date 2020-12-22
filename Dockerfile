FROM python:3

WORKDIR /usr/src/app

EXPOSE 5000/tcp
EXPOSE 5001/tcp

ENV DEBUG=True

COPY requirements.txt ./

RUN apt-get update && apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev

RUN pip install --upgrade pip


RUN pip install -r requirements.txt
COPY . .
RUN pip install dist/scoring_engine-0.1-py3-none-any.whl
CMD ["engine"]

# CMD ["sh", "test.sh"]
# CMD [ "sh", "start.sh" ]
