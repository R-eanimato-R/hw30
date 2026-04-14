from typing import Optional

from pydantic import BaseModel


class RecipeBase(BaseModel):
    id: int
    name: str
    time: int


class RecipeList(RecipeBase):
    views: int

    class Config:
        from_attributes = True


class RecipeDetail(RecipeBase):
    ingredients: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RecipeIn(BaseModel):
    name: str
    time: int
    ingredients: Optional[str] = None
    description: Optional[str] = None
