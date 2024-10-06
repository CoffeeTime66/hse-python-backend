from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing_extensions import Any
from sqlalchemy import Table, Column, Integer, ForeignKey


@as_declarative()
class Base:
    metadata = None
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


association_table = Table('cart_item_association', Base.metadata,
                          Column('cart_id', Integer, ForeignKey('cart.id')),
                          Column('item_id', Integer, ForeignKey('item.id')),
                          Column('quantity', Integer, default=1)
                          )
