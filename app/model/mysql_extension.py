from sqlalchemy import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import MySQLConfig, SQLAlchemyConfig

Base = declarative_base()


def create_all_table():
    from app.model.user.user_model import User

    Base.metadata.create_all(MySQLConnector.engine)


class MySQLInitializer:

    @staticmethod
    def create_engine():
        from sqlalchemy import create_engine

        return create_engine(
            url=MySQLConfig.MYSQL_URL,
            pool_recycle=SQLAlchemyConfig.POOL_RECYCLE,
            pool_size=SQLAlchemyConfig.POOL_SIZE,
            max_overflow=SQLAlchemyConfig.MAX_OVERFLOW,
            pool_pre_ping=SQLAlchemyConfig.POOL_PRE_PING
        )

    @staticmethod
    def create_session(engine: Engine) -> scoped_session:
        return scoped_session(
            sessionmaker(
                bind=engine,
                autocommit=SQLAlchemyConfig.AUTO_COMMIT,
                autoflush=SQLAlchemyConfig.AUTO_FLUSH,
                expire_on_commit=SQLAlchemyConfig.EXPIRE_ON_COMMIT
            )
        )


class MySQLConnector:
    engine = MySQLInitializer.create_engine()
    session = MySQLInitializer.create_session(engine)
