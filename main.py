from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy.future import select

import models
import schemas
from database import async_session, engine

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


@app.post('/recipes/', response_model=schemas.RecipeIn)
async def recipe(recipe: schemas.RecipeIn) -> models.Recipe:
    async with async_session() as session:
        new_recipe = models.Recipe(**recipe.model_dump())
        session.add(new_recipe)
        await session.commit()
        await session.refresh(new_recipe)
        return new_recipe


@app.get('/recipes/', response_model=List[schemas.RecipeList])
async def recipes() -> List[models.Recipe]:
    async with async_session() as session:
        res = await session.execute(
            select(models.Recipe).order_by(
                models.Recipe.views.desc(),
                models.Recipe.time.desc()
            )
        )
        return res.scalars().all()


@app.get('/recipes/{recipe_id}', response_model=schemas.RecipeDetail)
async def check_recipes(recipe_id: int):
    async with async_session() as session:
        res = await session.execute(select(models.Recipe).where(models.Recipe.id == recipe_id))
        recipe_real = res.scalar_one_or_none()
        if not recipe_real:
            raise HTTPException(status_code=404, detail="Рецепт не найден")
        recipe_real.views += 1
        await session.commit()
        await session.refresh(recipe_real)
        return recipe_real