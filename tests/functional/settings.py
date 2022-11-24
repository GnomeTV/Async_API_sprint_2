from pydantic import BaseSettings, Field


class ServiceSetting(BaseSettings):
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_HOST')
    api_version: str = Field('api/v1/', env='API_VERSION')


class ElasticSettings(ServiceSetting):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')


class RedisSettings(ServiceSetting):
    redis_host: str = Field('redis://127.0.0.1:6379', env='REDIS_HOST')


es_setting = ElasticSettings()
redis_setting = RedisSettings()
service_setting = ServiceSetting()
