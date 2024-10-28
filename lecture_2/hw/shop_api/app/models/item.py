from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, association_table


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    deleted = Column(Boolean, default=False)
    cart_id = Column(Integer, ForeignKey("cart.id"))
    cart = relationship("Cart", secondary=association_table, back_populates="items")
    quantity = Column(Integer, default=0)
