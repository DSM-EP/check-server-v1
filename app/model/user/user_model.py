from app.model.mysql_extension import Base

from sqlalchemy import (
    Column,
    BINARY,
    VARCHAR,

)


class User(Base):
    __tablename__ = 'tbl_user'

    user_id = Column('id', BINARY(16), primary_key=True)
    name = Column('name', VARCHAR(5), nullable=False)
    email = Column('email', VARCHAR(25), nullable=False)
    image_path = Column('image_path', VARCHAR(255), nullable=False)