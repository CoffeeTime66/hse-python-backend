from typing import List
from fastapi import APIRouter, Depends, status, Body, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

import crud, models, schemas

from database import get_session_local, engine

models.base.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Корзина
@router.post("/cart", response_model=schemas.Cart)
def create_cart(db: Session = Depends(get_session_local)):
    cart = crud.create_cart(db=db)
    response = JSONResponse(content={"id": cart.id}, status_code=status.HTTP_201_CREATED)
    response.headers["Location"] = f"/cart/{cart.id}"
    return response


@router.get("/cart/{cart_id}", response_model=schemas.Cart)
def read_cart(cart_id: int, db: Session = Depends(get_session_local)):
    crud.update_cart_price(db=db, cart_id=cart_id)
    db_cart = crud.get_cart_by_id(db=db, cart_id=cart_id)
    if db_cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return db_cart


@router.get("/cart", response_model=List[schemas.Cart])
def read_carts(offset: int = 0, limit: int = 10, min_price: float = None,
               max_price: float = None, min_quantity: int = None, max_quantity: int = None,
               db: Session = Depends(get_session_local)):
    if offset < 0 or limit <= 0 or (min_price is not None and min_price < 0) or (
            max_price is not None and max_price <= 0) or (min_quantity is not None and min_quantity < 0) or (
            max_quantity is not None and max_quantity < 0):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, )
    carts = crud.get_carts(db=db, offset=offset, limit=limit, min_price=min_price,
                           max_price=max_price, min_quantity=min_quantity, max_quantity=max_quantity)
    return carts


# Товар
@router.post("/item", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_session_local)):
    db_item = crud.create_item(db=db, item=item)
    response = JSONResponse(content={"id": db_item.id, "name": db_item.name, "price": db_item.price},
                            status_code=status.HTTP_201_CREATED)
    response.headers["Location"] = f"/cart/{db_item.id}"
    return response


@router.get("/item/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_session_local)):
    db_item = crud.get_item_by_id(db=db, item_id=item_id)
    if db_item is None or db_item.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    response = JSONResponse(content={"id": db_item.id, "name": db_item.name, "price": db_item.price},
                            status_code=status.HTTP_200_OK)
    return response


@router.get("/item", response_model=List[schemas.Item])
def read_items(offset: int = 0, limit: int = 10, min_price: float = None,
               max_price: float = None, show_deleted: bool = False, db: Session = Depends(get_session_local)):
    if offset < 0 or limit <= 0 or (min_price is not None and min_price < 0) or (
            max_price is not None and max_price <= 0):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, )
    items = crud.get_items(db=db, offset=offset, limit=limit, min_price=min_price,
                           max_price=max_price, show_deleted=show_deleted)
    return items


@router.put("/item/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_session_local)):
    db_item = crud.update_item(db=db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    response = JSONResponse(content={"id": db_item.id, "name": db_item.name, "price": db_item.price},
                            status_code=status.HTTP_200_OK)
    return response


@router.delete("/item/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_session_local)):
    db_item = crud.get_item_by_id(db=db, item_id=item_id)
    if db_item.deleted is True:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    else:
        del_item = crud.delete_item(db=db, item_id=item_id)
        return del_item


@router.patch("/item/{item_id}", response_model=schemas.EmptyItemData)
def update_item(item_id: int, data=Body(), db: Session = Depends(get_session_local)):
    db_item = crud.get_item_by_id(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if db_item.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Cannot modify 'deleted' field")

    if data is None and db_item.deleted is False:
        return JSONResponse(content={"id": db_item.id, "name": db_item.name, "price": db_item.price},
                            status_code=status.HTTP_200_OK)

    allowed_fields = set(["name", "price"])
    for field in data:
        if field not in allowed_fields:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Cannot add new field '{field}'")

    update_data = data
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    response = JSONResponse(content={"id": db_item.id, "name": db_item.name, "price": db_item.price},
                            status_code=status.HTTP_200_OK)
    return response


@router.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart_route(cart_id: int, item_id: int, db: Session = Depends(get_session_local)):
    if crud.get_cart_by_id(db=db, cart_id=cart_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if crud.get_item_by_id(db=db, item_id=item_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    cart = crud.add_item_to_cart(db, cart_id, item_id)
    crud.update_cart_price(db=db, cart_id=cart_id)
    return cart
