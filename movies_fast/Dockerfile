FROM python:3.10

WORKDIR /opt/api
ENV PYTHONPATH=/opt/api/src

COPY requirements.txt requirements.txt
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

CMD ["bash", "run.sh"]