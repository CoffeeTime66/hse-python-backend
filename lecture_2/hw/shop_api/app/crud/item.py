from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from ..models.item import Item
from ..schemas.item import ItemCreate, ItemUpdate


def create_item(db: Session, item: ItemCreate) -> Item:
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item_by_id(db: Session, item_id: int) -> Item:
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(db: Session, offset: int = 0, limit: int = 10, min_price: float = None,
              max_price: float = None, show_deleted: bool = False) -> List[Item]:
    query = db.query(Item).filter(Item.deleted == False)
    if not show_deleted:
        query = query.filter(Item.deleted == False)
    if min_price:
        query = query.filter(Item.price >= min_price)
    if max_price:
        query = query.filter(Item.price <= max_price)
    return query.offset(offset).limit(limit).all()


def update_item(db: Session, item_id: int, item: ItemUpdate) -> Item:
    db_item = db.query(Item).filter(and_(Item.id == item_id, Item.deleted == False)).first()
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> Item:
    db_item = db.query(Item).filter(Item.id == item_id).first()
    db_item.deleted = True
    db.commit()
    db.refresh(db_item)
    return db_item
