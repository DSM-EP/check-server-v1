# run.py
from typing import List

from fastapi import FastAPI, HTTPException, Depends

app = FastAPI()

# config.py
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


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


class JWTConfig:
    KEY = os.environ['JWT_KEY']


# extension.py
from sqlalchemy import Engine, create_engine, BOOLEAN
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager


class MySQLInitializer:

    @staticmethod
    def create_engine():
        return create_engine(
            url=MySQLConfig.MYSQL_URL,
            pool_recycle=SQLAlchemyConfig.POOL_RECYCLE,
            pool_size=SQLAlchemyConfig.POOL_SIZE,
            max_overflow=SQLAlchemyConfig.MAX_OVERFLOW,
            pool_pre_ping=SQLAlchemyConfig.POOL_PRE_PING,
            echo=True
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


@contextmanager
def session_scope() -> Session:
    try:
        yield MySQLConnector.session
        MySQLConnector.session.commit()

    except HTTPException as e:
        MySQLConnector.session.rollback()
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )

    except Exception as e:
        MySQLConnector.session.rollback()
        raise HTTPException(
            status_code=500,
            detail=e.args
        )

    finally:
        MySQLConnector.session.close()


Base = declarative_base()

# model.py

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, INTEGER, VARCHAR, ForeignKey


class User(Base):
    __tablename__ = 'tbl_user'

    user_id = Column('user_id', INTEGER, primary_key=True, autoincrement=True)
    name = Column('name', VARCHAR(5), nullable=False)
    email = Column('email', VARCHAR(25), nullable=False)
    image_path = Column('image_path', VARCHAR(255), nullable=False)


class Admin(Base):
    __tablename__ = 'tbl_admin'

    admin_id = Column('admin_id', VARCHAR(255), nullable=False, primary_key=True)
    password = Column('password', VARCHAR(255), nullable=False)


class Room(Base):
    __tablename__ = 'tbl_room'

    creator_id = Column('creator_id', INTEGER, ForeignKey('tbl_user.user_id'), primary_key=True)
    room_id = Column('room_id', INTEGER, primary_key=True, autoincrement=True)
    emoji = Column('emoji', VARCHAR(255), nullable=False)
    name = Column('name', VARCHAR(255), nullable=False)
    is_approved = Column('is_approved', BOOLEAN, nullable=False, default=False)

    user = relationship('User')


class JoinedRoom(Base):
    __tablename__ = 'tbl_registered_room'
    user_id = Column('user_id', INTEGER, ForeignKey('tbl_user.user_id'), primary_key=True)
    room_id = Column('room_id', INTEGER, ForeignKey('tbl_room.room_id'), primary_key=True)

    user = relationship('User')
    room = relationship('Room')


class Todo(Base):
    __tablename__ = 'tbl_todo'

    todo_id = Column('todo_id', INTEGER, primary_key=True, autoincrement=True)
    name = Column('name', VARCHAR(255), nullable=False)
    is_approved = Column('is_approved', BOOLEAN, nullable=False, default=False)


class JoinedTodo(Base):
    __tablename__ = 'tbl_registered_todo'
    __allow_unmapped__ = True

    room_id = Column('room_id', INTEGER, ForeignKey('tbl_room.room_id'), primary_key=True)
    todo_id = Column('todo_id', INTEGER, ForeignKey('tbl_todo.todo_id'), primary_key=True)
    amount = Column('amount', INTEGER, nullable=False, default=0, server_default='0')

    room = relationship('Room')
    todo: Todo = relationship('Todo')


from jwt import encode, decode
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def generate_access_token(uid, role):
    return encode(
        payload={
            'uid': uid,
            'role': role
        },
        key=JWTConfig.KEY
    )


def get_user_id_from_jwt(token: str):
    payload = decode(
        jwt=token,
        algorithms='HS256',
        key=JWTConfig.KEY
    )
    return payload['uid']


def get_role_from_jwt(token: str):
    payload = decode(
        jwt=token,
        algorithms='HS256',
        key=JWTConfig.KEY
    )
    return payload['role']


from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    admin_id: str
    password: str


class SignUpOrInRequest(BaseModel):
    id_token: str


