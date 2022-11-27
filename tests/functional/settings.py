from pydantic import BaseSettings, Field


class ServiceSetting(BaseSettings):
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_HOST')
    api_version: str = Field('api/v1/', env='API_VERSION')


class ElasticSettings(ServiceSetting):
    es_scheme: str = Field('http', env='ELASTIC_SCHEME')
    es_host: str = Field('127.0.0.1', env='ELASTIC_HOST')
    es_port: str = Field('9200', env='ELASTIC_PORT')


class RedisSettings(ServiceSetting):
    scheme: str = Field('redis', env='REDIS_SCHEME')
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')


es_setting = ElasticSettings()
redis_setting = RedisSettings()
service_setting = ServiceSetting()
