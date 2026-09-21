# E-Commerce API

A robust RESTful API for managing a complete e-commerce platform backend. Built to handle product inventory, category mapping, order processing with automated stock deduction, and user reviews. 

## Features

* **Product & Category Management:** Full CRUD operations for product catalogs, including category filtering and strict URL slug generation.
* **Order Processing:** Secure checkout system that validates inventory, deducts stock upon order creation, and manages fulfillment states using strictly typed enum statuses (Pending, Paid, Shipped, Delivered, Cancelled).
* **Product Ratings:** Integrated review system allowing users to rate and describe their experience with specific products.
* **Authentication & Authorization:** Endpoint protection ensuring users can only modify their own data (e.g., preventing unauthorized status updates on other users' orders).
* **Isolated Testing Environment:** Comprehensive unit test coverage utilizing Pytest, with custom dependency overrides ensuring tests run against a clean, in-memory SQLite database without polluting production data.

## Tech Stack

* **Framework:** FastAPI
* **Data Validation:** Pydantic
* **ORM:** SQLAlchemy
* **Database:** SQLite (file-based for development, in-memory for testing)
* **Testing:** Pytest, HTTPX (FastAPI TestClient)

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sirnusi/apiecommerce.git](https://github.com/sirnusi/apiecommerce.git)
   cd apiecommerce

   python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt

Start the development server:

Bash
uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000. You can access the interactive Swagger documentation at http://127.0.0.1:8000/docs.
Testing
The project maintains a strict testing suite to guarantee data integrity. Tests are configured to automatically spin up isolated database sessions and mock user authentication.



Run the test suite with standard output to view detailed execution logs:

Bash
pytest -s
