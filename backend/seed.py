from backend.database import SessionLocal, engine
from backend import models

def seed_data():
    db = SessionLocal()

    # Check if items already exist
    existing_items = db.query(models.Item).first()
    if existing_items:
        print("Seed skipped: data already exists.")
        db.close()
        return

    print("Seeding database...")

    # Create items
    milk = models.Item(
        name="milk",
        price=50,
        quantity=20,
        minimum_quantity=5
    )

    eggs = models.Item(
        name="eggs",
        price=6,
        quantity=10,
        minimum_quantity=4
    )

    bread = models.Item(
        name="bread",
        price=40,
        quantity=3,
        minimum_quantity=5  # low stock on purpose
    )

    db.add_all([milk, eggs, bread])
    db.commit()

    # Create sales
    sale1 = models.Sale(
        item_id=milk.id,
        item_name=milk.name,
        quantity_sold=2,
        price_at_sale=milk.price
    )

    sale2 = models.Sale(
        item_id=eggs.id,
        item_name=eggs.name,
        quantity_sold=1,
        price_at_sale=eggs.price
    )

    db.add_all([sale1, sale2])
    db.commit()

    db.close()
    print("Seed completed successfully.")


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    seed_data()