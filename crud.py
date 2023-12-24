from sqlalchemy.orm import Session
import schemas
from models import ProductCategory, Product


def create_product_category(db: Session, category_data: schemas.ProductCategoryCreate):
    db_category = ProductCategory(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_product_categories(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ProductCategory).offset(skip).limit(limit).all()


def get_product_category(db: Session, category_id: int):
    return db.query(ProductCategory).filter_by(id=category_id).first()


def update_product_category(db: Session, category_id: int, category_data: schemas.ProductCategoryUpdate):
    db_category = db.query(ProductCategory).filter_by(id=category_id).first()

    if db_category:
        for key, value in category_data.dict().items():
            setattr(db_category, key, value)

        db.commit()
        db.refresh(db_category)
    return db_category


def delete_product_category(db: Session, category_id: int):
    db_category = db.query(ProductCategory).filter_by(id=category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


def create_product(db: Session, product_data: schemas.ProductCreate):
    db_product = Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Product).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter_by(id=product_id).first()


def update_product(db: Session, product_id: int, product_data: schemas.ProductUpdate):
    db_product = db.query(Product).filter_by(id=product_id).first()

    if db_product:
        for key, value in product_data.dict().items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter_by(id=product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False
