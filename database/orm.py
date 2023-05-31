from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from database.models import Base, User, UserContext

from settings.db_config import postgre_url


def _create_session():
    engine = create_engine(postgre_url, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def add_user(tg_id) -> None:
    session = _create_session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if user is None:
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        session.commit()


def get_user(tg_id) -> User | None:
    session = _create_session()
    return session.query(User).filter(User.tg_id == tg_id).first()


def get_context(tg_id, name: str) -> UserContext | None:
    session = _create_session()
    user = get_user(tg_id)
    return session.query(UserContext).filter(UserContext.owner == user.id, UserContext.name == name).first()


def get_list_contexts_by_user(tg_id) -> list:
    user = get_user(tg_id)
    return [context.name for context in user.contexts]


def delete_user_context(tg_id, name_context):
    session = _create_session()
    user = get_user(tg_id)
    context = session.query(UserContext).filter(UserContext.owner == user.id, UserContext.name == name_context).first()
    if context:
        session.delete(context)
        session.commit()
    else:
        return None


def save_context(tg_id, name, content):
    session = _create_session()
    user = get_user(tg_id)
    context = get_context(tg_id, name)
    if context:
        context.update({'content': content})
        session.commit()
    else:
        new_context = UserContext(owner=user.id, name=name, content=content)
        session.add(new_context)
        session.commit()
