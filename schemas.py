from typing import Optional

from pydantic import BaseModel, ConfigDict


class RecipeBase(BaseModel):
    id: int
    name: str
    time: int

    model_config = ConfigDict(from_attributes=True)


class RecipeList(RecipeBase):
    views: int


class RecipeDetail(RecipeBase):
    ingredients: Optional[str] = None
    description: Optional[str] = None
    views: int


class RecipeIn(BaseModel):
    name: str
    time: int
    ingredients: Optional[str] = None
    description: Optional[str] = None
