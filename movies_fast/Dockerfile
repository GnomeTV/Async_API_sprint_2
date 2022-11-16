FROM python:3.10

WORKDIR /opt/api

COPY requirements.txt requirements.txt
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

CMD ["bash", "run.sh"]