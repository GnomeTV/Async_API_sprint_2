import time

from elasticsearch import Elasticsearch
from settings import es_setting

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{es_setting.scheme}://{es_setting.host}:{es_setting.port}',
                              validate_cert=False,
                              use_ssl=False,
                              )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
