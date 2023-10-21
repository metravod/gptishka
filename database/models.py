import os
from datetime import datetime

from sqlalchemy import Column, ForeignKey, JSON, ARRAY
from sqlalchemy import DateTime, Integer, BigInteger, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

postgre_url = os.getenv('POSTGRE_URL')


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
    owner = Column(BigInteger, ForeignKey('Users.id'), nullable=False)
    date_start = Column(DateTime, default=datetime.now, nullable=False)
    name = Column(String, nullable=False)
    content = Column(ARRAY(JSON))

    def __repr__(self):
        return f'{self.name}'


# Создаем движок
engine = create_engine(postgre_url, echo=True)
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()
