from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import engine, SessionLocal
from backend import models
from pydantic import BaseModel, Field

app = FastAPI()

# ✅ CORS MUST be added immediately after app creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # explicit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)


# Pydantic schema (API input)
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    minimum_quantity: int = Field(..., ge=0)

class SaleCreate(BaseModel):
    item_name: str = Field(..., min_length=1)
    quantity_sold: int = Field(..., gt=0)

class RestockItem(BaseModel):
    quantity: int = Field(..., gt=0)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(item: ItemCreate, db: Session = Depends(get_db)):

    # Then check if item already exists
    item_name = item.name.strip().lower()

    existing_item = db.query(models.Item).filter(
        models.Item.name == item_name
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=409,
            detail=f"Item '{item_name}' already exists. Use PUT /items/{item_name}/restock to add stock."
    )

    db_item = models.Item(
        name=item_name,
        price=item.price,
        quantity=item.quantity,
        minimum_quantity=item.minimum_quantity
)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return {
        "message": "Item created successfully",
        "item": {
            "name": db_item.name,
            "price": db_item.price,
            "quantity": db_item.quantity,
            "minimum_quantity": db_item.minimum_quantity,
            "low_stock": db_item.quantity <= db_item.minimum_quantity
        }
    }


@app.put("/items/{item_name}/restock", status_code=status.HTTP_200_OK)
def restock_item(item_name: str, restock: RestockItem, db: Session = Depends(get_db)):
    """Add stock to an existing item"""

    normalized_name = item_name.strip().lower()

    item = db.query(models.Item).filter(
    models.Item.name == normalized_name 
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Item '{item_name}' not found"
        )

    item.quantity += restock.quantity
    db.commit()
    db.refresh(item)

    return {
        "message": f"Restocked {restock.quantity} units of {item.name}",
        "item": {
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "minimum_quantity": item.minimum_quantity,
            "low_stock": item.quantity <= item.minimum_quantity
        }
    }


@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(models.Item).all()

    result = []
    for item in items:
        result.append({
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "minimum_quantity": item.minimum_quantity,
            "low_stock": item.quantity <= item.minimum_quantity
        })

    return {
        "count": len(result),
        "items": result
    }


@app.post("/sales")
def sell_item(sale: SaleCreate, db: Session = Depends(get_db)):

    normalized_name = sale.item_name.strip().lower()
    
    item = db.query(models.Item).filter(
        models.Item.name == normalized_name
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    if sale.quantity_sold > item.quantity:
        raise HTTPException(
            status_code=409,
            detail=f"Not enough stock for '{item.name}'. Available quantity: {item.quantity}"
        )

    # Deduct stock
    item.quantity -= sale.quantity_sold

    # Create sale record
    sale_record = models.Sale(
        item_id=item.id,
        item_name=item.name,
        quantity_sold=sale.quantity_sold,
        price_at_sale=item.price
    )

    db.add(sale_record)
    db.commit()
    db.refresh(sale_record)

    return {
        "message": "Sale successful",
        "item": {
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "minimum_quantity": item.minimum_quantity,
            "low_stock": item.quantity <= item.minimum_quantity
        }
    }

@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    sales = db.query(models.Sale).all()

    return {
        "count": len(sales),
        "sales": [
            {
                "sale_id": sale.id,
                "item_name": sale.item_name,
                "quantity_sold": sale.quantity_sold,
                "price_at_sale": sale.price_at_sale,
                "sold_at": sale.sold_at
            }
            for sale in sales
        ]
    }