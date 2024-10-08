from sqlalchemy import Boolean, Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, association_table


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    items = relationship("Item", secondary=association_table, back_populates="cart")
    available = Column(Boolean, default=True)
    price = Column(Float, default=0.0)