class CreateRoomRequest(BaseModel):
    emoji: str
    name: str


class CheckRoomRequest(BaseModel):
    is_approved: bool


class CreateTodoRequest(BaseModel):
    name: str


class CreateJoinedTodoRequest(BaseModel):
    room_id: int
    todo_id: int


# Admin
@app.post('/admin/login')
def admin_login(request: AdminLoginRequest):
    with session_scope() as session:
        admin = session.query(Admin).filter(Admin.admin_id == request.admin_id).scalar()

        if admin.password != request.password:
            raise HTTPException(status_code=400, detail='admin password incorrect')

    return generate_access_token(0, 'ADMIN')


# user
@app.get('/user/auth')
def get_client_id():
    pass


@app.post('/user/auth')
def register_or_login(request: SignUpOrInRequest):
    pass


# Room
@app.post('/room')
def create_room(request: CreateRoomRequest, token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_jwt(token)
    with session_scope() as session:
        session.add(
            Room(
                creator_id=user_id,
                **request.dict()
            )
        )


@app.patch('/room')
def approve_or_reject_room(room_id: int, request: CheckRoomRequest):
    with session_scope() as session:
        session.query(Room).filter(Room.room_id == room_id).update({
            Room.is_approved: request.is_approved
        })

        room = session.query(Room).filter(Room.room_id == room_id).one()

        joined_room = JoinedRoom(
            user_id=room.creator_id,
            room_id=room_id
        )

        session.add(joined_room)


@app.get('/room/detail')
def get_room_detail(room_id: int):
    with session_scope() as session:
        room = session.query(Room). \
            join(User, Room.creator_id == User.user_id) \
            .filter(Room.room_id == room_id).scalar()

        return {
            'creator_name': room.user.name,
            'room_name': room.name,
            'room_emoji': room.emoji,
            'room_id': room.room_id
        }


@app.get('/room/list')
def get_room_list(is_approved: bool):
    with session_scope() as session:
        return session.query(Room).filter(Room.is_approved == is_approved).all()


@app.get('/room/my-list')
def get_my_room_list(user_id: int):
    with session_scope() as session:
        my_list: List[Room] = session \
            .query(Room) \
            .join(JoinedRoom, JoinedRoom.room_id == Room.room_id) \
            .filter(JoinedRoom.user_id == user_id) \
            .all()

        return [
            {
                'room_id': i.room_id,
                'room_name': i.name,
                'emoji': i.emoji
            }
            if i else None for i in my_list
        ]


@app.post('/todo')
def create_room(request: CreateTodoRequest):
    with session_scope() as session:
        session.add(
            Todo(
                name=request.name
            )
        )


@app.patch('/todo/approve')
def approve_todo(todo_id: int):
    with session_scope() as session:
        session.query(Todo) \
            .filter(Todo.todo_id == todo_id) \
            .update({Todo.is_approved: True})


@app.get('/todo/list')
def get_todo_list(is_approved: bool):
    with session_scope() as session:
        return session.query(Todo) \
            .filter(Todo.is_approved == is_approved).all()


@app.get('/todo/my-list')
def get_my_todo_list(room_id: int):
    with session_scope() as session:
        result: JoinedTodo = session.query(JoinedTodo) \
            .join(Todo, JoinedTodo.todo_id == Todo.todo_id) \
            .filter(JoinedRoom.room_id == room_id) \
            .all()

        return [
            {
                'todo_id': i.todo_id,
                'name': i.todo.name,
                'amount': i.amount
            }
            if i else None for i in result
        ]


@app.patch('/todo')
def check_todo(room_id: int, todo_id: int):
    with session_scope() as session:
        session.query(JoinedTodo) \
            .filter(JoinedTodo.room_id == todo_id, JoinedTodo.room_id == room_id) \
            .update({
            JoinedTodo.amount: JoinedTodo.amount + 1
        })


@app.post('/todo/room')
def add_to_room(request: CreateJoinedTodoRequest):
    with session_scope() as session:
        session.add(
            JoinedTodo(
                **request.dict()
            )
        )


Base.metadata.create_all(MySQLConnector.engine)
