import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base
import models
from routers.auth import get_current_user
from routers.products import get_db
from routers.orders import get_db as get_order_db
from routers.rating import get_db as get_rating_db
from routers.categories import get_db as get_category_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./testcommerce.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    def override_get_current_user():
        return models.User(id=1, email="test@ecommerce.local", first_name="Test", last_name="User")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_category_db] = override_get_db
    app.dependency_overrides[get_order_db] = override_get_db
    app.dependency_overrides[get_rating_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()