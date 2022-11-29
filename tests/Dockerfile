FROM python:3.10

WORKDIR /opt/tests
ENV PYTHONPATH=/opt/tests

COPY functional/requirements.txt requirements.txt
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

CMD ["bash", "run.sh"]