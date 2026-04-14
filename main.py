from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy.future import select

import models
import schemas
from database import engine, session

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


@app.post("/recipes/", response_model=schemas.RecipeIn)
async def add_recipe(recipe: schemas.RecipeIn) -> models.Recipe:
    new_recipe = models.Recipe(**recipe.dict())
    async with session.begin():
        session.add(new_recipe)
        await session.commit()
    return new_recipe


@app.get("/recipes/", response_model=List[schemas.RecipeList])
async def recipes() -> List[models.Recipe]:
    res = await session.execute(
        select(models.Recipe).order_by(
            models.Recipe.views.desc(), models.Recipe.time.desc()
        )
    )
    return res.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
async def check_recipes(
    recipe_id: int,
):
    res = await session.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe_real = res.scalar_one_or_none()
    if not recipe_real:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    recipe_real.views += 1
    await session.commit()
    return recipe_real
