from pydantic import BaseSettings, Field


class ServiceSetting(BaseSettings):
    scheme: str = Field('http', env='API_SCHEME')
    host: str = Field('127.0.0.1', env='API_HOST')
    port: str = Field('8000', env='API_PORT')
    api_version: str = Field('api/v1/', env='API_VERSION')


class ElasticSettings(ServiceSetting):
    scheme: str = Field('http', env='ELASTIC_SCHEME')
    host: str = Field('127.0.0.1', env='ELASTIC_HOST')
    port: str = Field('9200', env='ELASTIC_PORT')


class RedisSettings(ServiceSetting):
    scheme: str = Field('redis', env='REDIS_SCHEME')
    host: str = Field('127.0.0.1', env='REDIS_HOST')
    port: str = Field('6379', env='REDIS_PORT')


es_setting = ElasticSettings()
redis_setting = RedisSettings()
service_setting = ServiceSetting()
