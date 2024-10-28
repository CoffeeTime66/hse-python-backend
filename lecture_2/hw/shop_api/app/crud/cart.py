from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import association_table
from models import Cart


def create_cart(db: Session) -> Cart:
    cart = Cart()
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart_by_id(db: Session, cart_id: int) -> Cart:
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
    for item in db_cart.items:
        if len(db_cart.items) == 0:
            return db_cart
        else:
            association_row = db.query(association_table).filter_by(cart_id=cart_id).first()
            item.quantity = association_row.quantity
    return db_cart


def get_carts(db: Session, offset: int = 0, limit: int = 10, min_price: float = None,
              max_price: float = None, min_quantity: int = None, max_quantity: int = None) -> List[Cart]:
    query = db.query(Cart)

    if min_price:
        query = query.filter(Cart.price >= min_price)
    if max_price:
        query = query.filter(Cart.price <= max_price)
    if max_quantity == 0:
        query = query.filter(Cart.items == None)
    query = query.join(association_table)

    # Выполнение подсчета количества товаров в каждой корзине
    query = query.group_by(Cart.id). \
        having(func.sum(association_table.c.quantity) >= min_quantity if min_quantity else True). \
        having(func.sum(association_table.c.quantity) <= max_quantity if max_quantity else True)

    return query.offset(offset).limit(limit).all()


def add_item_to_cart(db: Session, cart_id: int, item_id: int):
    cart = get_cart_by_id(db, cart_id)
    current_quantity = 1
    association_row = (
        db.query(association_table)
        .filter(association_table.c.cart_id == cart_id)
        .filter(association_table.c.item_id == item_id)
        .first()
    )

    if association_row:
        current_quantity = association_row.quantity + 1
        db.query(association_table).filter(
            (association_table.c.cart_id == cart_id) & (association_table.c.item_id == item_id)
        ).update({association_table.c.quantity: current_quantity})
    else:
        association = association_table.insert().values(cart_id=cart_id, item_id=item_id, quantity=current_quantity)
        db.execute(association)

    return cart


def update_cart_price(db: Session, cart_id: int):
    cart = get_cart_by_id(db, cart_id)

    # вычислить сумму цен всех товаров
    total_price = 0
    for item in cart.items:
        total_price += item.price * item.quantity

    cart.price = total_price
    db.add(cart)
    db.commit()
