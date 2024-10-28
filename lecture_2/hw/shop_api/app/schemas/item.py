from pydantic import BaseModel
from typing_extensions import Optional


class ItemBase(BaseModel):
    name: str
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    deleted: bool
    cart_id: Optional[int]
    quantity: Optional[int]

    class Config:
        from_attributes = True


class EmptyItemData(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
