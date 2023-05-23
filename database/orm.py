from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, User, UserContext, MessageFromContext

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


def add_context(tg_id, name: str, context_id: int, is_active: bool):
    session = _create_session()
    user = get_user(tg_id)
    context = _get_context(tg_id, name)
    if context is None:
        new_context = UserContext(context_id=context_id, owner=user.id, name=name, is_active=is_active)
        session.add(new_context)
        session.commit()


def _get_context(tg_id, name: str) -> UserContext | None:
    session = _create_session()
    user = get_user(tg_id)
    return session.query(UserContext).filter(UserContext.owner == user.id, UserContext.name == name).first()


def get_active_context(tg_id) -> UserContext | None:
    session = _create_session()
    user = get_user(tg_id)
    return session.query(UserContext).filter(UserContext.owner == user.id, UserContext.is_active).first()


def disactive_context(tg_id, name: str):
    session = _create_session()
    user = get_user(tg_id)
    session.query(UserContext).filter(UserContext.owner == user.id, UserContext.name == name).update({'is_active': False})
    session.commit()


def add_message(tg_id: int, name_context: str, content: dict):
    session = _create_session()
    context = _get_context(tg_id, name_context)
    new_message = MessageFromContext(context=context.id, message=content)
    session.add(new_message)
    session.commit()


def get_talk(tg_id, name_context) -> list:
    context = _get_context(tg_id, name_context)
    return [el.message for el in context.messages]


def get_list_contexts_by_user(tg_id) -> list:
    user = get_user(tg_id)
    return [context.name for context in user.contexts]


def update_count_tokens_in_context(tg_id, name, count_tokens: int):
    session = _create_session()
    user = get_user(tg_id)
    session.query(UserContext).filter(UserContext.owner == user.id, UserContext.name == name).update({'tokens': count_tokens})
    session.commit()


def delete_user_context(tg_id, name_context):
    session = _create_session()
    context = _get_context(tg_id, name_context)
    session.delete(context)
    session.commit()
