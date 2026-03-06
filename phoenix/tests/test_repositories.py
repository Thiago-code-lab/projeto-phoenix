from phoenix.core.database import Base, engine, get_session
from phoenix.core.models import Goal
from phoenix.core.repository import Repository


def test_repository_add_and_list() -> None:
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        repo = Repository(session, Goal)
        repo.add(title="Teste repo")
        items = repo.list_all()
        assert any(item.title == "Teste repo" for item in items)
