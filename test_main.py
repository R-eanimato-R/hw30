import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from database import Base, async_session, engine
from main import app


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session
        await session.execute(text("DELETE FROM recipes"))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_recipe(client):
    response = await client.post(
        "/recipes/",
        json={
            "name": "Тестовый рецепт",
            "time": 25,
            "ingredients": "яйца, молоко",
            "description": "простой тест",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Тестовый рецепт"
    assert data["time"] == 25
    assert "id" in data
    assert data["views"] == 0


@pytest.mark.asyncio
async def test_get_recipes_empty(client):
    response = await client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_recipes_with_data(client):
    resp1 = await client.post(
        "/recipes/",
        json={
            "name": "Рецепт 1",
            "time": 30,
            "ingredients": "a",
            "description": "d1",
        },
    )
    resp2 = await client.post(
        "/recipes/",
        json={
            "name": "Рецепт 2",
            "time": 20,
            "ingredients": "b",
            "description": "d2",
        },
    )

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    response = await client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [r["name"] for r in data]
    assert "Рецепт 1" in names
    assert "Рецепт 2" in names


@pytest.mark.asyncio
async def test_get_recipe_by_id(client):
    create_resp = await client.post(
        "/recipes/",
        json={
            "name": "Найти меня",
            "time": 15,
            "ingredients": "x",
            "description": "y",
        },
    )
    recipe_id = create_resp.json()["id"]

    response = await client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Найти меня"
    assert data["views"] >= 1


@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    response = await client.get("/recipes/99999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


@pytest.mark.asyncio
async def test_views_increment(client):
    create_resp = await client.post(
        "/recipes/",
        json={
            "name": "Просмотры",
            "time": 10,
            "ingredients": "z",
            "description": "w",
        },
    )
    recipe_id = create_resp.json()["id"]

    await client.get(f"/recipes/{recipe_id}")
    response = await client.get(f"/recipes/{recipe_id}")

    assert response.json()["views"] >= 2
