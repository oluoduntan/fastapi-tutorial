from TodoApp.main import app
from TodoApp.database import Base
from TodoApp.routers.todos import get_db, get_current_user
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from TodoApp.models import Todo

SQLALCHEMY_DATABASE_URL = "sqlite:///./TodoApp/test/test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # poolclass=StaticPool,
    pool_size=1,
    pool_timeout=0,
    max_overflow=0
)
TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    return

def override_get_current_user():
    return {"user_name": "test_user", "user_id": 1, 'role': "admin"}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture()
def test_todo():
    todo = Todo(
        title="Learn to Code!",
        description="Need to Learn Everyday!",
        priority=5,
        complete=False,
        owner_id = 1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.close()
    yield  todo
    with engine.connect() as connections:
        connections.execute(text("DELETE FROM todo;"))
        connections.commit()

def test_read_all_authenticated(test_todo):
    response = client.get("/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"title": "Learn to Code!", "description": "Need to Learn Everyday!", "priority": 5, "complete": False, "owner_id": 1, "id": 1}]

def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"title": "Learn to Code!", "description": "Need to Learn Everyday!", "priority": 5, "complete": False, "owner_id": 1, "id": 1}

def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
