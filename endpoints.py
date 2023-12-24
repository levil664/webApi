from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

import schemas
from database import get_db
from sqlalchemy.orm import Session
from crud import (
    create_product_category, get_product_categories, get_product_category,
    update_product_category, delete_product_category,
    create_product, get_products, get_product, update_product, delete_product
)

router_websocket = APIRouter()
router_product_categories = APIRouter(prefix='/categories', tags=['category'])
router_products = APIRouter(prefix='/products', tags=['product'])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def notify_clients(message: str):
    for connection in manager.active_connections:
        await connection.send_text(message)


@router_websocket.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    await manager.broadcast(f"Client #{client_id} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


@router_product_categories.post("/", response_model=schemas.ProductCategory)
async def create_product_category_route(product_category_data: schemas.ProductCategoryCreate,
                                        db: Session = Depends(get_db)):
    product_category = create_product_category(db, product_category_data)
    await notify_clients(f"Category added: {product_category.name}")
    return product_category


@router_product_categories.get("/", response_model=List[schemas.ProductCategory])
async def read_product_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    product_categories = get_product_categories(db, skip=skip, limit=limit)
    return product_categories


@router_product_categories.get("/{product_category_id}", response_model=schemas.ProductCategory)
async def read_category(product_category_id: int, db: Session = Depends(get_db)):
    product_category = get_product_category(db, product_category_id)
    return product_category


@router_product_categories.patch("/{product_category_id}", response_model=schemas.ProductCategory)
async def update_category_route(product_category_id: int, product_category_data: schemas.ProductCategoryUpdate,
                                db: Session = Depends(get_db)):
    updated_product_category = update_product_category(db, product_category_id, product_category_data)
    if updated_product_category:
        await notify_clients(f"Product category updated: {updated_product_category.name}")
        return updated_product_category
    return {"message": "Product category not found"}


@router_product_categories.delete("/{product_category_id}")
async def delete_category_route(product_category_id: int, db: Session = Depends(get_db)):
    deleted_product_category = delete_product_category(db, product_category_id)
    if deleted_product_category:
        await notify_clients(f"Product category deleted: ID {product_category_id}")
        return {"message": "Product category deleted"}
    return {"message": "Product category not found"}


@router_products.post("/", response_model=schemas.Product)
async def create_item_route(schema: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = create_product(db, schema)
    await notify_clients(f"Product added: {product.name}")
    return product


@router_products.get("/", response_model=List[schemas.Product])
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = get_products(db, skip=skip, limit=limit)
    return products


@router_products.get("/{product_id}", response_model=schemas.Product)
async def read_item(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    return product


@router_products.patch("/{product_id}")
async def update_item_route(product_id: int, schema: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated_product = update_product(db, product_id, schema)
    if updated_product:
        await notify_clients(f"Product updated: {updated_product.name}")
        return updated_product
    return {"message": "Product not found"}


@router_products.delete("/{product_id}")
async def delete_item_route(product_id: int, db: Session = Depends(get_db)):
    deleted_product = delete_product(db, product_id)
    if deleted_product:
        await notify_clients(f"Product deleted: ID {product_id}")
        return {"message": "Product deleted"}
    return {"message": "Product not found"}