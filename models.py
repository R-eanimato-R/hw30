from sqlalchemy import Column, String, Integer, Text

from database import Base


class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    time = Column(Integer, nullable=False)
    ingredients = Column(Text)
    description = Column(Text)
    views = Column(Integer, default=0)
