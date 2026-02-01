from sqlalchemy import Column, Integer, String, Float
from backend.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)
    quantity = Column(Integer)
    minimum_quantity = Column(Integer)


from sqlalchemy import DateTime
from datetime import datetime

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer)
    item_name = Column(String)
    quantity_sold = Column(Integer)
    price_at_sale = Column(Float)
    sold_at = Column(DateTime, default=datetime.utcnow)