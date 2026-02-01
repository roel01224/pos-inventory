# POS Inventory Management System

A simple full-stack Point-of-Sale (POS) and Inventory Management System built with **FastAPI**, **SQLite**, and a **vanilla HTML/CSS/JavaScript frontend**.

This project supports item management, sales tracking, low-stock alerts, and includes automated backend tests using **pytest**.

---

## 🚀 Features

### Inventory Management
- Add new items with price, quantity, and minimum stock threshold
- Prevent duplicate item creation
- Restock existing items
- Automatically detect and flag **low stock** items
- Disable selling when item quantity reaches zero

### Sales Management
- Sell items with validation against available stock
- Record each sale in a **sales history table**
- Capture item name, quantity sold, price at sale, and timestamp
- Display sales history in the frontend

### Frontend UI
- Inventory table with real-time updates
- Inline quantity inputs for Sell and Restock
- Low-stock highlighting
- User-friendly error messages
- Local-time display for sales timestamps
- Mobile-friendly design considerations

### Backend
- REST API built with FastAPI
- Input validation using Pydantic
- SQLite database with SQLAlchemy ORM
- CORS enabled for frontend access

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (no framework)
- **Testing**: pytest, FastAPI TestClient

---

## 📁 Project Structure
pos-inventory/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── tests/
│       ├── conftest.py
│       └── test_items.py
├── frontend/
│   ├── index.html
│   └── app.js
└── README.md

---

## ⚙️ Setup Instructions

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

Backend will run at:
http://127.0.0.1:8000

2. Frontend Setup

Open the frontend using any static server.

Example using Python:
cd frontend
python -m http.server 5500

Frontend URL:
http://127.0.0.1:5500

🔌 API Endpoints

Items
Method
Endpoint
Description
POST
/items
Add new item
GET
/items
Get all items
PUT
/items/{item_name}/restock
Restock item


🧪 Testing Summary

Backend tests are implemented using pytest and FastAPI TestClient.

Test Coverage Includes:

Inventory Tests
	•	✅ Inventory starts empty
	•	✅ Successfully create a new item
	•	✅ Prevent duplicate item creation (409 Conflict)
	•	✅ Reject invalid inputs (negative price, quantity, minimum quantity)
	•	✅ Low-stock flag correctly triggered

Sales Tests
	•	✅ Successful sale reduces inventory quantity
	•	✅ Prevent selling more than available stock
	•	✅ Prevent selling zero or negative quantity
	•	✅ Sale record is created correctly
	•	✅ Multiple sales correctly recorded in history

Database & Isolation
	•	✅ In-memory SQLite used for tests
	•	✅ Tables created and dropped per test session
	•	✅ Test DB fully isolated from production DB

All tests pass successfully.

⸻

🧠 Key Learnings
	•	Dependency overrides in FastAPI for test isolation
	•	Proper handling of CORS for frontend-backend integration
	•	Managing edge cases in inventory systems
	•	Separating UI-safe identifiers from real backend values
	•	Converting UTC timestamps to local time on the frontend
	•	Writing meaningful automated tests for APIs

⸻

📌 Future Improvements
	•	Pagination for large inventories
	•	Authentication and user roles
	•	Editable item details
	•	Improved mobile UI styling
	•	Export sales reports

⸻

✅ Status

Project complete and fully tested.
---

### ✅ What to do now

1. Paste this into `README.md`
2. Save the file
3. Run:
```bash
git add README.md
git commit -m "Add project documentation"
git push
