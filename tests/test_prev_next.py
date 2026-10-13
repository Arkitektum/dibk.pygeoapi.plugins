"""Unit tests for the prev/next ids of a single item."""

import pytest
from postgresql_ext import PostgreSQLProvider
from sqlalchemy import Column, Integer, create_engine, event
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = "item"
    objid = Column(Integer, primary_key=True)


class _StubProvider(PostgreSQLProvider):
    """Skips DB-backed init; sets only what _set_prev_and_next consults."""

    def __init__(self):
        self.table_model = Item
        self.id_field = "objid"


@pytest.fixture
def session_with():
    sessions = []

    def make(*ids):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)
        session = Session(engine)
        session.add_all(Item(objid=i) for i in ids)
        session.commit()
        sessions.append(session)
        return session

    yield make

    for session in sessions:
        session.close()


def neighbours(session, item_id):
    feature = {}
    _StubProvider()._set_prev_and_next(item_id, feature, session)
    return feature["prev"], feature["next"]


@pytest.mark.parametrize(
    ("ids", "item_id", "expected"),
    [
        ((1, 2, 5, 9), 2, ("1", "5")),
        ((1, 2, 5, 9), 1, ("9", "2")),
        ((1, 2, 5, 9), 9, ("5", "1")),
        ((7,), 7, ("7", "7")),
        ((1, 2, 10, 20), 2, ("1", "10")),
    ],
    ids=[
        "middle",
        "first wraps to last",
        "last wraps to first",
        "only item",
        "numeric order",
    ],
)
def test_prev_and_next_follow_id_order(session_with, ids, item_id, expected):
    assert neighbours(session_with(*ids), item_id) == expected


def test_prev_and_next_follow_rows_changed_since_the_last_request(session_with):
    session = session_with(1, 5, 9)
    assert neighbours(session, 5) == ("1", "9")

    session.add(Item(objid=3))
    session.commit()

    assert neighbours(session, 5) == ("3", "9")
    assert neighbours(session, 3) == ("1", "5")


def test_prev_and_next_never_read_the_whole_table(session_with):
    session = session_with(1, 2, 5, 9)
    statements = []
    event.listen(
        session.get_bind(),
        "before_cursor_execute",
        lambda _conn, _cursor, statement, *_args: statements.append(statement),
    )

    neighbours(session, 1)
    neighbours(session, 9)

    assert statements
    assert all(
        "LIMIT" in statement or "max(" in statement or "min(" in statement
        for statement in statements
    ), statements
