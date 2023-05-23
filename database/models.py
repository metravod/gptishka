from datetime import datetime

from sqlalchemy import Column, ForeignKey, JSON
from sqlalchemy import DateTime, Integer, BigInteger, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from settings.db_config import postgre_url


Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    connection_date = Column(DateTime, default=datetime.now, nullable=False)
    contexts = relationship('UserContext', backref='context', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return self.tg_id


class UserContext(Base):
    __tablename__ = 'UserContexts'
    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, nullable=False)
    owner = Column(BigInteger, ForeignKey('Users.id'), nullable=False)
    date_start = Column(DateTime, default=datetime.now, nullable=False)
    name = Column(String, nullable=False)
    tokens = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, nullable=False)
    messages = relationship('MessageFromContext', backref='content', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'{self.name}'


class MessageFromContext(Base):
    __tablename__ = 'MessagesFromContext'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now, nullable=False)
    context = Column(Integer, ForeignKey('UserContexts.id'), nullable=False)
    message = Column(JSON)

    def __repr__(self):
        return f'{self.message}'


# Создаем движок
engine = create_engine(postgre_url, echo=True)
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()
