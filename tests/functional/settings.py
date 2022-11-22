from pydantic import BaseSettings, Field


class ElasticSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_HOST')


# class RedisSettings(BaseSettings):
#     es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
#     es_index: str =
#     es_id_field: str =
#     es_index_mapping: dict =
#
#     redis_host: str =
#     service_url: str =


es_setting = ElasticSettings()
# redis_setting = RedisSettings
