import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class MongoConfig:
    _MONGO_HOST = os.environ['MONGO_HOST']
    _MONGO_PORT = os.environ['MONGO_PORT']
    _MONGO_ROOT_NAME = os.environ['MONGO_ROOT_NAME']
    _MONGO_ROOT_PASSWORD = os.environ['MONGO_ROOT_PASSWORD']

    MONGO_URL = f'mongodb://{_MONGO_ROOT_NAME}:{_MONGO_ROOT_PASSWORD}@{_MONGO_HOST}:{_MONGO_PORT}'
    MONGO_DATABASE_NAME = os.environ['MONGO_DATABASE_NAME']


class MySQLConfig:
    _MYSQL_HOST = os.environ['MYSQL_HOST']
    _MYSQL_PORT = os.environ['MYSQL_PORT']
    _MYSQL_ROOT = os.environ['MYSQL_ROOT_NAME']
    _MYSQL_ROOT_PASSWORD = os.environ['MYSQL_ROOT_PASSWORD']
    _MYSQL_DATABASE_NAME = os.environ['MYSQL_DATABASE_NAME']

    MYSQL_URL = f'mysql+pymysql://{_MYSQL_ROOT}:{_MYSQL_ROOT_PASSWORD}@{_MYSQL_HOST}:{_MYSQL_PORT}/{_MYSQL_DATABASE_NAME}'


class SQLAlchemyConfig:
    POOL_RECYCLE = 3600
    POOL_SIZE = 20
    MAX_OVERFLOW = 20
    POOL_PRE_PING = True

    AUTO_COMMIT = False
    AUTO_FLUSH = False
    EXPIRE_ON_COMMIT = False
