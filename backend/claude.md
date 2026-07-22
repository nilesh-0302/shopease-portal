# ShopEase Customer Portal



## Project

ShopEase is an online store. This is the backend for our customer portal.

Customers use it to view orders, track deliveries, and raise support tickets.



## Tech Stack

- Python 3.11 with FastAPI

- Pydantic for data models

- Pytest for tests

- PostgreSQL as the database

- asyncpg as the async PostgreSQL driver

- SQLAlchemy 2.0 (async) for ORM



## Code Rules

- All functions must have docstrings

- Use snake\_case for everything

- Every route must return proper HTTP status codes (200, 201, 404, 400)

- Always validate input with Pydantic models

- Max 25 lines per function — split if longer

- All DB calls must be async (use async/await)



## ShopEase Brand Tone

When writing any customer-facing message (error messages, responses):

- Be friendly and helpful, never cold or technical

- Say "We couldn't find your order" not "404 Not Found"

- Say "Something went wrong on our end" not "Internal Server Error"



## Database Schema

### orders

| column     | type      | notes                          |
|------------|-----------|--------------------------------|
| id         | VARCHAR   | primary key e.g. ORD001        |
| customer   | VARCHAR   | customer email                 |
| items      | TEXT\[]    | array of item names            |
| status     | VARCHAR   | shipped/pending/delivered/cancelled |
| total      | INTEGER   | amount in paise e.g. 2499      |
| created\_at | TIMESTAMP | default now()                  |



### tickets

| column     | type      | notes                          |
|------------|-----------|--------------------------------|
| id         | VARCHAR   | primary key e.g. TKT001        |
| order\_id   | VARCHAR   | foreign key → orders.id        |
| issue      | TEXT      | customer description           |
| status     | VARCHAR   | open/in-progress/resolved      |
| created\_at | TIMESTAMP | default now()                  |



### tracking

| column     | type      | notes                          |
|------------|-----------|--------------------------------|
| order\_id   | VARCHAR   | foreign key → orders.id        |
| location   | VARCHAR   | current location               |
| updated\_at | TIMESTAMP | last update time               |
| eta        | DATE      | estimated delivery date        |



## File Structure

- Routes go in app/routes/

- Models go in app/models/schema.py

- SQLAlchemy table definitions in app/db/models.py

- DB session/engine in app/db/database.py

- Alembic migrations in alembic/versions/

- Environment variables in .env — never commit this file



## Testing

- Use pytest-asyncio for async test functions

- Use a separate test database: shopease\_test

- Always roll back transactions after each test

