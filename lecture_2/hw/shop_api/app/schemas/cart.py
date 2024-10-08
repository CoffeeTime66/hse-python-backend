from typing import List
from pydantic import BaseModel

from .item import Item


class CartBase(BaseModel):
    pass


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    id: int
    items: List[Item] = []
    price: float

    class Config:
        from_attributes = True
